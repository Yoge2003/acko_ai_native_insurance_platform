"""
Database Engine configuration for the ACKO AI Native Insurance Platform.
Initializes the SQLAlchemy Engine with optimized pooling options configuration.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_connection_string(masked: bool = False) -> str:
    """
    Constructs the PostgreSQL connection string.

    Args:
        masked: If True, replaces the password with asterisks for safe logging.

    Returns:
        Structured PostgreSQL connection string URL.
    """
    password = "••••••••" if masked else settings.POSTGRES_PASSWORD
    return (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:{password}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def create_db_engine() -> Engine:
    """
    Configures and creates a SQLAlchemy Engine.
    Implements pool pre-ping (connection liveliness checks), pooling settings,
    and returns the engine instance.

    Returns:
        SQLAlchemy Engine instance.
    
    Raises:
        Exception: If database engine creation fails.
    """
    connection_url = get_connection_string(masked=False)
    masked_url = get_connection_string(masked=True)
    
    try:
        # pool_recycle re-creates connections older than 30 minutes (1800s) to avoid database timeouts.
        # pool_pre_ping verifies connection viability at the start of each checkout step.
        engine = create_engine(
            url=connection_url,
            pool_size=15,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False,
            future=True
        )
        logger.info(f"Database Engine initialized successfully for: {masked_url}")
        return engine
    except Exception as err:
        logger.critical(f"CRITICAL: Failed to create database engine for: {masked_url}. Details: {err}", exc_info=True)
        raise err


# Create and export default engine instance
try:
    engine: Engine = create_db_engine()
except Exception as e:
    logger.error(f"Engine instancing warning: DB Engine start deferred. Connection error: {e}")
    # Maintain reference placeholder if it fails at import time in offsite tests
    engine = None  # type: ignore[assignment, name-defined]
