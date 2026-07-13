"""
Database Health Check utilities for the ACKO AI Native Insurance Platform.
Implements the health check query execution and calculates database response latency.
"""

import logging
import time
from typing import Any, Dict
from sqlalchemy import text
import src.database.database as db_module

logger = logging.getLogger(__name__)


def check_database_health() -> Dict[str, Any]:
    """
    Performs a diagnostic database request to check connectivity and response time.
    Executes a standard 'SELECT 1' connection check.

    Returns:
        A dictionary with the following keys:
            - "status" (str): Either "Connected" or "Disconnected".
            - "latency_ms" (float): Duration of query execution in milliseconds.
            - "error" (str or None): Diagnostic messages if exceptions are raised.
    """
    result: Dict[str, Any] = {
        "status": "Disconnected",
        "latency_ms": 0.0,
        "error": None
    }
    
    if db_module.engine is None:
        result["error"] = "Database engine is unconfigured or null."
        logger.error("Health check executed but engine is None.")
        return result

    start_time = time.perf_counter()
    try:
        # Check out connection and run simple query
        with db_module.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        elapsed_time = time.perf_counter() - start_time
        result["status"] = "Connected"
        result["latency_ms"] = round(elapsed_time * 1000, 2)
        logger.info(f"Database health check success with latency: {result['latency_ms']} ms")
    except Exception as err:
        elapsed_time = time.perf_counter() - start_time
        result["latency_ms"] = round(elapsed_time * 1000, 2)
        result["error"] = str(err)
        logger.error(f"Database health check failed: {err}", exc_info=True)

    return result
