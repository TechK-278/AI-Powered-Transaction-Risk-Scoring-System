"""
Model evaluation routines for validation and test partitions.

Provides model assessment functions, probability generation,
and threshold optimization workflows.
"""

from typing import Any, Sequence

import numpy as np
import pandas as pd

from ml.src.training.metrics import (
    EvaluationMetrics,
    compute_classification_metrics,
    find_optimal_threshold,
    sweep_thresholds,
)


def evaluate_model(
    model: Any,
    X: pd.DataFrame | np.ndarray,
    y: pd.Series | np.ndarray,
    threshold: float = 0.5,
) -> tuple[EvaluationMetrics, np.ndarray]:
    """
    Generate predictions and calculate classification metrics for a dataset partition.

    Args:
        model: Trained classifier supporting predict_proba.
        X: Feature matrix.
        y: True target labels.
        threshold: Decision threshold for fraud classification (default: 0.5).

    Returns:
        tuple[EvaluationMetrics, np.ndarray]: Calculated metrics object and raw fraud probabilities array.
    """
    # Obtain fraud probabilities (Class = 1)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X)[:, 1]
    else:
        # Fallback for models outputting raw decision function
        probabilities = model.predict(X)

    metrics = compute_classification_metrics(y, probabilities, threshold=threshold)
    return metrics, probabilities


def generate_threshold_analysis(
    model: Any,
    X_val: pd.DataFrame | np.ndarray,
    y_val: pd.Series | np.ndarray,
    thresholds: Sequence[float] | None = None,
    criterion: str = "max_f1",
    min_precision: float = 0.0,
) -> tuple[pd.DataFrame, float, EvaluationMetrics]:
    """
    Perform threshold sweep on the validation set and select optimal threshold.

    Args:
        model: Trained classifier.
        X_val: Validation feature matrix.
        y_val: Validation target labels.
        thresholds: Spectrum of candidate thresholds to test.
        criterion: Optimal threshold selection strategy ('max_f1' or 'balanced_recall').
        min_precision: Optional minimum precision constraint.

    Returns:
        tuple containing:
        - pd.DataFrame: Full sweep table comparing precision, recall, F1 across thresholds.
        - float: Selected optimal threshold value.
        - EvaluationMetrics: Validation metrics evaluated at the selected threshold.
    """
    val_metrics_default, val_probs = evaluate_model(model, X_val, y_val, threshold=0.5)
    sweep_df = sweep_thresholds(y_val, val_probs, thresholds=thresholds)

    optimal_th, _ = find_optimal_threshold(
        sweep_df, criterion=criterion, min_precision=min_precision
    )
    optimal_val_metrics = compute_classification_metrics(y_val, val_probs, threshold=optimal_th)

    return sweep_df, optimal_th, optimal_val_metrics
