"""
General core helper functions, formatting, and performance utilities.
No business logic is contained herein.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar

# Get module level logger
logger = logging.getLogger(__name__)

# Type variable for decorator typing preservation
F = TypeVar("F", bound=Callable[..., Any])


def format_currency(amount: float, currency_symbol: str = "₹") -> str:
    """
    Formats a raw numerical amount into localized currency display.

    Args:
        amount: Raw numeric amount.
        currency_symbol: Prefix symbol. Defaults to Indian Rupee (₹).

    Returns:
        Formatted currency string, e.g., ₹12,897.00.
    """
    try:
        return f"{currency_symbol}{amount:,.2f}"
    except (ValueError, TypeError) as err:
        logger.error(f"Error formatting currency amount '{amount}': {err}")
        return f"{currency_symbol}0.00"


def calculate_percentage(part: float, total: float, decimal_places: int = 2) -> float:
    """
    Safely calculates percentage representation without throwing division exceptions.

    Args:
        part: The subset value.
        total: The base value.
        decimal_places: Resolution of returned float.

    Returns:
        The fraction percentage as a float. Returns 0.0 if total is 0.
    """
    if not total:
        return 0.0
    try:
        val = (part / total) * 100
        return round(val, decimal_places)
    except (ValueError, TypeError) as err:
        logger.error(f"Error in percentage calculation (part={part}, total={total}): {err}")
        return 0.0


def log_execution_time(func: F) -> F:
    """
    Decorator that calculates execution elapsed durations of core methods for performance profiling.
    """
    @wraps(func)
    def decorator_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logger.error(f"Exc in timed execution of {func.__name__}: {err}")
            raise err
        finally:
            elapsed = time.perf_counter() - start_time
            logger.info(f"Method '{func.__name__}' execution duration: {elapsed:.4f}s")

    return decorator_wrapper  # type: ignore[return-value]
