"""String validation utilities."""

import logging

logger = logging.getLogger(__name__)


def validate_non_empty(value: str):
    """Check that a string is not empty or whitespace-only."""
    if not isinstance(value, str) or not value.strip():
        logger.debug("Validation failed: empty or non-string value")
        return (None, "value must be a non-empty string")
    return (value.strip(), None)


def validate_max_length(value: str, max_length: int):
    """Check that a string does not exceed a maximum length."""
    if not isinstance(value, str):
        return (None, "value must be a string")
    if len(value) > max_length:
        logger.debug("Validation failed: length %d exceeds max %d", len(value), max_length)
        return (None, f"value exceeds max length of {max_length}")
    return (value, None)


def validate_alphanumeric(value: str):
    """Check that a string contains only alphanumeric characters."""
    if not isinstance(value, str) or not value.isalnum():
        logger.debug("Validation failed: non-alphanumeric value")
        return (None, "value must contain only alphanumeric characters")
    return (value, None)
