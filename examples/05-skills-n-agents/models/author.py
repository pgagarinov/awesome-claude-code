"""Author model for the BookStore project."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Author:
    """Represents a book author.

    Args:
        name: The author's full name.
        bio: Short biography.
        book_isbns: List of ISBN-13s for the author's books.
    """

    name: str
    bio: str = ""
    book_isbns: list[str] = field(default_factory=list)
