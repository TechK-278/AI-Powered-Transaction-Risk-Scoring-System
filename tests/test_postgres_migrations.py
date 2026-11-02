"""
PostgreSQL migration test (Phase 12).

Runs the Alembic migrations up and down against a real PostgreSQL database.
Opt-in: set RUN_POSTGRES_TESTS=1. Because the test downgrades to an empty
schema, it refuses to run unless the configured database name contains
"test", protecting development and production databases.
"""

import os
import unittest
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url

from app.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"


def postgres_test_skip_reason() -> str | None:
    """Return why the PostgreSQL test cannot run, or None when it can."""
    if os.environ.get("RUN_POSTGRES_TESTS") != "1":
        return "Set RUN_POSTGRES_TESTS=1 to run PostgreSQL migration tests."
    database_url = make_url(settings.database_url)
    if not database_url.drivername.startswith("postgresql"):
        return "DATABASE_URL does not point to PostgreSQL."
    if "test" not in (database_url.database or ""):
        return "Refusing to run: DATABASE_URL database name must contain 'test'."
    return None


@unittest.skipIf(postgres_test_skip_reason() is not None, postgres_test_skip_reason() or "")
class TestAlembicMigrationsOnPostgres(unittest.TestCase):
    """Upgrade/downgrade round trip of the Alembic migration history."""

    def setUp(self) -> None:
        from alembic.config import Config

        self.alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
        self.alembic_config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        self.engine = create_engine(settings.database_url)

    def tearDown(self) -> None:
        self.engine.dispose()

    def test_upgrade_creates_transactions_table_and_downgrade_removes_it(self) -> None:
        from alembic import command

        command.upgrade(self.alembic_config, "head")
        inspector = inspect(self.engine)
        self.assertIn("transactions", inspector.get_table_names())
        column_names = {column["name"] for column in inspector.get_columns("transactions")}
        self.assertTrue(
            {"id", "amount", "time", "fraud_probability", "risk_score", "risk_label", "created_at"} <= column_names
        )

        command.downgrade(self.alembic_config, "base")
        self.assertNotIn("transactions", inspect(self.engine).get_table_names())

        command.upgrade(self.alembic_config, "head")


if __name__ == "__main__":
    unittest.main()
