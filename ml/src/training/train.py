"""
Model training, serialization, and end-to-end training pipeline orchestrator.

Implements data ingestion, dynamic class-weight estimation, XGBoost model training,
validation threshold optimization, test evaluation, and model artifact persistence.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from ml.src.config import (
    DEFAULT_COLSAMPLE_BYTREE,
    DEFAULT_EVAL_METRIC,
    DEFAULT_LEARNING_RATE,
    DEFAULT_MAX_DEPTH,
    DEFAULT_MIN_CHILD_WEIGHT,
    DEFAULT_N_ESTIMATORS,
    DEFAULT_REG_ALPHA,
    DEFAULT_REG_LAMBDA,
    DEFAULT_SUBSAMPLE,
    FRAUD_MODEL_ARTIFACT_FILE,
    MODEL_METADATA_FILE,
    RANDOM_SEED,
    SAVED_MODELS_DIR,
    TARGET_COLUMN,
    TEST_DATA_FILE,
    TRAIN_DATA_FILE,
    VAL_DATA_FILE,
)
from ml.src.training.evaluate import evaluate_model, generate_threshold_analysis
from ml.src.training.metrics import EvaluationMetrics, calculate_class_weight


def load_processed_data(
    file_path: Path | str, target_col: str = TARGET_COLUMN
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Load a processed dataset and separate features and target.

    Args:
        file_path: Path to the processed CSV file.
        target_col: Name of the target column.

    Returns:
        tuple[pd.DataFrame, pd.Series]: (X_features, y_target).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If target_col is missing.
    """
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Processed data file not found at: {path}")

    df = pd.read_csv(path)
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in {path}")

    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols]
    y = df[target_col]
    return X, y


def build_xgb_model(
    scale_pos_weight: float | None = None,
    n_estimators: int = DEFAULT_N_ESTIMATORS,
    max_depth: int = DEFAULT_MAX_DEPTH,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    subsample: float = DEFAULT_SUBSAMPLE,
    colsample_bytree: float = DEFAULT_COLSAMPLE_BYTREE,
    min_child_weight: int = DEFAULT_MIN_CHILD_WEIGHT,
    reg_alpha: float = DEFAULT_REG_ALPHA,
    reg_lambda: float = DEFAULT_REG_LAMBDA,
    eval_metric: str = DEFAULT_EVAL_METRIC,
    random_state: int = RANDOM_SEED,
    **kwargs: Any,
) -> XGBClassifier:
    """
    Instantiate an explicitly configured XGBoost fraud classifier.

    Args:
        scale_pos_weight: Imbalance penalization ratio (negative_count / positive_count).
        n_estimators: Number of gradient boosted trees.
        max_depth: Maximum tree depth for base learners.
        learning_rate: Boosting learning rate (eta).
        subsample: Subsample ratio of training instances.
        colsample_bytree: Subsample ratio of columns when constructing each tree.
        min_child_weight: Minimum sum of instance weight (hessian) needed in a child.
        reg_alpha: L1 regularization term on weights.
        reg_lambda: L2 regularization term on weights.
        eval_metric: Evaluation metrics for validation data.
        random_state: Centralized random seed for deterministic tree construction.
        **kwargs: Additional parameters passed to XGBClassifier.

    Returns:
        XGBClassifier: Configured model instance.
    """
    model_params = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "learning_rate": learning_rate,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,
        "min_child_weight": min_child_weight,
        "reg_alpha": reg_alpha,
        "reg_lambda": reg_lambda,
        "eval_metric": eval_metric,
        "random_state": random_state,
        "n_jobs": -1,
        "tree_method": "hist",
    }
    if scale_pos_weight is not None:
        model_params["scale_pos_weight"] = float(scale_pos_weight)

    model_params.update(kwargs)
    return XGBClassifier(**model_params)


def train_model(
    X_train: pd.DataFrame | np.ndarray,
    y_train: pd.Series | np.ndarray,
    X_val: pd.DataFrame | np.ndarray | None = None,
    y_val: pd.Series | np.ndarray | None = None,
    scale_pos_weight: float | None = None,
    **model_kwargs: Any,
) -> XGBClassifier:
    """
    Train an XGBoost classifier with dynamic class imbalance weighting.

    Args:
        X_train: Training feature matrix.
        y_train: Training target labels.
        X_val: Optional validation feature matrix for early stopping monitoring.
        y_val: Optional validation target labels.
        scale_pos_weight: Optional class weight. If None, dynamically computed from y_train.
        **model_kwargs: Additional parameters passed to build_xgb_model.

    Returns:
        XGBClassifier: Fitted model instance.
    """
    if scale_pos_weight is None:
        scale_pos_weight = calculate_class_weight(y_train)

    model = build_xgb_model(scale_pos_weight=scale_pos_weight, **model_kwargs)

    fit_params: dict[str, Any] = {}
    if X_val is not None and y_val is not None:
        fit_params["eval_set"] = [(X_val, y_val)]
        fit_params["verbose"] = False

    model.fit(X_train, y_train, **fit_params)
    return model


def save_model(
    model: Any,
    output_path: Path | str = FRAUD_MODEL_ARTIFACT_FILE,
) -> Path:
    """
    Serialize a trained model object to disk using joblib.

    Args:
        model: Fitted model instance.
        output_path: Destination file path.

    Returns:
        Path: Absolute path to the saved artifact.
    """
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def load_model(
    model_path: Path | str = FRAUD_MODEL_ARTIFACT_FILE,
) -> Any:
    """
    Load a serialized model object from disk.

    Args:
        model_path: Path to the serialized artifact.

    Returns:
        Any: Deserialized model instance.

    Raises:
        FileNotFoundError: If the artifact file does not exist.
    """
    path = Path(model_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Model artifact not found at: {path}")

    return joblib.load(path)


def save_model_metadata(
    metadata: dict[str, Any],
    output_path: Path | str = MODEL_METADATA_FILE,
) -> Path:
    """
    Persist training metadata and metrics as structured JSON.

    Args:
        metadata: Dictionary containing training parameters and evaluation results.
        output_path: Destination JSON file path.

    Returns:
        Path: Path to written metadata file.
    """
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    return path


def run_training_pipeline(
    train_path: Path | str = TRAIN_DATA_FILE,
    val_path: Path | str = VAL_DATA_FILE,
    test_path: Path | str = TEST_DATA_FILE,
    model_artifact_path: Path | str = FRAUD_MODEL_ARTIFACT_FILE,
    metadata_artifact_path: Path | str = MODEL_METADATA_FILE,
    random_seed: int = RANDOM_SEED,
) -> dict[str, Any]:
    """
    Execute end-to-end model training, validation threshold selection, test evaluation, and artifact saving.

    Args:
        train_path: Path to train.csv.
        val_path: Path to validation.csv.
        test_path: Path to test.csv.
        model_artifact_path: Path to export fraud_model.joblib.
        metadata_artifact_path: Path to export model_metadata.json.
        random_seed: Random state for deterministic model training.

    Returns:
        dict[str, Any]: Comprehensive training and evaluation report dictionary.
    """
    # 1. Load Processed Partitions
    X_train, y_train = load_processed_data(train_path)
    X_val, y_val = load_processed_data(val_path)
    X_test, y_test = load_processed_data(test_path)

    # 2. Dynamic Class Weight
    class_weight = calculate_class_weight(y_train)

    # 3. Model Training
    model = train_model(
        X_train,
        y_train,
        X_val=X_val,
        y_val=y_val,
        scale_pos_weight=class_weight,
        random_state=random_seed,
    )

    # 4. Validation Threshold Optimization (Maximizing Validation F1)
    sweep_df, optimal_threshold, val_metrics_optimal = generate_threshold_analysis(
        model,
        X_val,
        y_val,
        criterion="max_f1",
    )
    val_metrics_default, _ = evaluate_model(model, X_val, y_val, threshold=0.5)

    # 5. Final Unbiased Evaluation on Test Partition
    test_metrics_optimal, _ = evaluate_model(
        model, X_test, y_test, threshold=optimal_threshold
    )
    test_metrics_default, _ = evaluate_model(
        model, X_test, y_test, threshold=0.5
    )

    # 6. Save Model Artifact
    saved_model_file = save_model(model, model_artifact_path)

    # 7. Construct & Save Metadata
    metadata: dict[str, Any] = {
        "model_type": "xgboost.XGBClassifier",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "random_seed": random_seed,
        "feature_count": int(X_train.shape[1]),
        "feature_names": list(X_train.columns),
        "dataset_splits": {
            "train_samples": int(len(X_train)),
            "train_legit": int((y_train == 0).sum()),
            "train_fraud": int((y_train == 1).sum()),
            "train_fraud_rate": float((y_train == 1).mean()),
            "val_samples": int(len(X_val)),
            "val_legit": int((y_val == 0).sum()),
            "val_fraud": int((y_val == 1).sum()),
            "val_fraud_rate": float((y_val == 1).mean()),
            "test_samples": int(len(X_test)),
            "test_legit": int((y_test == 0).sum()),
            "test_fraud": int((y_test == 1).sum()),
            "test_fraud_rate": float((y_test == 1).mean()),
        },
        "hyperparameters": {
            "n_estimators": DEFAULT_N_ESTIMATORS,
            "max_depth": DEFAULT_MAX_DEPTH,
            "learning_rate": DEFAULT_LEARNING_RATE,
            "subsample": DEFAULT_SUBSAMPLE,
            "colsample_bytree": DEFAULT_COLSAMPLE_BYTREE,
            "min_child_weight": DEFAULT_MIN_CHILD_WEIGHT,
            "reg_alpha": DEFAULT_REG_ALPHA,
            "reg_lambda": DEFAULT_REG_LAMBDA,
            "scale_pos_weight": class_weight,
            "eval_metric": DEFAULT_EVAL_METRIC,
            "tree_method": "hist",
        },
        "threshold_selection": {
            "criterion": "max_f1_on_validation",
            "selected_threshold": optimal_threshold,
            "default_threshold": 0.5,
        },
        "validation_metrics_optimal_threshold": val_metrics_optimal.to_dict(),
        "validation_metrics_default_threshold": val_metrics_default.to_dict(),
        "final_test_metrics_optimal_threshold": test_metrics_optimal.to_dict(),
        "final_test_metrics_default_threshold": test_metrics_default.to_dict(),
    }

    saved_metadata_file = save_model_metadata(metadata, metadata_artifact_path)

    # 8. Reload & Reproducibility Verification
    reloaded_model = load_model(saved_model_file)
    sample_X = X_test.head(100)
    orig_probs = model.predict_proba(sample_X)[:, 1]
    reloaded_probs = reloaded_model.predict_proba(sample_X)[:, 1]
    np.testing.assert_allclose(
        orig_probs,
        reloaded_probs,
        err_msg="Reloaded model probabilities differ from in-memory model.",
    )

    return {
        "metadata": metadata,
        "saved_model_file": str(saved_model_file),
        "saved_metadata_file": str(saved_metadata_file),
        "sweep_df": sweep_df,
        "optimal_threshold": optimal_threshold,
        "val_metrics": val_metrics_optimal,
        "test_metrics": test_metrics_optimal,
    }


if __name__ == "__main__":
    results = run_training_pipeline()
    tm = results["test_metrics"]
    print("=== Training Pipeline Run Successful ===")
    print(f"Optimal Threshold: {results['optimal_threshold']:.4f}")
    print(f"Test Accuracy:  {tm.accuracy:.5f}")
    print(f"Test Precision: {tm.precision:.5f}")
    print(f"Test Recall:    {tm.recall:.5f}")
    print(f"Test F1-Score:  {tm.f1_score:.5f}")
    print(f"Test ROC-AUC:   {tm.roc_auc:.5f}")
    print(f"Test PR-AUC:    {tm.pr_auc:.5f}")
    print(f"Confusion Matrix: TN={tm.true_negatives}, FP={tm.false_positives}, FN={tm.false_negatives}, TP={tm.true_positives}")
