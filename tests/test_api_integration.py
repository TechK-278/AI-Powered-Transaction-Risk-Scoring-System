"""
API integration tests that run without trained model artifacts (Phase 12).

The predictor is replaced by a stub returning a fixed RiskAssessment so the
evaluate → persist → list → detail → analytics flow can be verified in CI
against the in-memory SQLite database provided by conftest.py.
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import AppSettings, settings
from app.main import app
from app.ml.loader import ModelArtifactNotFoundError
from app.ml.risk_engine import RiskAssessment

EVALUATE_URL = "/api/v1/transactions/evaluate"
HIGH_RISK_ASSESSMENT = RiskAssessment(fraud_probability=0.912, risk_score=91, risk_label="High")
LOW_RISK_ASSESSMENT = RiskAssessment(fraud_probability=0.021, risk_score=2, risk_label="Low")


class TestEvaluationPersistenceFlow(unittest.TestCase):
    """End-to-end API flow with a stubbed predictor."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def evaluate_with_assessment(self, assessment: RiskAssessment, amount: float = 120.0) -> dict:
        with patch("app.api.transactions._predictor.predict", return_value=assessment):
            response = self.client.post(EVALUATE_URL, json={"amount": amount, "time": 3600.0})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_evaluation_is_persisted_and_retrievable_by_id(self) -> None:
        created = self.evaluate_with_assessment(HIGH_RISK_ASSESSMENT, amount=250.0)

        detail = self.client.get(f"/api/v1/transactions/{created['id']}")

        self.assertEqual(detail.status_code, 200)
        body = detail.json()
        self.assertEqual(body["amount"], 250.0)
        self.assertEqual(body["risk_score"], 91)
        self.assertEqual(body["risk_label"], "High")
        self.assertAlmostEqual(body["fraud_probability"], 0.912)

    def test_history_filters_by_label_and_score_range(self) -> None:
        self.evaluate_with_assessment(HIGH_RISK_ASSESSMENT)
        self.evaluate_with_assessment(LOW_RISK_ASSESSMENT)
        self.evaluate_with_assessment(LOW_RISK_ASSESSMENT)

        high_only = self.client.get("/api/v1/transactions/", params={"risk_label": "high"}).json()
        low_range = self.client.get("/api/v1/transactions/", params={"max_risk_score": 30}).json()

        self.assertEqual(high_only["total"], 1)
        self.assertEqual(high_only["items"][0]["risk_label"], "High")
        self.assertEqual(low_range["total"], 2)

    def test_history_pagination_metadata(self) -> None:
        for _ in range(3):
            self.evaluate_with_assessment(LOW_RISK_ASSESSMENT)

        second_page = self.client.get("/api/v1/transactions/", params={"page": 2, "page_size": 2}).json()

        self.assertEqual(second_page["total"], 3)
        self.assertEqual(second_page["total_pages"], 2)
        self.assertEqual(len(second_page["items"]), 1)

    def test_analytics_reflects_persisted_evaluations(self) -> None:
        self.evaluate_with_assessment(HIGH_RISK_ASSESSMENT)
        self.evaluate_with_assessment(LOW_RISK_ASSESSMENT)

        summary = self.client.get("/api/v1/analytics/summary").json()

        self.assertEqual(summary["total_evaluations"], 2)
        counts = {item["risk_label"]: item["count"] for item in summary["risk_label_counts"]}
        self.assertEqual(counts, {"Low": 1, "Medium": 0, "High": 1})
        self.assertEqual(summary["daily_volume"][-1]["high"], 1)

    def test_missing_model_artifacts_return_503_without_persisting(self) -> None:
        with patch("app.api.transactions._predictor.predict", side_effect=ModelArtifactNotFoundError("missing")):
            response = self.client.post(EVALUATE_URL, json={"amount": 10.0, "time": 0.0})

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("missing", response.json()["detail"])
        self.assertEqual(self.client.get("/api/v1/transactions/").json()["total"], 0)

    def test_unexpected_error_returns_generic_500(self) -> None:
        with patch("app.api.transactions._predictor.predict", side_effect=RuntimeError("C:\\secret\\path")):
            response = self.client.post(EVALUATE_URL, json={"amount": 10.0, "time": 0.0})

        self.assertEqual(response.status_code, 500)
        self.assertNotIn("secret", response.json()["detail"])


class TestCorsConfiguration(unittest.TestCase):
    """CORS middleware and origin list parsing."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_preflight_from_configured_origin_is_allowed(self) -> None:
        configured_origin = settings.cors_origin_list[0]
        response = self.client.options(
            EVALUATE_URL,
            headers={"Origin": configured_origin, "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), configured_origin)

    def test_unknown_origin_receives_no_cors_header(self) -> None:
        response = self.client.get("/api/v1/health/", headers={"Origin": "https://untrusted.example"})
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_cors_origin_list_ignores_blanks_and_whitespace(self) -> None:
        settings = AppSettings(cors_origins=" https://a.example , ,https://b.example ", database_url="sqlite://")
        self.assertEqual(settings.cors_origin_list, ["https://a.example", "https://b.example"])


if __name__ == "__main__":
    unittest.main()
