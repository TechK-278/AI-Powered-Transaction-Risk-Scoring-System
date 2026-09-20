"""
Training and evaluation package for the AI-Powered Transaction Risk Scoring System.
"""

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
    run_training_pipeline,
    save_model,
    save_model_metadata,
    train_model,
)

__all__ = [
    "EvaluationMetrics",
    "calculate_class_weight",
    "compute_classification_metrics",
    "sweep_thresholds",
    "find_optimal_threshold",
    "evaluate_model",
    "generate_threshold_analysis",
    "load_processed_data",
    "build_xgb_model",
    "train_model",
    "save_model",
    "load_model",
    "save_model_metadata",
    "run_training_pipeline",
]
