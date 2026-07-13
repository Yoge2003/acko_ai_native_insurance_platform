"""
Central logger establishing rotating file logs for platform domains.
Manages file buffers for auth, prediction, claims, quotation, RAG, Manager AI, database, dashboard, and system.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import List

os.makedirs("logs", exist_ok=True)


class LogManager:
    """
    Central logger establishing rotating files for corporate domains.
    """
    
    _loggers = {}
    
    @staticmethod
    def get_logger(domain: str) -> logging.Logger:
        """
        Retrieves or instantiates a domain-specific RotatingFileHandler logger.
        """
        domain = domain.lower().strip()
        if domain in LogManager._loggers:
            return LogManager._loggers[domain]
            
        logger = logging.getLogger(f"acko_{domain}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        
        if not logger.handlers:
            log_file = f"logs/{domain}.log"
            handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        LogManager._loggers[domain] = logger
        return logger

    @classmethod
    def get_recent_logs(cls, domain: str, num_lines: int = 50) -> List[str]:
        """Reads the tail of specific domain log file."""
        log_file = f"logs/{domain.lower().strip()}.log"
        if not os.path.exists(log_file):
            return []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-num_lines:]]
        except Exception as e:
            return [f"Error reading log file: {e}"]
