"""
Availability check for the trained model artifacts used by inference tests.

The artifacts are gitignored (they are produced by the ML training pipeline),
so tests that need them skip where they are absent, such as in CI.
"""

import unittest
from pathlib import Path

SAVED_MODELS_DIR = Path(__file__).resolve().parent.parent / "ml" / "saved_models"

MODEL_ARTIFACTS_AVAILABLE = all(
    (SAVED_MODELS_DIR / artifact_name).is_file()
    for artifact_name in ("fraud_model.joblib", "preprocessor.joblib")
)

requires_model_artifacts = unittest.skipUnless(
    MODEL_ARTIFACTS_AVAILABLE,
    "Trained model artifacts not found in ml/saved_models (run the training pipeline).",
)
