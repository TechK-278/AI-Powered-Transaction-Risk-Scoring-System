"""
Unit and integration tests for Phase 05 Preprocessing & Feature Engineering.

Validates data validation, duplicate handling, stratified splitting,
transformer logic, data leakage prevention, serialization equality, and online single-record transformations.
Compatible with standard library unittest and pytest.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from ml.src.config import (
    AMOUNT_COLUMN,
    ENGINEERED_FEATURE_NAMES,
    PCA_COLUMNS,
    RANDOM_SEED,
    TARGET_COLUMN,
    TIME_COLUMN,
)
from ml.src.preprocessing.data_cleaning import (
    clean_dataset,
    split_dataset,
    validate_raw_data,
)
from ml.src.preprocessing.feature_engineering import TransactionFeatureTransformer
from ml.src.preprocessing.pipeline import (
    build_preprocessing_pipeline,
    load_preprocessor,
    save_preprocessor,
)


class TestPreprocessingPipeline(unittest.TestCase):
    """Test suite for data cleaning, splitting, transformation, and serialization."""

    def setUp(self) -> None:
        """Create a synthetic mini DataFrame matching the raw dataset schema."""
        np.random.seed(RANDOM_SEED)
        n_samples = 200
        data: dict[str, np.ndarray] = {
            TIME_COLUMN: np.random.uniform(0, 172800, n_samples),
        }
        for col in PCA_COLUMNS:
            data[col] = np.random.normal(0, 1, n_samples)

        data[AMOUNT_COLUMN] = np.random.exponential(50, n_samples)
        # 95% legit (0), 5% fraud (1)
        data[TARGET_COLUMN] = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
        self.sample_df = pd.DataFrame(data)

    def test_validate_raw_data_valid(self) -> None:
        """Test that valid schema passes validation without error."""
        validate_raw_data(self.sample_df)

    def test_validate_raw_data_missing_column(self) -> None:
        """Test that validation fails when an expected column is missing."""
        invalid_df = self.sample_df.drop(columns=["V10"])
        with self.assertRaises(ValueError):
            validate_raw_data(invalid_df)

    def test_validate_raw_data_invalid_target(self) -> None:
        """Test that validation fails when target is not binary (0, 1)."""
        invalid_df = self.sample_df.copy()
        invalid_df.loc[0, TARGET_COLUMN] = 99
        with self.assertRaises(ValueError):
            validate_raw_data(invalid_df)

    def test_clean_dataset_removes_duplicates(self) -> None:
        """Test that duplicate rows are detected and removed correctly."""
        df = pd.DataFrame(
            {
                TIME_COLUMN: [100.0, 100.0, 200.0],
                AMOUNT_COLUMN: [50.0, 50.0, 75.0],
                TARGET_COLUMN: [0, 0, 1],
            }
        )
        for col in PCA_COLUMNS:
            df[col] = 0.5

        cleaned_df, metrics = clean_dataset(df, drop_duplicates_flag=True)
        self.assertEqual(metrics["initial_rows"], 3)
        self.assertEqual(metrics["final_rows"], 2)
        self.assertEqual(metrics["total_duplicates"], 1)
        self.assertEqual(len(cleaned_df), 2)

    def test_stratified_split_preserves_class_distribution(self) -> None:
        """Test that 70/15/15 stratified split preserves minority fraud ratio."""
        cleaned_df, _ = clean_dataset(self.sample_df, drop_duplicates_flag=False)
        X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(
            cleaned_df,
            train_ratio=0.70,
            val_ratio=0.15,
            test_ratio=0.15,
            random_seed=RANDOM_SEED,
        )

        total_len = len(cleaned_df)
        self.assertEqual(len(X_train), int(total_len * 0.70))
        self.assertEqual(len(X_val) + len(X_test), total_len - len(X_train))

        # Check stratification: both classes present
        self.assertEqual(set(y_train.unique()), {0, 1})
        self.assertLess(abs(y_train.mean() - y_val.mean()), 0.05)
        self.assertLess(abs(y_train.mean() - y_test.mean()), 0.05)

    def test_feature_transformer_engineering(self) -> None:
        """Test temporal sin/cos and log1p amount transformations."""
        X = self.sample_df.drop(columns=[TARGET_COLUMN])
        transformer = TransactionFeatureTransformer(scale_amount=True)
        transformer.fit(X)

        output_matrix = transformer.transform(X)
        self.assertEqual(output_matrix.shape, (len(X), 31))

        df_out = transformer.transform_to_dataframe(X)
        self.assertEqual(list(df_out.columns), list(ENGINEERED_FEATURE_NAMES))

        # Sine and cosine features must be bounded in [-1.0, 1.0]
        self.assertTrue((df_out["hour_sin"] >= -1.0 - 1e-6).all())
        self.assertTrue((df_out["hour_sin"] <= 1.0 + 1e-6).all())
        self.assertTrue((df_out["hour_cos"] >= -1.0 - 1e-6).all())
        self.assertTrue((df_out["hour_cos"] <= 1.0 + 1e-6).all())

    def test_data_leakage_prevention(self) -> None:
        """
        Verify that fitting transformer on X_train does not use X_val or X_test information.
        """
        cleaned_df, _ = clean_dataset(self.sample_df, drop_duplicates_flag=False)
        X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(cleaned_df)

        train_amount_log = np.log1p(
            np.maximum(0, X_train[AMOUNT_COLUMN].values)
        ).reshape(-1, 1)
        expected_median = float(np.median(train_amount_log))

        transformer = TransactionFeatureTransformer(scale_amount=True)
        transformer.fit(X_train)

        self.assertIsNotNone(transformer.amount_scaler)
        self.assertTrue(
            np.isclose(transformer.amount_scaler.center_[0], expected_median)
        )

        val_transformed = transformer.transform(X_val)
        test_transformed = transformer.transform(X_test)

        self.assertEqual(val_transformed.shape, (len(X_val), 31))
        self.assertEqual(test_transformed.shape, (len(X_test), 31))

    def test_preprocessor_serialization_and_reproducibility(self) -> None:
        """Test saving and loading preprocessor joblib artifact preserves exact transform outputs."""
        X = self.sample_df.drop(columns=[TARGET_COLUMN])
        pipeline = build_preprocessing_pipeline(scale_amount=True)
        pipeline.fit(X)

        original_transformed = pipeline.transform(X)

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_file = Path(tmp_dir) / "test_preprocessor.joblib"
            save_preprocessor(pipeline, artifact_file)

            loaded_pipeline = load_preprocessor(artifact_file)
            loaded_transformed = loaded_pipeline.transform(X)

            np.testing.assert_allclose(original_transformed, loaded_transformed)

    def test_online_single_transaction_inference_dictionary(self) -> None:
        """Test transforming a single transaction dictionary for online inference."""
        raw_dict = {
            TIME_COLUMN: 7200.0,
            AMOUNT_COLUMN: 149.99,
        }
        for col in PCA_COLUMNS:
            raw_dict[col] = 0.123

        transformer = TransactionFeatureTransformer(scale_amount=True)
        mock_df = pd.DataFrame([raw_dict] * 10)
        transformer.fit(mock_df)

        # Single dictionary transform
        single_out = transformer.transform(raw_dict)
        self.assertEqual(single_out.shape, (1, 31))

        df_out = transformer.transform_to_dataframe(raw_dict)
        self.assertIsInstance(df_out, pd.DataFrame)
        self.assertEqual(len(df_out), 1)
        self.assertEqual(df_out.shape, (1, 31))


if __name__ == "__main__":
    unittest.main()
