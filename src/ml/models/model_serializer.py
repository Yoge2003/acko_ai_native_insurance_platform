"""
Model Serializer.
Handles saving and loading serialized model estimators using Joblib.
"""

import logging
from pathlib import Path
from typing import Any, Union
import joblib

# Set up logger
logger = logging.getLogger(__name__)


class ModelSerializer:
    """
    Manager for model serialization and retrieval.
    """

    @staticmethod
    def serialize(model: Any, filepath: Union[str, Path]) -> Path:
        """
        Saves a trained model to a serialized joblib file.

        Args:
            model: Fitted estimator model.
            filepath: Destination file path.

        Returns:
            Path: Path to saved file.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("Serializing model estimator to %s", path)
        try:
            joblib.dump(model, path)
            logger.info("Successfully serialized model.")
        except Exception as e:
            error_msg = f"Failed to serialize model to {path}. Error: {e}"
            logger.error(error_msg)
            raise e
        return path

    @staticmethod
    def deserialize(filepath: Union[str, Path]) -> Any:
        """
        Loads a serialized estimator.

        Args:
            filepath: Source file path.

        Returns:
            Any: Loaded model estimator.
        """
        path = Path(filepath)
        logger.info("Deserializing model estimator from %s", path)
        
        if not path.exists():
            error_msg = f"Model file not found at: {path.absolute()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            model = joblib.load(path)
            logger.info("Successfully loaded model estimator.")
            return model
        except Exception as e:
            error_msg = f"Failed to deserialize model from {path}. Error: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
