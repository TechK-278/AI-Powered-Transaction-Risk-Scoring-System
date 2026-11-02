"""
Shared pytest configuration.

* Every test runs against an isolated in-memory SQLite database through a
  `get_db` dependency override, so the suite never writes to the developer's
  PostgreSQL database and does not require one (CI only needs DATABASE_URL to
  be set so the engine module can be imported; no connection is opened).
* Tests needing the trained model use `model_artifacts.requires_model_artifacts`
  to skip where the gitignored artifacts are absent (e.g. CI).
"""

from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.transaction import Transaction  # noqa: F401  (registers the table on Base.metadata)


def create_sqlite_session_factory() -> sessionmaker:
    """Create a session factory bound to a fresh in-memory SQLite database shared across threads."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def isolated_database() -> Generator[sessionmaker, None, None]:
    """Route the API's database dependency to a per-test in-memory SQLite database."""
    session_factory = create_sqlite_session_factory()

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield session_factory
    app.dependency_overrides.pop(get_db, None)
