"""
Transaction risk predictor service module.

Coordinates feature preprocessing, model inference, fraud probability extraction,
and risk assessment using the Phase 7 RiskScoreEngine.
"""

from typing import Any, Mapping, Optional
import numpy as np

from app.core.logging import logger
from app.ml.loader import ModelLoader
from app.ml.preprocessing import OnlineFeaturePreprocessor
from app.ml.risk_engine import RiskAssessment, RiskScoreEngine
from app.schemas.transaction import TransactionEvaluationRequest


class TransactionPredictor:
    """
    Inference service for real-time transaction risk scoring.

    Integrates online preprocessing, trained XGBoost model execution,
    and Phase 7 RiskScoreEngine evaluation.
    """

    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[OnlineFeaturePreprocessor] = None,
        risk_engine: Optional[RiskScoreEngine] = None,
    ) -> None:
        """
        Initialize the transaction predictor.

        Args:
            model: Optional explicit trained model instance.
            preprocessor: Optional explicit OnlineFeaturePreprocessor instance.
            risk_engine: Optional explicit RiskScoreEngine instance.
        """
        self._model = model
        self.preprocessor = preprocessor or OnlineFeaturePreprocessor()
        self.risk_engine = risk_engine or RiskScoreEngine()

    @property
    def model(self) -> Any:
        """Retrieve active model instance."""
        if self._model is not None:
            return self._model
        return ModelLoader.get_model()

    def predict(
        self,
        transaction_data: Any,
    ) -> RiskAssessment:
        """
        Execute end-to-end real-time risk prediction for a single transaction.

        Args:
            transaction_data: TransactionEvaluationRequest, Pydantic model, or feature mapping.

        Returns:
            RiskAssessment: Immutable assessment containing fraud_probability, risk_score, and risk_label.

        Raises:
            ValueError: If preprocessing or model prediction yields invalid numerical values.
        """
        # 1. Extract feature mapping
        if hasattr(transaction_data, "to_feature_dict"):
            feature_dict = transaction_data.to_feature_dict()
        elif isinstance(transaction_data, Mapping):
            # Normalize keys to canonical uppercase schema ('Time', 'Amount', 'V1'..'V28')
            feature_dict = {}
            for k, v in transaction_data.items():
                k_lower = str(k).lower()
                if k_lower == "amount":
                    feature_dict["Amount"] = float(v)
                elif k_lower == "time":
                    feature_dict["Time"] = float(v)
                elif k_lower.startswith("v") and k_lower[1:].isdigit():
                    feature_dict[f"V{k_lower[1:]}"] = float(v)
                else:
                    feature_dict[str(k)] = float(v)
            # Ensure any missing V1..V28 default to 0.0 if not supplied
            for i in range(1, 29):
                feature_dict.setdefault(f"V{i}", 0.0)
            feature_dict.setdefault("Time", 0.0)
        else:
            raise TypeError(
                f"Expected TransactionEvaluationRequest or Mapping, got {type(transaction_data).__name__}"
            )

        # 2. Online preprocessing
        feature_matrix = self.preprocessor.transform(feature_dict)

        # 3. Execute model inference
        try:
            raw_probs = self.model.predict_proba(feature_matrix)
        except Exception as exc:
            logger.exception("Model prediction failed: %s", exc)
            raise ValueError(f"Model prediction failed: {exc}") from exc

        # Extract P(Class=1)
        if hasattr(raw_probs, "ndim") and raw_probs.ndim == 2 and raw_probs.shape[1] >= 2:
            fraud_prob = float(raw_probs[0, 1])
        elif hasattr(raw_probs, "__iter__"):
            fraud_prob = float(raw_probs[0])
        else:
            fraud_prob = float(raw_probs)

        # 4. Pass through Phase 7 RiskScoreEngine (validates probability, computes 0-100 score, classifies label)
        assessment = self.risk_engine.assess(fraud_prob)

        logger.debug(
            "Transaction assessed: prob=%.4f, score=%d, label=%s",
            assessment.fraud_probability,
            assessment.risk_score,
            assessment.risk_label,
        )

        return assessment
