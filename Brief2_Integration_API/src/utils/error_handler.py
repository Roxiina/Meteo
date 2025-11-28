"""
Custom exception classes for Cyclone Tracker.

This module defines a hierarchy of exceptions for different error scenarios.
"""


class APIError(Exception):
    """Base exception for API-related errors."""
    pass


class ValidationError(APIError):
    """Raised when input validation fails."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded (HTTP 429)."""
    pass


class TimeoutError(APIError):
    """Raised when a request times out."""
    pass


class CacheError(Exception):
    """Raised when cache operations fail."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


class DataNotFoundError(APIError):
    """Raised when expected data is missing from API response."""
    pass
