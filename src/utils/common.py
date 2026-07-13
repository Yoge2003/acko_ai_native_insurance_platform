"""
Common helper functions and shared type structures.
Contains no business logic.
"""

import logging
import uuid
from datetime import date, datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


def generate_uuid() -> str:
    """
    Generates a unique identifier (UUID v4) for transactional logging and tracking.

    Returns:
        String UUID format, e.g. 'c9a646d3-9c61-4cd4-bc11-3d7f55ec1c19'.
    """
    return str(uuid.uuid4())


def serialize_datetime(value: Any) -> str:
    """
    Safely serializes a datetime or date object into standard ISO 8601 format.

    Args:
        value: Datetime or Date object.

    Returns:
        ISO 8601 formatted string or empty string if input serialization fails.
    """
    if isinstance(value, (datetime, date)):
        try:
            return value.isoformat()
        except Exception as err:
            logger.error(f"Error serializing date/datetime '{value}': {err}")
            return ""
    logger.debug(f"Input is not a datetime/date object (received type: {type(value)})")
    return ""


def clean_dictionary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively strips leading/trailing whitespaces from keys and removes key-value
    pairs whose values are None. Useful for cleansing forms and queries.

    Args:
        payload: Dict to clean.

    Returns:
        A cleaned dictionary copy.
    """
    if not isinstance(payload, dict):
        return payload
    
    cleaned = {}
    for key, val in payload.items():
        if val is None:
            continue
        
        # Format string keys
        clean_key = key.strip() if isinstance(key, str) else key
        
        if isinstance(val, dict):
            cleaned[clean_key] = clean_dictionary(val)
        else:
            cleaned[clean_key] = val
            
    return cleaned
