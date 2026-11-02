"""
SQLAlchemy 2.0 ORM model for transaction risk assessments.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Transaction(Base):
    """
    SQLAlchemy model representing an evaluated transaction and its risk assessment.

    Persists input monetary parameters, temporal metadata, calculated fraud probability,
    and resulting risk tier assessment.
    """

    __tablename__ = "transactions"

    # Primary key: UUID string representation
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Unique identifier for the transaction record.",
    )

    # Input monetary amount
    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Transaction monetary amount.",
    )

    # Temporal metadata (seconds from reference timestamp)
    time: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="Elapsed time in seconds from reference start.",
    )

    # Model evaluation output
    fraud_probability: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Estimated posterior probability of fraud P(Class=1) in [0.0, 1.0].",
    )

    # Risk score output (0 - 100)
    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Scaled integer risk score from 0 to 100.",
    )

    # Risk label category: Low, Medium, High
    risk_label: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        doc="Risk tier category (Low, Medium, High).",
    )

    # Record creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        index=True,
        doc="Timestamp when the transaction risk evaluation was persisted.",
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_transactions_amount_positive"),
        CheckConstraint("time >= 0", name="chk_transactions_time_non_negative"),
        CheckConstraint(
            "fraud_probability >= 0.0 AND fraud_probability <= 1.0",
            name="chk_transactions_fraud_probability_range",
        ),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="chk_transactions_risk_score_range",
        ),
        Index("ix_transactions_created_at_desc", created_at.desc()),
        Index("ix_transactions_risk_score", risk_score),
        {"extend_existing": True},
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id='{self.id}', amount={self.amount}, "
            f"risk_score={self.risk_score}, risk_label='{self.risk_label}')>"
        )
