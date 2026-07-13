"""
Logging configuration for the ACKO AI Native Insurance Platform.
Implements a production-ready logging setup with console output and a daily rotating file handler.
Logs are placed under the `src/logs/` directory.
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# Path to the source root
SRC_ROOT = Path(__file__).resolve().parent.parent


def get_log_level(level_name: str) -> int:
    """
    Translates string log levels dynamically to logging integer components.
    """
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_name.upper(), logging.INFO)


def configure_logging(
    log_level_override: Optional[str] = None,
    log_dir_override: Optional[Path] = None
) -> None:
    """
    Initializes and configures the root logger.
    Sets up a Console Handler and a daily TimedRotatingFileHandler.

    Args:
        log_level_override: Custom logging level (e.g. 'DEBUG'). Defaults to Settings configurations.
        log_dir_override: Custom logging directory path. Defaults to src/logs/
    """
    # Defer setting import to avoid circular dependency problems on system startup
    from src.config.settings import settings

    # Resolve log level
    lvl_str = log_level_override or settings.LOG_LEVEL
    level = get_log_level(lvl_str)

    # Resolve log directory
    log_dir = log_dir_override or (SRC_ROOT / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "app.log"

    # Define standard log format
    # Example format: 2026-07-08 19:45:00,123 | INFO | src/config/logging_config.py:34 | Application started.
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Clear any existing handlers on root to prevent duplicate logs
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)

    # 1. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # 2. Daily Rotating File Handler
    # rotates at midnight, keeps 30 days of archives
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file_path),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    logging.info(f"Logging configured successfully. Level: {lvl_str}, Log File: {log_file_path}")


# Run logging configuration on package import
try:
    configure_logging()
except Exception as err:
    print(f"FAILED TO CONFIGURE LOGGING SYSTEM: {err}")
