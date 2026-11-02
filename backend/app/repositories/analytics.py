"""
Repository module for aggregate queries over persisted transaction evaluations.
"""

from datetime import datetime
from typing import NamedTuple, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class EvaluationTotals(NamedTuple):
    """Overall count and averages across all evaluations."""

    count: int
    average_risk_score: Optional[float]
    average_fraud_probability: Optional[float]


class AnalyticsRepository:
    """
    Read-only aggregate queries used by the analytics service.

    Aggregation happens in the database so the number of rows returned stays
    bounded (at most 101 score values and a handful of labels) regardless of
    how many evaluations are stored.
    """

    @staticmethod
    def get_totals(db: Session) -> EvaluationTotals:
        """Return the evaluation count and mean score/probability."""
        statement = select(
            func.count(Transaction.id),
            func.avg(Transaction.risk_score),
            func.avg(Transaction.fraud_probability),
        )
        count, average_score, average_probability = db.execute(statement).one()
        return EvaluationTotals(
            count=int(count or 0),
            average_risk_score=float(average_score) if average_score is not None else None,
            average_fraud_probability=float(average_probability) if average_probability is not None else None,
        )

    @staticmethod
    def count_by_risk_label(db: Session) -> dict[str, int]:
        """Return evaluation counts keyed by stored risk label."""
        statement = select(Transaction.risk_label, func.count(Transaction.id)).group_by(Transaction.risk_label)
        return {label: int(count) for label, count in db.execute(statement).all()}

    @staticmethod
    def count_by_risk_score(db: Session) -> dict[int, int]:
        """Return evaluation counts keyed by integer risk score (0-100)."""
        statement = select(Transaction.risk_score, func.count(Transaction.id)).group_by(Transaction.risk_score)
        return {int(score): int(count) for score, count in db.execute(statement).all()}

    @staticmethod
    def list_evaluations_since(db: Session, since: datetime) -> Sequence[tuple[datetime, str]]:
        """
        Return (created_at, risk_label) pairs for evaluations created at or after `since`.

        Only two narrow columns are selected; day bucketing is done by the caller
        in UTC so results do not depend on the database session time zone.
        """
        statement = select(Transaction.created_at, Transaction.risk_label).where(Transaction.created_at >= since)
        return [(created_at, risk_label) for created_at, risk_label in db.execute(statement).all()]
