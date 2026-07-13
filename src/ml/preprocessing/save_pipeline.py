"""
Pipeline persistence layer.
Handles saving and loading of fitted preprocessing pipelines using joblib.
"""

import os
import logging
from pathlib import Path
from typing import Union
import joblib
from sklearn.pipeline import Pipeline

# Set up logger
logger = logging.getLogger(__name__)


def get_saved_pipelines_dir() -> Path:
    """
    Returns the path to the directory where ML pipelines are saved.

    Returns:
        Path: Path to saved_pipelines directory.
    """
    base_dir = Path(__file__).resolve().parent.parent
    saved_dir = base_dir / "saved_pipelines"
    saved_dir.mkdir(parents=True, exist_ok=True)
    return saved_dir


def save_pipeline(pipeline: Pipeline, filename: str) -> Path:
    """
    Serializes a fitted scikit-learn pipeline using joblib.

    Args:
        pipeline: Fitted scikit-learn Pipeline object to save.
        filename: Destination filename (e.g. 'car_quotation_pipeline.joblib').

    Returns:
        Path: Absolute path to the saved file.

    Raises:
        ValueError: If pipeline is not a valid Pipeline instance.
        IOError: If serialization fails.
    """
    if not isinstance(pipeline, Pipeline):
        error_msg = f"Expected scikit-learn Pipeline instance, got {type(pipeline)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    saved_dir = get_saved_pipelines_dir()
    file_path = saved_dir / filename

    logger.info("Saving fitted pipeline to: %s", file_path)
    try:
        joblib.dump(pipeline, file_path)
        logger.info("Successfully saved pipeline to %s", file_path)
        return file_path
    except Exception as e:
        error_msg = f"Failed to save pipeline to path '{file_path}'. Error: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg) from e


def load_pipeline(filename: str) -> Pipeline:
    """
    Loads a serialized fitted scikit-learn pipeline from disk.

    Args:
        filename: Name of the saved pipeline file.

    Returns:
        Pipeline: The loaded Pipeline object.

    Raises:
        FileNotFoundError: If the pipeline file does not exist.
        IOError: If deserialization fails.
    """
    saved_dir = get_saved_pipelines_dir()
    file_path = saved_dir / filename

    if not file_path.exists():
        # Fallback: check if the input filename is an absolute path that exists
        alt_path = Path(filename)
        if alt_path.is_absolute() and alt_path.exists():
            file_path = alt_path
        else:
            error_msg = f"Pipeline file not found at: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    logger.info("Loading pipeline from: %s", file_path)
    try:
        pipeline = joblib.load(file_path)
        if not isinstance(pipeline, Pipeline):
            logger.warning("Loaded object is of type %s, expected Pipeline.", type(pipeline))
        logger.info("Successfully loaded pipeline from %s", file_path)
        return pipeline
    except Exception as e:
        error_msg = f"Failed to load pipeline from '{file_path}'. Error: {str(e)}"
        logger.error(error_msg)
        raise IOError(error_msg) from e
