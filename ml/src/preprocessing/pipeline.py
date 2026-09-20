"""
Pipeline construction, serialization, and end-to-end execution orchestrator.

Integrates data cleaning, stratified splitting, feature transformation,
and joblib artifact persistence for offline training and online serving.
"""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from ml.src.config import (
    PREPROCESSOR_ARTIFACT_FILE,
    PROCESSED_DATA_DIR,
    RANDOM_SEED,
    RAW_DATA_FILE,
    SAVED_MODELS_DIR,
    TARGET_COLUMN,
    TEST_DATA_FILE,
    TRAIN_DATA_FILE,
    VAL_DATA_FILE,
)
from ml.src.preprocessing.data_cleaning import (
    clean_dataset,
    load_raw_data,
    split_dataset,
)
from ml.src.preprocessing.feature_engineering import TransactionFeatureTransformer


def build_preprocessing_pipeline(scale_amount: bool = True) -> Pipeline:
    """
    Construct a Scikit-learn Pipeline encapsulating feature engineering and scaling.

    Args:
        scale_amount: Whether to apply RobustScaler on amount.

    Returns:
        Pipeline: Sklearn Pipeline ready to fit on training data.
    """
    return Pipeline(
        steps=[
            (
                "feature_transformer",
                TransactionFeatureTransformer(scale_amount=scale_amount),
            )
        ]
    )


def save_preprocessor(
    preprocessor: Any,
    output_path: Path | str = PREPROCESSOR_ARTIFACT_FILE,
) -> Path:
    """
    Serialize a fitted preprocessor object to disk using joblib.

    Args:
        preprocessor: Fitted preprocessor / Pipeline instance.
        output_path: Destination file path.

    Returns:
        Path: Absolute path to the saved artifact.
    """
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, path)
    return path


def load_preprocessor(
    model_path: Path | str = PREPROCESSOR_ARTIFACT_FILE,
) -> Any:
    """
    Load a serialized preprocessor object from disk.

    Args:
        model_path: Path to the serialized artifact.

    Returns:
        Any: Deserialized preprocessor / Pipeline instance.

    Raises:
        FileNotFoundError: If the artifact file does not exist.
    """
    path = Path(model_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Preprocessor artifact not found at: {path}")

    return joblib.load(path)


def run_preprocessing_pipeline(
    raw_data_path: Path | str = RAW_DATA_FILE,
    processed_dir: Path | str = PROCESSED_DATA_DIR,
    artifact_path: Path | str = PREPROCESSOR_ARTIFACT_FILE,
    random_seed: int = RANDOM_SEED,
) -> dict[str, Any]:
    """
    Execute the complete end-to-end preprocessing workflow:
    1. Load and validate raw transaction dataset.
    2. Clean dataset and resolve duplicates.
    3. Perform stratified 70/15/15 train/val/test split.
    4. Fit preprocessing pipeline strictly on training split.
    5. Transform train, validation, and test sets.
    6. Persist processed CSV datasets and serialized preprocessor.joblib artifact.
    7. Perform reproducibility verification against reload.

    Args:
        raw_data_path: Path to raw dataset CSV.
        processed_dir: Directory to save processed train/val/test CSVs.
        artifact_path: File path to save the preprocessor artifact.
        random_seed: Random seed for splitting.

    Returns:
        dict[str, Any]: Comprehensive pipeline run execution statistics.
    """
    processed_path = Path(processed_dir).resolve()
    processed_path.mkdir(parents=True, exist_ok=True)

    # 1. Load raw data
    raw_df = load_raw_data(raw_data_path)

    # 2. Clean data
    cleaned_df, cleaning_metrics = clean_dataset(raw_df, drop_duplicates_flag=True)

    # 3. Stratified split (70% Train, 15% Val, 15% Test)
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(
        cleaned_df,
        target_col=TARGET_COLUMN,
        random_seed=random_seed,
    )

    # 4. Build and fit pipeline strictly on X_train (Leakage Prevention)
    pipeline = build_preprocessing_pipeline(scale_amount=True)
    pipeline.fit(X_train)

    # Extract transformer for DataFrame formatting
    transformer: TransactionFeatureTransformer = pipeline.named_steps["feature_transformer"]

    # 5. Transform partitions
    X_train_transformed = transformer.transform_to_dataframe(X_train)
    X_val_transformed = transformer.transform_to_dataframe(X_val)
    X_test_transformed = transformer.transform_to_dataframe(X_test)

    # Attach targets to create self-contained processed datasets
    train_df = X_train_transformed.copy()
    train_df[TARGET_COLUMN] = y_train.values

    val_df = X_val_transformed.copy()
    val_df[TARGET_COLUMN] = y_val.values

    test_df = X_test_transformed.copy()
    test_df[TARGET_COLUMN] = y_test.values

    # 6. Save processed datasets
    train_file = processed_path / "train.csv"
    val_file = processed_path / "validation.csv"
    test_file = processed_path / "test.csv"

    train_df.to_csv(train_file, index=False)
    val_df.to_csv(val_file, index=False)
    test_df.to_csv(test_file, index=False)

    # 7. Save serialized preprocessor
    saved_artifact_path = save_preprocessor(pipeline, artifact_path)

    # 8. Reload and verify equality
    reloaded_pipeline = load_preprocessor(saved_artifact_path)
    sample_test_features = X_test.head(100)
    original_output = pipeline.transform(sample_test_features)
    reloaded_output = reloaded_pipeline.transform(sample_test_features)
    np.testing.assert_allclose(
        original_output,
        reloaded_output,
        err_msg="Reloaded preprocessor output differs from original fitted preprocessor.",
    )

    # Summary statistics
    pipeline_stats: dict[str, Any] = {
        "cleaning_metrics": cleaning_metrics,
        "train_shape": train_df.shape,
        "val_shape": val_df.shape,
        "test_shape": test_df.shape,
        "train_fraud_count": int((train_df[TARGET_COLUMN] == 1).sum()),
        "train_fraud_rate": float((train_df[TARGET_COLUMN] == 1).mean()),
        "val_fraud_count": int((val_df[TARGET_COLUMN] == 1).sum()),
        "val_fraud_rate": float((val_df[TARGET_COLUMN] == 1).mean()),
        "test_fraud_count": int((test_df[TARGET_COLUMN] == 1).sum()),
        "test_fraud_rate": float((test_df[TARGET_COLUMN] == 1).mean()),
        "saved_train_file": str(train_file),
        "saved_val_file": str(val_file),
        "saved_test_file": str(test_file),
        "saved_artifact_file": str(saved_artifact_path),
        "feature_count": len(transformer.get_feature_names_out()),
        "feature_names": transformer.get_feature_names_out(),
    }

    return pipeline_stats


if __name__ == "__main__":
    stats = run_preprocessing_pipeline()
    print("=== Preprocessing Pipeline Run Successful ===")
    print(f"Train Shape: {stats['train_shape']}, Fraud: {stats['train_fraud_count']} ({stats['train_fraud_rate']:.5%})")
    print(f"Val Shape:   {stats['val_shape']}, Fraud: {stats['val_fraud_count']} ({stats['val_fraud_rate']:.5%})")
    print(f"Test Shape:  {stats['test_shape']}, Fraud: {stats['test_fraud_count']} ({stats['test_fraud_rate']:.5%})")
    print(f"Artifact:    {stats['saved_artifact_file']}")
