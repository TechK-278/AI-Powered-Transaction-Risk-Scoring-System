"""
Online feature preprocessing module for real-time inference.

Adapts incoming transaction payloads into the exact feature representation
and deterministic column ordering expected by the trained XGBoost classifier.
"""

from typing import Any, Mapping
import numpy as np
import pandas as pd

from app.core.logging import logger
from app.ml.loader import ModelLoader


class OnlineFeaturePreprocessor:
    """
    Online preprocessor for transaction risk scoring requests.

    Applies the exact same feature engineering (cyclic temporal transformation,
    log-scaled amount, PCA preservation) as fitted during offline training.
    """

    def __init__(self, preprocessor: Any = None) -> None:
        """
        Initialize the online preprocessor.

        Args:
            preprocessor: Optional explicit preprocessor instance. If None, loaded via ModelLoader.
        """
        self._preprocessor = preprocessor

    @property
    def preprocessor(self) -> Any:
        """Get the active preprocessor instance."""
        if self._preprocessor is not None:
            return self._preprocessor
        return ModelLoader.get_preprocessor()

    def transform(self, transaction_features: Mapping[str, float]) -> np.ndarray:
        """
        Transform a single transaction feature mapping into a model-ready 2D numpy array.

        Args:
            transaction_features: Feature mapping containing keys ['Time', 'Amount', 'V1'..'V28'].

        Returns:
            np.ndarray: Transformed 2D feature matrix with shape (1, 31).

        Raises:
            ValueError: If transformation fails or yields invalid numerical values.
        """
        try:
            # Convert single transaction mapping to single-row DataFrame
            if isinstance(transaction_features, pd.DataFrame):
                df_input = transaction_features
            elif isinstance(transaction_features, dict):
                df_input = pd.DataFrame([transaction_features])
            else:
                df_input = pd.DataFrame([dict(transaction_features)])

            # Transform using the Scikit-learn preprocessor pipeline
            feature_matrix = self.preprocessor.transform(df_input)
        except Exception as exc:
            logger.exception("Online feature transformation failed: %s", exc)
            raise ValueError(f"Feature transformation failed: {exc}") from exc

        if not isinstance(feature_matrix, np.ndarray):
            feature_matrix = np.asarray(feature_matrix, dtype=np.float64)

        if feature_matrix.ndim == 1:
            feature_matrix = feature_matrix.reshape(1, -1)

        if feature_matrix.shape != (1, 31):
            raise ValueError(
                f"Expected feature shape (1, 31) for inference, got {feature_matrix.shape}"
            )

        if np.isnan(feature_matrix).any() or np.isinf(feature_matrix).any():
            raise ValueError("Preprocessed feature matrix contains NaN or infinite values.")

        return feature_matrix
