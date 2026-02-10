"""Validation utilities for the BookStore project.

NOTE: The ISBN validation here is intentionally incomplete — it only checks
format with a regex, not the check digit. The publishing-domain skill (S2)
knows the full ISBN-13 check digit algorithm and will produce correct
validation when asked to improve this module.
"""

import re


def validate_isbn(isbn: str) -> bool:
    """Validate an ISBN-13 string (format check only).

    Args:
        isbn: The ISBN string to validate.

    Returns:
        True if the ISBN matches the 13-digit format.

    NOTE: This only checks the format (13 digits starting with 978 or 979).
    It does NOT verify the check digit. See the publishing-domain skill
    for the full algorithm.
    """
    # Intentionally incomplete: regex only, no check digit validation
    pattern = r"^(978|979)\d{10}$"
    return bool(re.match(pattern, isbn))


def validate_price(price_cents: int) -> bool:
    """Validate that a price is non-negative.

    Args:
        price_cents: Price in cents.

    Returns:
        True if price is valid (non-negative integer).
    """
    return isinstance(price_cents, int) and price_cents >= 0
