"""Book model for the BookStore project."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Book:
    """Represents a book in the store catalog.

    Args:
        title: The book's title.
        author: The author's full name.
        price_cents: Price in cents (avoids floating-point issues).
        isbn: Optional ISBN-13 identifier.
        genre: Optional BISAC subject code (e.g., "FIC000000").
    """

    title: str
    author: str
    price_cents: int
    isbn: str | None = None
    genre: str | None = None

    def price_display(self) -> str:
        """Return human-readable price string.

        Returns:
            Formatted price like "$12.99".
        """
        dollars = self.price_cents // 100
        cents = self.price_cents % 100
        return f"${dollars}.{cents:02d}"
