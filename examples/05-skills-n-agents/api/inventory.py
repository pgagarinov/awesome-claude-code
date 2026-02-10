"""Inventory API for tracking book stock levels."""

# In-memory stock store: key → quantity
_stock: dict[str, int] = {}


def track_stock(book_key: str, quantity: int) -> dict:
    """Set the stock level for a book.

    Args:
        book_key: The book's catalog key (ISBN or title-slug).
        quantity: Number of copies in stock.

    Returns:
        Dict with the updated stock info.

    Raises:
        ValueError: If quantity is negative.
    """
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    _stock[book_key] = quantity
    return {"book_key": book_key, "quantity": quantity, "status": "updated"}


def check_availability(book_key: str) -> dict:
    """Check whether a book is in stock.

    Args:
        book_key: The book's catalog key.

    Returns:
        Dict with availability status and quantity.
    """
    quantity = _stock.get(book_key, 0)
    return {
        "book_key": book_key,
        "quantity": quantity,
        "available": quantity > 0,
    }


def adjust_stock(book_key: str, delta: int) -> dict:
    """Adjust stock by a relative amount (positive = add, negative = remove).

    Args:
        book_key: The book's catalog key.
        delta: Amount to add (positive) or remove (negative).

    Returns:
        Dict with the new stock level.

    Raises:
        ValueError: If the adjustment would make stock negative.
    """
    current = _stock.get(book_key, 0)
    new_quantity = current + delta
    if new_quantity < 0:
        raise ValueError(
            f"Cannot remove {abs(delta)} copies; only {current} in stock"
        )
    _stock[book_key] = new_quantity
    return {"book_key": book_key, "quantity": new_quantity, "status": "adjusted"}
