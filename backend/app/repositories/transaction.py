"""
Repository module for transaction database operations.
"""

from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:
    """
    Data access repository for Transaction entity persistence and queries.
    """

    @staticmethod
    def create(
        db: Session,
        *,
        amount: float,
        time: float,
        fraud_probability: float,
        risk_score: int,
        risk_label: str,
    ) -> Transaction:
        """
        Persist a new transaction risk assessment record.

        Args:
            db: Active SQLAlchemy database session.
            amount: Evaluated monetary amount.
            time: Elapsed seconds timestamp.
            fraud_probability: Evaluated fraud probability in [0.0, 1.0].
            risk_score: Integer risk score in [0, 100].
            risk_label: Risk category ('Low', 'Medium', 'High').

        Returns:
            Transaction: The persisted ORM entity.
        """
        transaction = Transaction(
            amount=amount,
            time=time,
            fraud_probability=fraud_probability,
            risk_score=risk_score,
            risk_label=risk_label,
        )
        db.add(transaction)
        db.flush()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def get_by_id(db: Session, transaction_id: str) -> Optional[Transaction]:
        """
        Retrieve a single transaction evaluation by its unique ID.

        Args:
            db: Active SQLAlchemy database session.
            transaction_id: UUID string primary key.

        Returns:
            Optional[Transaction]: The transaction record if found, else None.
        """
        statement = select(Transaction).where(Transaction.id == transaction_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_paginated(
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        risk_label: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        max_risk_score: Optional[int] = None,
    ) -> tuple[Sequence[Transaction], int]:
        """
        Retrieve paginated transaction records with optional risk filtering.

        Args:
            db: Active SQLAlchemy database session.
            skip: Number of records to offset.
            limit: Maximum number of records to return.
            risk_label: Optional filter for risk tier ('Low', 'Medium', 'High').
            min_risk_score: Optional minimum risk score (inclusive).
            max_risk_score: Optional maximum risk score (inclusive).

        Returns:
            tuple[Sequence[Transaction], int]: (List of matching transaction entities, total count matching filter).
        """
        # Base query with filters applied
        query = select(Transaction)
        count_query = select(func.count(Transaction.id))

        filters = []
        if risk_label:
            # Case-insensitive label match
            filters.append(func.lower(Transaction.risk_label) == risk_label.strip().lower())
        if min_risk_score is not None:
            filters.append(Transaction.risk_score >= min_risk_score)
        if max_risk_score is not None:
            filters.append(Transaction.risk_score <= max_risk_score)

        if filters:
            for f in filters:
                query = query.where(f)
                count_query = count_query.where(f)

        # Total count matching criteria
        total_count = db.scalar(count_query) or 0

        # Query items ordered by newest first
        query = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)
        items = db.scalars(query).all()

        return items, total_count
