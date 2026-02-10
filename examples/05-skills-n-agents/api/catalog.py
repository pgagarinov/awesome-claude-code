"""Catalog API for managing books in the store."""

from models.book import Book

# In-memory store (would be a database in production)
_books: dict[str, Book] = {}


def create_book(title: str, author: str, price_cents: int, isbn: str | None = None) -> dict:
    """Create a new book and add it to the catalog.

    Args:
        title: The book's title.
        author: The author's full name.
        price_cents: Price in cents.
        isbn: Optional ISBN-13 identifier.

    Returns:
        Dict with the created book's details and a "status" key.

    Raises:
        ValueError: If title is empty or price_cents is negative.
    """
    if not title:
        raise ValueError("Title cannot be empty")
    if price_cents < 0:
        raise ValueError("Price cannot be negative")

    book = Book(title=title, author=author, price_cents=price_cents, isbn=isbn)
    key = isbn or title.lower().replace(" ", "-")
    _books[key] = book
    return {"status": "created", "key": key, "book": _to_dict(book)}


def get_book(key: str) -> dict:
    """Retrieve a book by its key (ISBN or title-slug).

    Args:
        key: The book's catalog key.

    Returns:
        Dict with the book's details.

    Raises:
        ValueError: If the book is not found.
    """
    book = _books.get(key)
    if book is None:
        raise ValueError(f"Book not found: {key}")
    return _to_dict(book)


def list_books() -> list[dict]:
    """List all books in the catalog.

    Returns:
        List of dicts, each containing a book's details.
    """
    return [_to_dict(book) for book in _books.values()]


def search_books(query: str) -> list[dict]:
    """Search books by title or author (case-insensitive substring match).

    Args:
        query: Search string to match against title and author.

    Returns:
        List of matching book dicts.
    """
    # NOTE: Uses string formatting — a pattern the security-review skill
    # is designed to flag in more dangerous contexts (e.g., SQL queries).
    query_lower = query.lower()
    results = []
    for book in _books.values():
        if query_lower in book.title.lower() or query_lower in book.author.lower():
            results.append(_to_dict(book))
    return results


def _to_dict(book: Book) -> dict:
    """Convert a Book dataclass to a plain dict."""
    return {
        "title": book.title,
        "author": book.author,
        "price": book.price_display(),
        "price_cents": book.price_cents,
        "isbn": book.isbn,
        "genre": book.genre,
    }
