"""
Reusable general input validation regex and helper utilities.
Contains no business domain logic rules.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Compile regex structures for performance
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{1,14}$")  # General E.164 format
# Standard Indian vehicle number plate regex, e.g. MH12AB1234 or DL3CA9999
VEHICLE_IND_PATTERN = re.compile(r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,2}[0-9]{4}$")



def is_valid_email(email: str) -> bool:
    """
    Checks if a string has a valid RFC 5322 style email representation.

    Args:
        email: Address string to check.

    Returns:
        Boolean indicating structural validity.
    """
    if not email:
        return False
    try:
        return bool(EMAIL_PATTERN.match(email.strip()))
    except Exception as err:
        logger.error(f"Error checking email validity: {err}")
        return False


def is_valid_phone(phone: str) -> bool:
    """
    Checks if it satisfies E.164 phone formats.

    Args:
        phone: Phone number string.

    Returns:
        Boolean validation outcome.
    """
    if not phone:
        return False
    try:
        clean_phone = phone.strip().replace(" ", "").replace("-", "")
        return bool(PHONE_PATTERN.match(clean_phone))
    except Exception as err:
        logger.error(f"Error checking phone validity: {err}")
        return False


def is_valid_vehicle_registration(reg_number: str) -> bool:
    """
    Validates structural correctness of standard Indian Vehicle Registration numbers.
    Accepts spacings and hyphens which are stripped before checks.

    Args:
        reg_number: String registration plate.

    Returns:
        Boolean validation outcome.
    """
    if not reg_number:
        return False
    try:
        clean_reg = reg_number.strip().upper().replace(" ", "").replace("-", "")
        return bool(VEHICLE_IND_PATTERN.match(clean_reg))
    except Exception as err:
        logger.error(f"Error checking vehicle registration: {err}")
        return False
