"""
Database declarative base module.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    
    Provides a shared metadata registry used by Alembic for autogenerating
    database migrations.
    """
    pass
