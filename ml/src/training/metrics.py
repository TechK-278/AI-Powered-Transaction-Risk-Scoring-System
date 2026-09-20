"""
Evaluation metrics and threshold analysis module.

Provides structured metric containers, dynamic class-weight calculation,
imbalance-aware metric computation (PR-AUC, ROC-AUC, F1, Recall, Precision),
and threshold sweep utilities.
"""

from dataclasses import asdict, dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


@dataclass
class EvaluationMetrics:
    """Structured container for binary classification performance metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    pr_auc: float
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int
    threshold: float

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to serializable dictionary."""
        return asdict(self)


def calculate_class_weight(y_train: Sequence[int] | np.ndarray | pd.Series) -> float:
    """
    Calculate dynamic scale_pos_weight for XGBoost from training target labels.

    scale_pos_weight = total_negative_samples / total_positive_samples

    Args:
        y_train: Training labels series or array.

    Returns:
        float: Imbalance weighting ratio.

    Raises:
        ValueError: If no positive samples exist in y_train.
    """
    y_arr = np.asarray(y_train)
    positive_count = int(np.sum(y_arr == 1))
    negative_count = int(np.sum(y_arr == 0))

    if positive_count == 0:
        raise ValueError("Cannot calculate scale_pos_weight: training set contains 0 positive samples.")

    return float(negative_count / positive_count)


def compute_classification_metrics(
    y_true: Sequence[int] | np.ndarray | pd.Series,
    y_prob: Sequence[float] | np.ndarray | pd.Series,
    threshold: float = 0.5,
) -> EvaluationMetrics:
    """
    Compute comprehensive classification metrics for given probabilities and threshold.

    Args:
        y_true: True binary target labels (0 or 1).
        y_prob: Predicted fraud probabilities (values in [0.0, 1.0]).
        threshold: Decision threshold for positive classification (default: 0.5).

    Returns:
        EvaluationMetrics: Structured metrics container.
    """
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)
    y_pred_arr = (y_prob_arr >= threshold).astype(int)

    # Confusion matrix: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred_arr, labels=[0, 1]).ravel()

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

    # Continuous ranking metrics (independent of decision threshold)
    try:
        roc_auc = float(roc_auc_score(y_true_arr, y_prob_arr))
    except ValueError:
        roc_auc = 0.0

    try:
        pr_auc = float(average_precision_score(y_true_arr, y_prob_arr))
    except ValueError:
        pr_auc = 0.0

    return EvaluationMetrics(
        accuracy=acc,
        precision=prec,
        recall=rec,
        f1_score=f1,
        roc_auc=roc_auc,
        pr_auc=pr_auc,
        true_negatives=int(tn),
        false_positives=int(fp),
        false_negatives=int(fn),
        true_positives=int(tp),
        threshold=float(threshold),
    )


def sweep_thresholds(
    y_true: Sequence[int] | np.ndarray | pd.Series,
    y_prob: Sequence[float] | np.ndarray | pd.Series,
    thresholds: Sequence[float] | None = None,
) -> pd.DataFrame:
    """
    Evaluate precision, recall, F1, and confusion matrix across a spectrum of decision thresholds.

    Args:
        y_true: True binary target labels.
        y_prob: Predicted fraud probabilities.
        thresholds: List of thresholds to evaluate. If None, defaults to [0.05, 0.10, ..., 0.95].

    Returns:
        pd.DataFrame: Table comparing metrics across candidate thresholds.
    """
    if thresholds is None:
        thresholds = np.linspace(0.05, 0.95, 19)

    records: list[dict[str, Any]] = []
    for th in thresholds:
        metrics = compute_classification_metrics(y_true, y_prob, threshold=th)
        records.append(
            {
                "threshold": round(float(th), 4),
                "precision": metrics.precision,
                "recall": metrics.recall,
                "f1_score": metrics.f1_score,
                "accuracy": metrics.accuracy,
                "true_negatives": metrics.true_negatives,
                "false_positives": metrics.false_positives,
                "false_negatives": metrics.false_negatives,
                "true_positives": metrics.true_positives,
            }
        )

    return pd.DataFrame(records)


def find_optimal_threshold(
    threshold_df: pd.DataFrame,
    criterion: str = "max_f1",
    min_precision: float = 0.0,
) -> tuple[float, pd.Series]:
    """
    Select optimal decision threshold from a threshold sweep table based on explicit criterion.

    Supported criteria:
    - 'max_f1': Maximizes F1 score (harmonic mean of Precision and Recall).
    - 'balanced_recall': Maximizes Recall subject to precision >= min_precision.

    Args:
        threshold_df: DataFrame generated by sweep_thresholds.
        criterion: Selection criterion ('max_f1' or 'balanced_recall').
        min_precision: Minimum acceptable precision constraint.

    Returns:
        tuple[float, pd.Series]: Selected threshold and corresponding metric row.
    """
    if threshold_df.empty:
        raise ValueError("Cannot select threshold from empty DataFrame.")

    filtered_df = threshold_df[threshold_df["precision"] >= min_precision]
    if filtered_df.empty:
        filtered_df = threshold_df

    if criterion == "max_f1":
        best_idx = filtered_df["f1_score"].idxmax()
    elif criterion == "balanced_recall":
        best_idx = filtered_df["recall"].idxmax()
    else:
        raise ValueError(f"Unknown threshold selection criterion: {criterion}")

    best_row = filtered_df.loc[best_idx]
    return float(best_row["threshold"]), best_row
