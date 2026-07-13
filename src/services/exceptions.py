"""
Custom exceptions for the Business Service Layer of the ACKO Insurance Platform.
"""

class ServiceException(Exception):
    """Base exception for all service layer errors."""
    pass


class ValidationError(ServiceException):
    """Raised when request inputs fail basic validation constraints."""
    pass


class ResourceNotFoundError(ServiceException):
    """Raised when a requested database entity cannot be retrieved by its identifier."""
    pass


class DuplicateResourceError(ServiceException):
    """Raised when attempting to create a record that conflicts with an existing unique key or entity constraint."""
    pass


class BusinessRuleViolationError(ServiceException):
    """Raised when an operation violates active insurance business policies or rules."""
    pass
