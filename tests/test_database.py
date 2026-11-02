"""
Unit and integration tests for Phase 09 PostgreSQL Database Integration.

Tests SQLAlchemy 2.0 Transaction ORM model and TransactionRepository
CRUD, pagination, and filter queries.
"""

import unittest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models.transaction import Transaction
from app.repositories.transaction import TransactionRepository


class TestDatabaseRepository(unittest.TestCase):
    """Test suite for Transaction model and TransactionRepository."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up in-memory database and session for isolated repository testing."""
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(cls.engine)
        cls.SessionLocal = sessionmaker(bind=cls.engine, autocommit=False, autoflush=False)

    @classmethod
    def tearDownClass(cls) -> None:
        """Tear down database."""
        Base.metadata.drop_all(cls.engine)
        cls.engine.dispose()

    def setUp(self) -> None:
        """Create fresh tables and a new session for each test."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self.db: Session = self.SessionLocal()

    def tearDown(self) -> None:
        """Rollback and close session."""
        self.db.rollback()
        self.db.close()

    def test_transaction_model_creation(self) -> None:
        """Test creating a Transaction ORM instance with defaults."""
        tx = Transaction(
            amount=150.0,
            time=3600.0,
            fraud_probability=0.05,
            risk_score=5,
            risk_label="Low",
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)

        self.assertIsNotNone(tx.id)
        self.assertEqual(len(tx.id), 36)  # UUID format
        self.assertEqual(tx.amount, 150.0)
        self.assertEqual(tx.time, 3600.0)
        self.assertEqual(tx.fraud_probability, 0.05)
        self.assertEqual(tx.risk_score, 5)
        self.assertEqual(tx.risk_label, "Low")
        self.assertIsNotNone(tx.created_at)
        self.assertIn("150.0", repr(tx))

    def test_repository_create_and_get_by_id(self) -> None:
        """Test creating a transaction record via repository and fetching by ID."""
        tx = TransactionRepository.create(
            db=self.db,
            amount=250.0,
            time=1200.0,
            fraud_probability=0.88,
            risk_score=88,
            risk_label="High",
        )
        self.db.commit()

        fetched = TransactionRepository.get_by_id(db=self.db, transaction_id=tx.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.id, tx.id)
        self.assertEqual(fetched.amount, 250.0)
        self.assertEqual(fetched.risk_score, 88)
        self.assertEqual(fetched.risk_label, "High")

    def test_repository_get_by_id_not_found(self) -> None:
        """Test querying a non-existent transaction ID returns None."""
        non_existent_id = str(uuid.uuid4())
        result = TransactionRepository.get_by_id(db=self.db, transaction_id=non_existent_id)
        self.assertIsNone(result)

    def test_repository_get_paginated_and_filters(self) -> None:
        """Test paginated retrieval and filtering by risk label and score range."""
        # Create a set of transactions
        records = [
            (10.0, 0.10, 10, "Low"),
            (20.0, 0.20, 20, "Low"),
            (50.0, 0.45, 45, "Medium"),
            (80.0, 0.65, 65, "Medium"),
            (200.0, 0.85, 85, "High"),
            (500.0, 0.95, 95, "High"),
        ]
        for amount, prob, score, label in records:
            TransactionRepository.create(
                db=self.db,
                amount=amount,
                time=100.0,
                fraud_probability=prob,
                risk_score=score,
                risk_label=label,
            )
        self.db.commit()

        # 1. Total count without filters
        items, total = TransactionRepository.get_paginated(db=self.db, skip=0, limit=100)
        self.assertGreaterEqual(total, 6)

        # 2. Filter by risk_label = 'High'
        high_items, high_total = TransactionRepository.get_paginated(
            db=self.db, skip=0, limit=10, risk_label="High"
        )
        self.assertEqual(high_total, 2)
        for item in high_items:
            self.assertEqual(item.risk_label, "High")

        # 3. Filter by min_risk_score = 40 and max_risk_score = 70 (Medium)
        med_items, med_total = TransactionRepository.get_paginated(
            db=self.db, skip=0, limit=10, min_risk_score=40, max_risk_score=70
        )
        self.assertEqual(med_total, 2)
        for item in med_items:
            self.assertTrue(40 <= item.risk_score <= 70)

        # 4. Pagination: page 1 of size 2
        page1_items, _ = TransactionRepository.get_paginated(db=self.db, skip=0, limit=2)
        self.assertEqual(len(page1_items), 2)


if __name__ == "__main__":
    unittest.main()
