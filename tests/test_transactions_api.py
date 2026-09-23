"""
Unit and integration tests for Phase 08 FastAPI Backend Expansion.

Validates ModelLoader singleton caching, TransactionPredictor service,
POST /api/v1/transactions/evaluate endpoint, request validation,
and health endpoint regression. Compatible with standard library unittest and pytest.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml.loader import (
    ModelArtifactNotFoundError,
    ModelLoadError,
    ModelLoader,
)
from backend.app.ml.predictor import TransactionPredictor
from backend.app.ml.preprocessing import OnlineFeaturePreprocessor
from backend.app.ml.risk_engine import RiskLabel
from backend.app.schemas.transaction import (
    TransactionEvaluationRequest,
    TransactionEvaluationResponse,
)


class TestModelLoader(unittest.TestCase):
    """Test suite for ModelLoader artifact management."""

    def tearDown(self) -> None:
        """Reset loader singleton state after each test."""
        ModelLoader.reset()

    def test_load_existing_artifacts(self) -> None:
        """Test loading local model and preprocessor artifacts."""
        model = ModelLoader.get_model()
        preprocessor = ModelLoader.get_preprocessor()

        self.assertIsNotNone(model)
        self.assertIsNotNone(preprocessor)
        self.assertTrue(ModelLoader.is_loaded())

    def test_singleton_caching_does_not_reload(self) -> None:
        """Test that repeated calls return the identical cached instance without re-reading disk."""
        model1 = ModelLoader.get_model()
        model2 = ModelLoader.get_model()
        self.assertIs(model1, model2)

        prep1 = ModelLoader.get_preprocessor()
        prep2 = ModelLoader.get_preprocessor()
        self.assertIs(prep1, prep2)

    def test_missing_model_artifact_raises_custom_exception(self) -> None:
        """Test that missing model file raises ModelArtifactNotFoundError."""
        ModelLoader.reset()
        non_existent_path = Path(tempfile.gettempdir()) / "non_existent_fraud_model.joblib"
        with self.assertRaises(ModelArtifactNotFoundError):
            ModelLoader.load_model(non_existent_path)

    def test_missing_preprocessor_artifact_raises_custom_exception(self) -> None:
        """Test that missing preprocessor file raises ModelArtifactNotFoundError."""
        ModelLoader.reset()
        non_existent_path = Path(tempfile.gettempdir()) / "non_existent_preprocessor.joblib"
        with self.assertRaises(ModelArtifactNotFoundError):
            ModelLoader.load_preprocessor(non_existent_path)


class TestTransactionPredictor(unittest.TestCase):
    """Test suite for TransactionPredictor inference service."""

    def setUp(self) -> None:
        """Initialize predictor."""
        self.predictor = TransactionPredictor()

    def test_predict_valid_request_model(self) -> None:
        """Test end-to-end prediction from TransactionEvaluationRequest."""
        request = TransactionEvaluationRequest(
            amount=149.99,
            time=7200.0,
            v1=0.1,
            v2=-0.2,
            v3=0.3,
            v4=0.4,
            v14=-1.5,
            v17=-2.0,
        )
        assessment = self.predictor.predict(request)

        self.assertIsInstance(assessment.fraud_probability, float)
        self.assertGreaterEqual(assessment.fraud_probability, 0.0)
        self.assertLessEqual(assessment.fraud_probability, 1.0)

        self.assertIsInstance(assessment.risk_score, int)
        self.assertGreaterEqual(assessment.risk_score, 0)
        self.assertLessEqual(assessment.risk_score, 100)

        self.assertIn(assessment.risk_label, [RiskLabel.LOW.value, RiskLabel.MEDIUM.value, RiskLabel.HIGH.value])

    def test_predict_with_mock_model_probability(self) -> None:
        """Test prediction mapping using a mock model with known probability output."""
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = np.array([[0.265, 0.735]])

        predictor = TransactionPredictor(model=mock_model)
        request = TransactionEvaluationRequest(amount=50.0, time=100.0)

        assessment = predictor.predict(request)
        self.assertEqual(assessment.fraud_probability, 0.735)
        self.assertEqual(assessment.risk_score, 74)
        self.assertEqual(assessment.risk_label, RiskLabel.HIGH.value)


class TestTransactionsAPI(unittest.TestCase):
    """Test suite for FastAPI transactions evaluation router."""

    def setUp(self) -> None:
        """Initialize FastAPI TestClient."""
        self.client = TestClient(app)

    def test_evaluate_transaction_success_200(self) -> None:
        """Test POST /api/v1/transactions/evaluate with valid payload returns 200 and valid schema."""
        payload = {
            "amount": 99.50,
            "time": 3600.0,
            "v1": 0.5,
            "v2": -0.3,
            "v14": -0.8,
            "v17": -1.2,
        }
        response = self.client.post("/api/v1/transactions/evaluate", json=payload)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("fraud_probability", data)
        self.assertIn("risk_score", data)
        self.assertIn("risk_label", data)

        self.assertIsInstance(data["fraud_probability"], float)
        self.assertTrue(0.0 <= data["fraud_probability"] <= 1.0)
        self.assertIsInstance(data["risk_score"], int)
        self.assertTrue(0 <= data["risk_score"] <= 100)
        self.assertIn(data["risk_label"], ["Low", "Medium", "High"])

    def test_evaluate_transaction_validation_negative_amount_422(self) -> None:
        """Test that negative amount payload is rejected with 422 Unprocessable Entity."""
        payload = {
            "amount": -25.0,
            "time": 100.0,
        }
        response = self.client.post("/api/v1/transactions/evaluate", json=payload)
        self.assertEqual(response.status_code, 422)
        errors = response.json()
        self.assertIn("detail", errors)

    def test_evaluate_transaction_validation_zero_amount_422(self) -> None:
        """Test that zero amount payload is rejected (must be gt=0)."""
        payload = {
            "amount": 0.0,
            "time": 100.0,
        }
        response = self.client.post("/api/v1/transactions/evaluate", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_evaluate_transaction_validation_non_numeric_amount_422(self) -> None:
        """Test that non-numeric amount string is rejected with 422."""
        payload = {
            "amount": "invalid_amount",
            "time": 100.0,
        }
        response = self.client.post("/api/v1/transactions/evaluate", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_evaluate_transaction_validation_missing_amount_422(self) -> None:
        """Test that payload missing required 'amount' field is rejected with 422."""
        payload = {
            "time": 100.0,
            "v1": 0.5,
        }
        response = self.client.post("/api/v1/transactions/evaluate", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_health_check_regression_200(self) -> None:
        """Test that GET /api/v1/health/ continues to return 200 healthy status."""
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("service", data)
        self.assertIn("version", data)


if __name__ == "__main__":
    unittest.main()
