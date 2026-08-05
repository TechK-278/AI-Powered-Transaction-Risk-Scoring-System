"""
Database session management module.
"""

from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.database.connection import engine


# Create a reusable session factory bound to the engine
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    
    Yields a new database session for a request and ensures it is properly
    closed once the request completes, regardless of success or failure.

    Yields:
        Session: A SQLAlchemy database session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
