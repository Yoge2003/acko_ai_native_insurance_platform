"""
Inference Prediction Logger.
Logs latency, model version, and secure SHA-256 hashes of input/output data (excluding PII).
"""

import os
import time
import logging
from datetime import datetime
import hashlib
from typing import Any
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)

AUDIT_LOG_FILE = "logs/prediction_audit.csv"


class PredictionLogger:
    """
    MLOps logging service recording run metrics and cryptographic input hashes.
    """

    @staticmethod
    def compute_input_hash(df_input: pd.DataFrame) -> str:
        """
        Computes SHA-256 hash representative of input DataFrame without preserving fields.
        """
        try:
            # Hash values structure to avoid preserving PII
            data_bytes = df_input.to_json(orient="values").encode("utf-8")
            return hashlib.sha256(data_bytes).hexdigest()
        except Exception as e:
            logger.warning("Failed to calculate input hash: %s", e)
            return "unknown_input_hash"

    @staticmethod
    def compute_prediction_hash(prediction: Any) -> str:
        """
        Computes SHA-256 hash of prediction result.
        """
        try:
            val_bytes = str(prediction).encode("utf-8")
            return hashlib.sha256(val_bytes).hexdigest()
        except Exception as e:
            logger.warning("Failed to calculate prediction hash: %s", e)
            return "unknown_prediction_hash"

    @classmethod
    def log_prediction(
        cls,
        dataset_type: str,
        model_version: str,
        latency_ms: float,
        input_hash: str,
        prediction_hash: str
    ) -> None:
        """
        Writes MLOps metrics to rotating debug loggers and appends to audit CSV record.
        """
        timestamp = datetime.now().isoformat()
        
        # Log to debug
        logger.info(
            "Prediction Audits - Type: %s, Version: %s, Latency: %.2fms, InputHash: %s, PredictionHash: %s",
            dataset_type, model_version, latency_ms, input_hash[:8], prediction_hash[:8]
        )

        # Write to structured file logs/prediction_audit.csv
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)
        
        log_row = pd.DataFrame([{
            "timestamp": timestamp,
            "dataset_type": dataset_type,
            "model_version": model_version,
            "latency_ms": latency_ms,
            "input_hash": input_hash,
            "prediction_hash": prediction_hash
        }])

        header = not os.path.exists(AUDIT_LOG_FILE)
        try:
            log_row.to_csv(AUDIT_LOG_FILE, mode="a", index=False, header=header, encoding="utf-8")
        except Exception as e:
            logger.error("Failed to append entry to prediction audit CSV log: %s", e)
