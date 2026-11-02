"""
Service that assembles the transaction risk analytics summary.
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.ml.risk_engine import RiskLabel
from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    DailyEvaluationVolume,
    RiskLabelCount,
    RiskScoreBucket,
)

SCORE_BUCKET_WIDTH = 10
RISK_LABEL_ORDER = [RiskLabel.LOW.value, RiskLabel.MEDIUM.value, RiskLabel.HIGH.value]


def build_risk_label_counts(counts_by_label: dict[str, int]) -> list[RiskLabelCount]:
    """Return a count for every tier in Low/Medium/High order, matching labels case-insensitively."""
    normalized_counts: dict[str, int] = {}
    for label, count in counts_by_label.items():
        key = label.strip().capitalize()
        normalized_counts[key] = normalized_counts.get(key, 0) + count
    return [RiskLabelCount(risk_label=label, count=normalized_counts.get(label, 0)) for label in RISK_LABEL_ORDER]


def build_score_distribution(counts_by_score: dict[int, int]) -> list[RiskScoreBucket]:
    """Group per-score counts into ten ranges; the last range (90-100) includes 100."""
    bucket_counts = [0] * 10
    for score, count in counts_by_score.items():
        bucket_index = min(score // SCORE_BUCKET_WIDTH, 9)
        bucket_counts[bucket_index] += count
    return [
        RiskScoreBucket(
            score_from=index * SCORE_BUCKET_WIDTH,
            score_to=100 if index == 9 else index * SCORE_BUCKET_WIDTH + SCORE_BUCKET_WIDTH - 1,
            count=count,
        )
        for index, count in enumerate(bucket_counts)
    ]


def to_utc_day(timestamp: datetime) -> date:
    """Convert a stored timestamp to its UTC calendar day, treating naive values as UTC."""
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc).date()


def build_daily_volume(
    evaluations: list[tuple[datetime, str]],
    first_day: date,
    window_days: int,
) -> list[DailyEvaluationVolume]:
    """Count evaluations per UTC day and tier, emitting a row for every day in the window."""
    tier_counts = {first_day + timedelta(days=offset): {"low": 0, "medium": 0, "high": 0} for offset in range(window_days)}
    for created_at, risk_label in evaluations:
        day_counts = tier_counts.get(to_utc_day(created_at))
        tier_key = risk_label.strip().lower()
        if day_counts is not None and tier_key in day_counts:
            day_counts[tier_key] += 1
    return [DailyEvaluationVolume(day=day, **counts) for day, counts in tier_counts.items()]


def build_analytics_summary(
    db: Session,
    window_days: int,
    now: Optional[datetime] = None,
) -> AnalyticsSummaryResponse:
    """
    Assemble the analytics summary across all persisted evaluations.

    Args:
        db: Active SQLAlchemy database session.
        window_days: Number of most recent UTC days (including today) for daily volume.
        now: Reference time; defaults to the current UTC time (injectable for tests).

    Returns:
        AnalyticsSummaryResponse: Totals, tier counts, score distribution, and daily volume.
    """
    reference_time = now or datetime.now(timezone.utc)
    first_day = to_utc_day(reference_time) - timedelta(days=window_days - 1)
    window_start = datetime.combine(first_day, time.min, tzinfo=timezone.utc)

    totals = AnalyticsRepository.get_totals(db)
    return AnalyticsSummaryResponse(
        total_evaluations=totals.count,
        average_risk_score=totals.average_risk_score,
        average_fraud_probability=totals.average_fraud_probability,
        risk_label_counts=build_risk_label_counts(AnalyticsRepository.count_by_risk_label(db)),
        score_distribution=build_score_distribution(AnalyticsRepository.count_by_risk_score(db)),
        daily_volume=build_daily_volume(
            list(AnalyticsRepository.list_evaluations_since(db, window_start)),
            first_day,
            window_days,
        ),
        window_days=window_days,
    )
