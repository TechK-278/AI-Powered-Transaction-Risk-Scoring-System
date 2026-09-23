"""
Pydantic schemas for transaction risk evaluation request and response.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class TransactionEvaluationRequest(BaseModel):
    """
    Schema for incoming transaction risk scoring request.

    Features correspond to the trained XGBoost model input schema:
      - amount: Transaction monetary value in currency units (e.g. Euros).
      - time: Elapsed seconds from reference start.
      - v1 through v28: Numerical PCA components.
    """

    amount: float = Field(
        ...,
        gt=0.0,
        description="Transaction monetary amount (must be strictly positive).",
        examples=[149.50],
    )
    time: float = Field(
        default=0.0,
        ge=0.0,
        description="Elapsed time in seconds from reference start.",
        examples=[3600.0],
    )

    # PCA feature components V1 through V28
    v1: float = Field(default=0.0, description="PCA component V1.", examples=[0.0])
    v2: float = Field(default=0.0, description="PCA component V2.", examples=[0.0])
    v3: float = Field(default=0.0, description="PCA component V3.", examples=[0.0])
    v4: float = Field(default=0.0, description="PCA component V4.", examples=[0.0])
    v5: float = Field(default=0.0, description="PCA component V5.", examples=[0.0])
    v6: float = Field(default=0.0, description="PCA component V6.", examples=[0.0])
    v7: float = Field(default=0.0, description="PCA component V7.", examples=[0.0])
    v8: float = Field(default=0.0, description="PCA component V8.", examples=[0.0])
    v9: float = Field(default=0.0, description="PCA component V9.", examples=[0.0])
    v10: float = Field(default=0.0, description="PCA component V10.", examples=[0.0])
    v11: float = Field(default=0.0, description="PCA component V11.", examples=[0.0])
    v12: float = Field(default=0.0, description="PCA component V12.", examples=[0.0])
    v13: float = Field(default=0.0, description="PCA component V13.", examples=[0.0])
    v14: float = Field(default=0.0, description="PCA component V14.", examples=[0.0])
    v15: float = Field(default=0.0, description="PCA component V15.", examples=[0.0])
    v16: float = Field(default=0.0, description="PCA component V16.", examples=[0.0])
    v17: float = Field(default=0.0, description="PCA component V17.", examples=[0.0])
    v18: float = Field(default=0.0, description="PCA component V18.", examples=[0.0])
    v19: float = Field(default=0.0, description="PCA component V19.", examples=[0.0])
    v20: float = Field(default=0.0, description="PCA component V20.", examples=[0.0])
    v21: float = Field(default=0.0, description="PCA component V21.", examples=[0.0])
    v22: float = Field(default=0.0, description="PCA component V22.", examples=[0.0])
    v23: float = Field(default=0.0, description="PCA component V23.", examples=[0.0])
    v24: float = Field(default=0.0, description="PCA component V24.", examples=[0.0])
    v25: float = Field(default=0.0, description="PCA component V25.", examples=[0.0])
    v26: float = Field(default=0.0, description="PCA component V26.", examples=[0.0])
    v27: float = Field(default=0.0, description="PCA component V27.", examples=[0.0])
    v28: float = Field(default=0.0, description="PCA component V28.", examples=[0.0])

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )

    def to_feature_dict(self) -> dict[str, float]:
        """
        Convert request payload into the exact dictionary schema expected by the preprocessor.

        Returns:
            dict[str, float]: Dictionary with keys ['Time', 'Amount', 'V1'..'V28'].
        """
        features: dict[str, float] = {
            "Time": float(self.time),
            "Amount": float(self.amount),
        }
        for i in range(1, 29):
            val = getattr(self, f"v{i}", 0.0)
            features[f"V{i}"] = float(val)

        return features


class TransactionEvaluationResponse(BaseModel):
    """
    Schema for transaction risk evaluation response.

    Represents modeled statistical fraud risk without imposing operational decisions.
    """

    fraud_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Estimated posterior probability of fraud P(Class=1) in [0.0, 1.0].",
        examples=[0.87],
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Deterministic integer risk score scaled from 0 to 100.",
        examples=[87],
    )
    risk_label: str = Field(
        ...,
        description="Modeled risk tier category: 'Low' (0-30), 'Medium' (31-70), or 'High' (71-100).",
        examples=["High"],
    )

    model_config = ConfigDict(frozen=True)
