"""
Database Connection Manager for the ACKO AI Native Insurance Platform.
Implements helper functions to establish, check, and safely disconnect connection pools.
Ensures zero-crash behaviors under runtime DB failures.
"""

import logging
from typing import Tuple
from sqlalchemy import text
from sqlalchemy.engine import Engine
from src.database.database import get_connection_string
import src.database.database as db_module

logger = logging.getLogger(__name__)


def connect() -> Tuple[bool, str]:
    """
    Validates and initializes the database engine if uninstantiated.
    Performs a connection check to verify database access.

    Returns:
        Tuple[bool, str]: (Success status boolean, descriptive log message).
    """
    masked_url = get_connection_string(masked=True)
    
    try:
        # Re-initialize engine if it was not created during import time due to config issues
        if db_module.engine is None:
            logger.info("Database engine was uninitialized. Attempting to create one now.")
            db_module.engine = db_module.create_db_engine()

        # Perform test checkout
        with db_module.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        msg = f"Database connection successfully established to: {masked_url}"
        logger.info(msg)
        return True, msg
    except Exception as err:
        msg = f"Failed to connect to database: {masked_url}. Details: {err}"
        logger.error(msg, exc_info=True)
        return False, msg


def disconnect() -> Tuple[bool, str]:
    """
    Safely disposes of the connection pool inside the engine.
    Releases all TCP sockets connected to the database server.

    Returns:
        Tuple[bool, str]: (Success status boolean, descriptive log message).
    """
    if db_module.engine is None:
        msg = "No database engine to disconnect. Engine was already uninitialized."
        logger.warning(msg)
        return True, msg

    try:
        db_module.engine.dispose()
        msg = "Database connection pool disposed of successfully."
        logger.info(msg)
        return True, msg
    except Exception as err:
        msg = f"Unexpected error occurred during database engine connection pool disposal: {err}"
        logger.error(msg, exc_info=True)
        return False, msg


def test_connection() -> Tuple[bool, str]:
    """
    Tests database connectivity by fetching a connection from the pool and executing a query.
    Similar to connect(), but focuses on reporting system connection health status safely resource-wise.

    Returns:
        Tuple[bool, str]: (Alive boolean flag, health description message).
    """
    if db_module.engine is None:
        return False, "Database engine is unconfigured or null. Verify credentials."
        
    try:
        with db_module.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Database is alive and responsive."
    except Exception as err:
        msg = f"Database test query check failed. Exception details: {err}"
        logger.error(msg)
        return False, msg
