"""
Unit tests for Phase 07 Risk Score Engine.

Validates probability-to-score calculation, rounding behavior, risk tier boundaries,
strict monotonicity, invalid input rejections, and structured assessment outputs.
Compatible with standard library unittest and pytest.
"""

import math
import unittest

import numpy as np

from backend.app.ml.risk_engine import RiskAssessment, RiskLabel, RiskScoreEngine


class TestRiskScoreEngine(unittest.TestCase):
    """Test suite for RiskScoreEngine and RiskAssessment."""

    def setUp(self) -> None:
        """Initialize a fresh RiskScoreEngine instance."""
        self.engine = RiskScoreEngine()

    def test_zero_probability(self) -> None:
        """Test zero probability mapping to minimum score and Low risk."""
        assessment = self.engine.assess(0.0)
        self.assertEqual(assessment.fraud_probability, 0.0)
        self.assertEqual(assessment.risk_score, 0)
        self.assertEqual(assessment.risk_label, RiskLabel.LOW.value)

    def test_maximum_probability(self) -> None:
        """Test maximum probability (1.0) mapping to maximum score (100) and High risk."""
        assessment = self.engine.assess(1.0)
        self.assertEqual(assessment.fraud_probability, 1.0)
        self.assertEqual(assessment.risk_score, 100)
        self.assertEqual(assessment.risk_label, RiskLabel.HIGH.value)

    def test_low_risk_upper_boundary(self) -> None:
        """Test upper boundary of Low risk tier (0.30 -> 30 -> Low)."""
        assessment = self.engine.assess(0.30)
        self.assertEqual(assessment.risk_score, 30)
        self.assertEqual(assessment.risk_label, RiskLabel.LOW.value)

    def test_medium_risk_lower_boundary(self) -> None:
        """Test lower boundary of Medium risk tier (0.31 -> 31 -> Medium)."""
        assessment = self.engine.assess(0.31)
        self.assertEqual(assessment.risk_score, 31)
        self.assertEqual(assessment.risk_label, RiskLabel.MEDIUM.value)

    def test_medium_risk_upper_boundary(self) -> None:
        """Test upper boundary of Medium risk tier (0.70 -> 70 -> Medium)."""
        assessment = self.engine.assess(0.70)
        self.assertEqual(assessment.risk_score, 70)
        self.assertEqual(assessment.risk_label, RiskLabel.MEDIUM.value)

    def test_high_risk_lower_boundary(self) -> None:
        """Test lower boundary of High risk tier (0.71 -> 71 -> High)."""
        assessment = self.engine.assess(0.71)
        self.assertEqual(assessment.risk_score, 71)
        self.assertEqual(assessment.risk_label, RiskLabel.HIGH.value)

    def test_decimal_rounding_half_up(self) -> None:
        """Test standard half-up rounding on decimal probabilities."""
        test_cases = [
            (0.123, 12, RiskLabel.LOW.value),
            (0.125, 13, RiskLabel.LOW.value),
            (0.305, 31, RiskLabel.MEDIUM.value),
            (0.499, 50, RiskLabel.MEDIUM.value),
            (0.500, 50, RiskLabel.MEDIUM.value),
            (0.705, 71, RiskLabel.HIGH.value),
            (0.735, 74, RiskLabel.HIGH.value),
            (0.999, 100, RiskLabel.HIGH.value),
        ]
        for prob, expected_score, expected_label in test_cases:
            with self.subTest(prob=prob):
                assessment = self.engine.assess(prob)
                self.assertEqual(assessment.risk_score, expected_score)
                self.assertEqual(assessment.risk_label, expected_label)

    def test_strict_monotonicity(self) -> None:
        """Verify that risk score is strictly monotonically non-decreasing with respect to probability."""
        probabilities = np.linspace(0.0, 1.0, 1001)
        scores = [self.engine.calculate_score(float(p)) for p in probabilities]

        for i in range(len(scores) - 1):
            self.assertLessEqual(
                scores[i],
                scores[i + 1],
                f"Monotonicity violation between P={probabilities[i]} (score={scores[i]}) and P={probabilities[i+1]} (score={scores[i+1]})",
            )

    def test_invalid_negative_probability(self) -> None:
        """Test that negative probabilities raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.assess(-0.01)
        with self.assertRaises(ValueError):
            self.engine.assess(-1.0)

    def test_invalid_greater_than_one_probability(self) -> None:
        """Test that probabilities > 1.0 raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.assess(1.001)
        with self.assertRaises(ValueError):
            self.engine.assess(1.5)
        with self.assertRaises(ValueError):
            self.engine.assess(100.0)

    def test_invalid_nan_probability(self) -> None:
        """Test that NaN raises ValueError."""
        with self.assertRaises(ValueError):
            self.engine.assess(float("nan"))

    def test_invalid_infinite_probability(self) -> None:
        """Test that positive and negative infinity raise ValueError."""
        with self.assertRaises(ValueError):
            self.engine.assess(float("inf"))
        with self.assertRaises(ValueError):
            self.engine.assess(float("-inf"))

    def test_invalid_type_inputs(self) -> None:
        """Test that non-numeric types raise TypeError."""
        invalid_types = ["0.5", None, [0.5], {"prob": 0.5}, True, False]
        for val in invalid_types:
            with self.subTest(val=val):
                with self.assertRaises(TypeError):
                    self.engine.assess(val)  # type: ignore

    def test_classify_invalid_score_boundaries(self) -> None:
        """Test that classify rejects scores outside [0, 100] or non-int types."""
        with self.assertRaises(ValueError):
            self.engine.classify(-1)
        with self.assertRaises(ValueError):
            self.engine.classify(101)
        with self.assertRaises(TypeError):
            self.engine.classify(50.5)  # type: ignore
        with self.assertRaises(TypeError):
            self.engine.classify("50")  # type: ignore
        with self.assertRaises(TypeError):
            self.engine.classify(True)  # type: ignore

    def test_risk_assessment_dataclass_structure_and_serialization(self) -> None:
        """Test that RiskAssessment is immutable and serializes properly to dictionary."""
        assessment = self.engine.assess(0.735)
        self.assertIsInstance(assessment, RiskAssessment)
        self.assertEqual(assessment.fraud_probability, 0.735)
        self.assertEqual(assessment.risk_score, 74)
        self.assertEqual(assessment.risk_label, "High")

        # Verify to_dict() output
        d = assessment.to_dict()
        self.assertEqual(
            d,
            {
                "fraud_probability": 0.735,
                "risk_score": 74,
                "risk_label": "High",
            },
        )


if __name__ == "__main__":
    unittest.main()
