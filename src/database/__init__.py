"""
Database foundation package for the ACKO AI Native Insurance Platform.
Exposes database engines, session generators, metadata Base classes, and connection utility tasks.
"""

from src.database.database import engine, get_connection_string
from src.database.base import Base
from src.database.session import SessionLocal, get_db
from src.database.connection import connect, disconnect, test_connection
from src.database.health_check import check_database_health
import src.models  # Automatically registers all database schemas on Base.metadata

__all__ = [
    "engine",
    "get_connection_string",
    "Base",
    "SessionLocal",
    "get_db",
    "connect",
    "disconnect",
    "test_connection",
    "check_database_health",
]

