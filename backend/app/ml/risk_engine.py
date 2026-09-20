"""
Risk score engine module for transaction risk assessment.

Converts model fraud probabilities (P(Class=1) in [0.0, 1.0]) into deterministic
0–100 integer risk scores and maps them into Low, Medium, and High risk tiers.
"""

import math
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any


class RiskLabel(str, Enum):
    """Enumeration of standard risk tier categories."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass(frozen=True)
class RiskAssessment:
    """
    Immutable structured container for transaction risk evaluation results.

    Attributes:
        fraud_probability: Raw fraud probability P(Class=1) from ML model in [0.0, 1.0].
        risk_score: Normalized integer risk score in [0, 100].
        risk_label: Categorical risk tier ('Low', 'Medium', or 'High').
    """

    fraud_probability: float
    risk_score: int
    risk_label: str

    def to_dict(self) -> dict[str, Any]:
        """Convert risk assessment to serializable dictionary."""
        return asdict(self)


class RiskScoreEngine:
    """
    Deterministic risk scoring engine.

    Converts raw fraud probabilities into 0–100 integer risk scores and
    classifies transactions into modeled risk categories:
      - Low:    0 <= score <= 30 (Lower modeled fraud risk)
      - Medium: 31 <= score <= 70 (Moderate modeled fraud risk)
      - High:   71 <= score <= 100 (Higher modeled fraud risk)

    Note: Downstream transaction actions/policies are outside the scope of
    the risk score engine and are determined during later backend phases.
    """

    # Risk Tier Boundaries
    LOW_MAX: int = 30
    MEDIUM_MAX: int = 70
    HIGH_MAX: int = 100

    @staticmethod
    def validate_probability(fraud_probability: float) -> float:
        """
        Validate that the input is a valid, finite numeric probability in [0.0, 1.0].

        Args:
            fraud_probability: Fraud probability to validate.

        Returns:
            float: Validated float probability.

        Raises:
            TypeError: If input is not a float or integer (e.g. string, None, boolean).
            ValueError: If input is NaN, infinite, or outside [0.0, 1.0].
        """
        if isinstance(fraud_probability, bool) or not isinstance(
            fraud_probability, (int, float)
        ):
            raise TypeError(
                f"Fraud probability must be a numeric float or int. Got type: {type(fraud_probability).__name__}"
            )

        prob_float = float(fraud_probability)

        if math.isnan(prob_float):
            raise ValueError("Fraud probability cannot be NaN.")

        if math.isinf(prob_float):
            raise ValueError("Fraud probability cannot be infinite.")

        if prob_float < 0.0 or prob_float > 1.0:
            raise ValueError(
                f"Fraud probability must be within [0.0, 1.0]. Got: {prob_float}"
            )

        return prob_float

    def calculate_score(self, fraud_probability: float) -> int:
        """
        Convert a fraud probability in [0.0, 1.0] to a 0–100 integer risk score.

        Uses standard mathematical round-half-up rounding policy (e.g. 73.5 -> 74).

        Args:
            fraud_probability: Model-predicted probability of fraud P(Class=1).

        Returns:
            int: Integer risk score in [0, 100].
        """
        prob = self.validate_probability(fraud_probability)
        scaled = prob * 100.0

        # Standard deterministic round-half-up (e.g. 0.735 -> 73.5 -> 74)
        decimal_val = Decimal(str(scaled))
        score = int(decimal_val.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        # Defensive bounds clamping
        return max(0, min(100, score))

    def classify(self, risk_score: int) -> str:
        """
        Classify an integer risk score into a risk tier label.

        Boundaries:
          - 0 to 30:   'Low'
          - 31 to 70:  'Medium'
          - 71 to 100: 'High'

        Args:
            risk_score: Integer risk score in [0, 100].

        Returns:
            str: Risk tier label ('Low', 'Medium', or 'High').

        Raises:
            TypeError: If risk_score is not an integer.
            ValueError: If risk_score is outside [0, 100].
        """
        if isinstance(risk_score, bool) or not isinstance(risk_score, int):
            raise TypeError(
                f"Risk score must be an integer. Got type: {type(risk_score).__name__}"
            )

        if risk_score < 0 or risk_score > self.HIGH_MAX:
            raise ValueError(
                f"Risk score must be between 0 and 100. Got: {risk_score}"
            )

        if risk_score <= self.LOW_MAX:
            return RiskLabel.LOW.value
        elif risk_score <= self.MEDIUM_MAX:
            return RiskLabel.MEDIUM.value
        else:
            return RiskLabel.HIGH.value

    def assess(self, fraud_probability: float) -> RiskAssessment:
        """
        Generate a complete RiskAssessment from a raw model fraud probability.

        Args:
            fraud_probability: Model-predicted fraud probability in [0.0, 1.0].

        Returns:
            RiskAssessment: Structured evaluation container.
        """
        validated_prob = self.validate_probability(fraud_probability)
        score = self.calculate_score(validated_prob)
        label = self.classify(score)

        return RiskAssessment(
            fraud_probability=validated_prob,
            risk_score=score,
            risk_label=label,
        )
