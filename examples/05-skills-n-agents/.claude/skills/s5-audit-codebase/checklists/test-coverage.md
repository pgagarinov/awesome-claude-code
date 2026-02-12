# Test Coverage

## Rules

- Every public function has at least one test
- Cover happy path, edge cases, and error cases
- Use `pytest.fixture` for shared setup (e.g., clearing in-memory stores)
- Test classes named `TestFunctionName` grouping related tests
- Use `pytest.raises` with `match=` for error case assertions

## Good

```python
@pytest.fixture(autouse=True)
def clear_store():
    """Clear the in-memory store before each test."""
    _books.clear()
    yield
    _books.clear()

class TestCreateBook:
    def test_create_book_basic(self):              # happy path
        result = create_book("The Hobbit", "Tolkien", 1499)
        assert result["status"] == "created"

    def test_create_book_empty_title_raises(self): # error case
        with pytest.raises(ValueError, match="Title cannot be empty"):
            create_book("", "Author", 999)
```

## Bad

```python
def test_stuff():                                  # vague name, no class
    create_book("Book", "Author", 100)
    assert get_book("book") is not None            # no error case testing
    # no fixture — leaks state between tests
```
