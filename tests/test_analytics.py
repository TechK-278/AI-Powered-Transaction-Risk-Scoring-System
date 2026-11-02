"""
Tests for the transaction risk analytics summary (Phase 11).

Covers pure aggregation helpers, repository queries against an in-memory
SQLite database, and the GET /api/v1/analytics/summary endpoint with the
database dependency overridden.
"""

import unittest
from datetime import date, datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.transaction import Transaction
from app.services.analytics_service import (
    build_analytics_summary,
    build_daily_volume,
    build_risk_label_counts,
    build_score_distribution,
)

REFERENCE_TIME = datetime(2026, 11, 2, 15, 30, tzinfo=timezone.utc)


def create_in_memory_session_factory() -> sessionmaker:
    """Create a session factory bound to a fresh shared in-memory SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def make_transaction(risk_score: int, risk_label: str, created_at: datetime) -> Transaction:
    """Build a Transaction row with a fraud probability consistent with its score."""
    return Transaction(
        amount=50.0,
        time=100.0,
        fraud_probability=risk_score / 100,
        risk_score=risk_score,
        risk_label=risk_label,
        created_at=created_at,
    )


class TestAnalyticsAggregationHelpers(unittest.TestCase):
    """Unit tests for the pure aggregation functions."""

    def test_risk_label_counts_include_every_tier_in_order(self) -> None:
        counts = build_risk_label_counts({"High": 2, "low": 5})
        self.assertEqual(
            [(item.risk_label, item.count) for item in counts],
            [("Low", 5), ("Medium", 0), ("High", 2)],
        )

    def test_score_distribution_has_ten_buckets_and_includes_100_in_last(self) -> None:
        buckets = build_score_distribution({0: 1, 9: 2, 10: 3, 95: 4, 100: 5})
        self.assertEqual(len(buckets), 10)
        self.assertEqual((buckets[0].score_from, buckets[0].score_to, buckets[0].count), (0, 9, 3))
        self.assertEqual(buckets[1].count, 3)
        self.assertEqual((buckets[9].score_from, buckets[9].score_to, buckets[9].count), (90, 100, 9))

    def test_daily_volume_zero_fills_window_and_ignores_out_of_window_days(self) -> None:
        first_day = date(2026, 10, 31)
        evaluations = [
            (datetime(2026, 10, 31, 1, tzinfo=timezone.utc), "Low"),
            (datetime(2026, 11, 2, 9, tzinfo=timezone.utc), "High"),
            (datetime(2026, 11, 2, 10, tzinfo=timezone.utc), "High"),
            (datetime(2026, 10, 20, 10, tzinfo=timezone.utc), "High"),
        ]
        volume = build_daily_volume(evaluations, first_day, window_days=3)
        self.assertEqual([row.day for row in volume], [date(2026, 10, 31), date(2026, 11, 1), date(2026, 11, 2)])
        self.assertEqual((volume[0].low, volume[0].high), (1, 0))
        self.assertEqual((volume[1].low, volume[1].medium, volume[1].high), (0, 0, 0))
        self.assertEqual(volume[2].high, 2)

    def test_daily_volume_converts_offset_timestamps_to_utc_day(self) -> None:
        india_time = timezone(timedelta(hours=5, minutes=30))
        evaluations = [(datetime(2026, 11, 2, 2, 0, tzinfo=india_time), "Medium")]
        volume = build_daily_volume(evaluations, date(2026, 11, 1), window_days=2)
        self.assertEqual(volume[0].medium, 1)
        self.assertEqual(volume[1].medium, 0)


class TestAnalyticsSummaryService(unittest.TestCase):
    """Integration tests for build_analytics_summary against SQLite."""

    def setUp(self) -> None:
        self.db = create_in_memory_session_factory()()

    def tearDown(self) -> None:
        self.db.close()

    def test_empty_database_returns_zero_counts_and_null_averages(self) -> None:
        summary = build_analytics_summary(self.db, window_days=7, now=REFERENCE_TIME)
        self.assertEqual(summary.total_evaluations, 0)
        self.assertIsNone(summary.average_risk_score)
        self.assertIsNone(summary.average_fraud_probability)
        self.assertEqual(sum(item.count for item in summary.risk_label_counts), 0)
        self.assertEqual(len(summary.daily_volume), 7)
        self.assertEqual(summary.daily_volume[-1].day, date(2026, 11, 2))

    def test_summary_aggregates_persisted_evaluations(self) -> None:
        self.db.add_all(
            [
                make_transaction(10, "Low", REFERENCE_TIME - timedelta(hours=1)),
                make_transaction(50, "Medium", REFERENCE_TIME - timedelta(days=1)),
                make_transaction(90, "High", REFERENCE_TIME - timedelta(days=30)),
            ]
        )
        self.db.commit()

        summary = build_analytics_summary(self.db, window_days=7, now=REFERENCE_TIME)

        self.assertEqual(summary.total_evaluations, 3)
        self.assertAlmostEqual(summary.average_risk_score, 50.0)
        self.assertAlmostEqual(summary.average_fraud_probability, 0.5)
        self.assertEqual([item.count for item in summary.risk_label_counts], [1, 1, 1])
        self.assertEqual(summary.score_distribution[9].count, 1)
        self.assertEqual(summary.daily_volume[-1].low, 1)
        self.assertEqual(summary.daily_volume[-2].medium, 1)
        self.assertEqual(sum(row.high for row in summary.daily_volume), 0)


class TestAnalyticsSummaryEndpoint(unittest.TestCase):
    """API tests for GET /api/v1/analytics/summary."""

    def setUp(self) -> None:
        session_factory = create_in_memory_session_factory()
        seed_session = session_factory()
        seed_session.add(make_transaction(80, "High", datetime.now(timezone.utc)))
        seed_session.commit()
        seed_session.close()

        def override_get_db():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_summary_endpoint_returns_aggregates(self) -> None:
        response = self.client.get("/api/v1/analytics/summary", params={"window_days": 5})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_evaluations"], 1)
        self.assertEqual(body["window_days"], 5)
        self.assertEqual(len(body["daily_volume"]), 5)
        self.assertEqual(body["daily_volume"][-1]["high"], 1)
        self.assertEqual(len(body["score_distribution"]), 10)

    def test_summary_endpoint_rejects_out_of_range_window(self) -> None:
        self.assertEqual(self.client.get("/api/v1/analytics/summary", params={"window_days": 0}).status_code, 422)
        self.assertEqual(self.client.get("/api/v1/analytics/summary", params={"window_days": 91}).status_code, 422)


if __name__ == "__main__":
    unittest.main()
