"""
SQLAlchemy Declarative Base definition for the ACKO AI Native Insurance Platform.
All future ORM models will inherit from this Base to bind schemas to metadata.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.x Declarative Base class.
    Serves as the root class for database mapping.
    """
    pass
