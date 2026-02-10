"""Tests for the catalog API."""

import pytest
from api.catalog import create_book, get_book, list_books, search_books, _books


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the in-memory store before each test."""
    _books.clear()
    yield
    _books.clear()


class TestCreateBook:
    def test_create_book_basic(self):
        result = create_book("The Hobbit", "J.R.R. Tolkien", 1499)
        assert result["status"] == "created"
        assert result["book"]["title"] == "The Hobbit"
        assert result["book"]["price"] == "$14.99"

    def test_create_book_with_isbn(self):
        result = create_book("Dune", "Frank Herbert", 1699, isbn="9780441013593")
        assert result["key"] == "9780441013593"

    def test_create_book_empty_title_raises(self):
        with pytest.raises(ValueError, match="Title cannot be empty"):
            create_book("", "Author", 999)

    def test_create_book_negative_price_raises(self):
        with pytest.raises(ValueError, match="Price cannot be negative"):
            create_book("Title", "Author", -100)


class TestGetBook:
    def test_get_existing_book(self):
        create_book("1984", "George Orwell", 1299, isbn="9780451524935")
        book = get_book("9780451524935")
        assert book["title"] == "1984"

    def test_get_missing_book_raises(self):
        with pytest.raises(ValueError, match="Book not found"):
            get_book("nonexistent")


class TestListBooks:
    def test_list_empty(self):
        assert list_books() == []

    def test_list_multiple(self):
        create_book("Book A", "Author A", 999)
        create_book("Book B", "Author B", 1999)
        assert len(list_books()) == 2


class TestSearchBooks:
    def test_search_by_title(self):
        create_book("Python Crash Course", "Eric Matthes", 2999)
        create_book("Fluent Python", "Luciano Ramalho", 4999)
        results = search_books("python")
        assert len(results) == 2

    def test_search_by_author(self):
        create_book("Python Crash Course", "Eric Matthes", 2999)
        results = search_books("matthes")
        assert len(results) == 1

    def test_search_no_match(self):
        create_book("Python Crash Course", "Eric Matthes", 2999)
        assert search_books("javascript") == []
