"""
Unit and integration tests for FastAPI Transaction Evaluation & History API (Phases 08 & 09).

Validates ModelLoader, TransactionPredictor, transaction evaluation endpoint,
PostgreSQL persistence, history listing with pagination/filters, detail lookup,
and error/rollback behavior.
"""

import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.ml.loader import (
    ModelArtifactNotFoundError,
    ModelLoadError,
    ModelLoader,
)
from app.ml.predictor import TransactionPredictor
from app.ml.risk_engine import RiskLabel
from app.schemas.transaction import (
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
    """Test suite for FastAPI transactions evaluation and history router."""

    def setUp(self) -> None:
        """Initialize FastAPI TestClient."""
        self.client = TestClient(app)

    def test_evaluate_transaction_success_and_persistence(self) -> None:
        """Test POST /api/v1/transactions/evaluate persists transaction and returns 200 with ID."""
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
        self.assertIn("id", data)
        self.assertIsNotNone(data["id"])
        self.assertIn("fraud_probability", data)
        self.assertIn("risk_score", data)
        self.assertIn("risk_label", data)
        self.assertIn("created_at", data)

        self.assertIsInstance(data["fraud_probability"], float)
        self.assertTrue(0.0 <= data["fraud_probability"] <= 1.0)
        self.assertIsInstance(data["risk_score"], int)
        self.assertTrue(0 <= data["risk_score"] <= 100)
        self.assertIn(data["risk_label"], ["Low", "Medium", "High"])

        # Verify transaction can be fetched by the returned ID
        tx_id = data["id"]
        detail_res = self.client.get(f"/api/v1/transactions/{tx_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail_data = detail_res.json()
        self.assertEqual(detail_data["id"], tx_id)
        self.assertEqual(detail_data["amount"], 99.50)
        self.assertEqual(detail_data["risk_score"], data["risk_score"])

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

    def test_list_transactions_pagination(self) -> None:
        """Test GET /api/v1/transactions/ returns paginated response."""
        # Create at least one evaluation
        self.client.post(
            "/api/v1/transactions/evaluate",
            json={"amount": 42.0, "time": 10.0},
        )

        response = self.client.get("/api/v1/transactions/?page=1&page_size=5")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("page_size", data)
        self.assertIn("total_pages", data)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 5)
        self.assertIsInstance(data["items"], list)

    def test_list_transactions_filtering(self) -> None:
        """Test filtering by risk label and score range."""
        response = self.client.get("/api/v1/transactions/?risk_label=Low&min_risk_score=0&max_risk_score=30")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for item in data["items"]:
            self.assertEqual(item["risk_label"], "Low")
            self.assertTrue(0 <= item["risk_score"] <= 30)

    def test_list_transactions_invalid_filter_range_400(self) -> None:
        """Test that min_risk_score > max_risk_score returns 400 Bad Request."""
        response = self.client.get("/api/v1/transactions/?min_risk_score=80&max_risk_score=20")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("min_risk_score cannot be greater than max_risk_score", data["detail"])

    def test_get_transaction_by_id_404(self) -> None:
        """Test GET /api/v1/transactions/{id} with non-existent ID returns 404."""
        non_existent_id = str(uuid.uuid4())
        response = self.client.get(f"/api/v1/transactions/{non_existent_id}")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("not found", data["detail"])

    def test_evaluate_transaction_db_failure_rollback_500(self) -> None:
        """Test that database failure during persistence triggers rollback and returns 500."""
        with patch("app.api.transactions.TransactionRepository.create") as mock_create:
            mock_create.side_effect = SQLAlchemyError("Simulated DB connection error")
            payload = {"amount": 100.0, "time": 50.0}
            response = self.client.post("/api/v1/transactions/evaluate", json=payload)
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertIn("Database persistence error", data["detail"])

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
