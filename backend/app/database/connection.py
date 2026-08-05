"""
Database connection management.
"""

from sqlalchemy import Engine, create_engine

from app.core.config import settings


if not settings.database_url:
    raise ValueError("DATABASE_URL is not configured.")


engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)