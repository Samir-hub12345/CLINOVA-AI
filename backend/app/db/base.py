"""CLINOVA AI — Database Declarative Base.

Clean foundation for Continuous Care Intelligence data persistence.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model class for all SQLAlchemy ORM models in CLINOVA AI."""
    pass
