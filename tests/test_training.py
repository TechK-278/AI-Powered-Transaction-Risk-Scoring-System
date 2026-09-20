"""
Unit and integration tests for Phase 06 Model Training & Evaluation.

Validates data loading, class weight calculation, model construction,
synthetic training, threshold sweep, metric computation, and model serialization.
Compatible with standard library unittest and pytest.
"""

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from ml.src.config import (
    DEFAULT_MAX_DEPTH,
    DEFAULT_N_ESTIMATORS,
    PCA_COLUMNS,
    RANDOM_SEED,
    TARGET_COLUMN,
)
from ml.src.training.evaluate import evaluate_model, generate_threshold_analysis
from ml.src.training.metrics import (
    EvaluationMetrics,
    calculate_class_weight,
    compute_classification_metrics,
    find_optimal_threshold,
    sweep_thresholds,
)
from ml.src.training.train import (
    build_xgb_model,
    load_model,
    load_processed_data,
    save_model,
    save_model_metadata,
    train_model,
)


class TestTrainingPipeline(unittest.TestCase):
    """Test suite for model training, evaluation, and serialization."""

    def setUp(self) -> None:
        """Create a synthetic dataset for testing."""
        np.random.seed(RANDOM_SEED)
        n_samples = 300
        feature_names = PCA_COLUMNS + ["hour_sin", "hour_cos", "amount_log"]

        data: dict[str, np.ndarray] = {}
        for col in feature_names:
            data[col] = np.random.normal(0, 1, n_samples)

        # 90% legit (0), 10% fraud (1)
        data[TARGET_COLUMN] = np.random.choice([0, 1], size=n_samples, p=[0.90, 0.10])
        self.sample_df = pd.DataFrame(data)
        self.feature_cols = feature_names
        self.X = self.sample_df[feature_names]
        self.y = self.sample_df[TARGET_COLUMN]

    def test_calculate_class_weight(self) -> None:
        """Test dynamic calculation of scale_pos_weight."""
        y = np.array([0, 0, 0, 0, 1])
        weight = calculate_class_weight(y)
        self.assertEqual(weight, 4.0)

    def test_calculate_class_weight_no_positives_raises(self) -> None:
        """Test that calculating weight with zero positives raises ValueError."""
        y = np.array([0, 0, 0])
        with self.assertRaises(ValueError):
            calculate_class_weight(y)

    def test_build_xgb_model_configuration(self) -> None:
        """Test XGBClassifier configuration and parameter assignment."""
        model = build_xgb_model(
            scale_pos_weight=10.0,
            n_estimators=50,
            max_depth=4,
            learning_rate=0.1,
        )
        self.assertIsInstance(model, XGBClassifier)
        self.assertEqual(model.n_estimators, 50)
        self.assertEqual(model.max_depth, 4)
        self.assertEqual(model.scale_pos_weight, 10.0)

    def test_compute_classification_metrics(self) -> None:
        """Test binary metric calculations against known inputs."""
        y_true = np.array([0, 0, 1, 1])
        y_prob = np.array([0.1, 0.4, 0.7, 0.9])

        metrics = compute_classification_metrics(y_true, y_prob, threshold=0.5)
        self.assertIsInstance(metrics, EvaluationMetrics)
        self.assertEqual(metrics.true_negatives, 2)
        self.assertEqual(metrics.false_positives, 0)
        self.assertEqual(metrics.false_negatives, 0)
        self.assertEqual(metrics.true_positives, 2)
        self.assertEqual(metrics.accuracy, 1.0)
        self.assertEqual(metrics.precision, 1.0)
        self.assertEqual(metrics.recall, 1.0)
        self.assertEqual(metrics.f1_score, 1.0)
        self.assertEqual(metrics.roc_auc, 1.0)
        self.assertEqual(metrics.pr_auc, 1.0)

    def test_sweep_thresholds_structure(self) -> None:
        """Test that threshold sweeping returns expected columns and row count."""
        y_true = np.array([0, 0, 0, 1, 1])
        y_prob = np.array([0.05, 0.2, 0.4, 0.6, 0.8])
        thresholds = [0.1, 0.5, 0.9]

        sweep_df = sweep_thresholds(y_true, y_prob, thresholds=thresholds)
        self.assertEqual(len(sweep_df), 3)
        expected_cols = {
            "threshold",
            "precision",
            "recall",
            "f1_score",
            "accuracy",
            "true_negatives",
            "false_positives",
            "false_negatives",
            "true_positives",
        }
        self.assertTrue(expected_cols.issubset(set(sweep_df.columns)))

    def test_find_optimal_threshold(self) -> None:
        """Test threshold selection under max_f1 criterion."""
        sweep_data = pd.DataFrame(
            {
                "threshold": [0.2, 0.5, 0.8],
                "precision": [0.5, 0.8, 1.0],
                "recall": [1.0, 0.8, 0.4],
                "f1_score": [0.67, 0.80, 0.57],
            }
        )
        opt_th, row = find_optimal_threshold(sweep_data, criterion="max_f1")
        self.assertEqual(opt_th, 0.5)
        self.assertEqual(row["f1_score"], 0.80)

    def test_train_model_synthetic_data(self) -> None:
        """Test model training and prediction output on synthetic dataset."""
        model = train_model(
            self.X,
            self.y,
            n_estimators=10,
            max_depth=3,
            scale_pos_weight=9.0,
            random_state=RANDOM_SEED,
        )
        self.assertIsInstance(model, XGBClassifier)

        metrics, probs = evaluate_model(model, self.X, self.y, threshold=0.5)
        self.assertEqual(len(probs), len(self.X))
        self.assertTrue((probs >= 0.0).all() and (probs <= 1.0).all())
        self.assertGreaterEqual(metrics.roc_auc, 0.5)

    def test_save_and_load_model_reproducibility(self) -> None:
        """Test that saved model artifact reproduces identical probabilities on reload."""
        model = train_model(
            self.X,
            self.y,
            n_estimators=10,
            max_depth=3,
            random_state=RANDOM_SEED,
        )
        orig_probs = model.predict_proba(self.X)[:, 1]

        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = Path(tmp_dir) / "test_fraud_model.joblib"
            save_model(model, model_path)

            loaded_model = load_model(model_path)
            loaded_probs = loaded_model.predict_proba(self.X)[:, 1]

            np.testing.assert_allclose(orig_probs, loaded_probs)

    def test_save_model_metadata_format(self) -> None:
        """Test that metadata JSON file is formatted properly."""
        dummy_meta = {
            "model_type": "xgboost.XGBClassifier",
            "test_f1": 0.85,
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            meta_path = Path(tmp_dir) / "metadata.json"
            save_model_metadata(dummy_meta, meta_path)

            with open(meta_path, "r", encoding="utf-8") as f:
                loaded_meta = json.load(f)

            self.assertEqual(loaded_meta["model_type"], "xgboost.XGBClassifier")
            self.assertEqual(loaded_meta["test_f1"], 0.85)


if __name__ == "__main__":
    unittest.main()
