# Naming Consistency

## Rules

- Functions use `snake_case` with verb prefixes (`get_`, `create_`, `check_`, `validate_`)
- Classes use `PascalCase` (e.g., `Book`, `TestCreateBook`)
- Private helpers prefixed with `_` (e.g., `_to_dict`)
- Test classes named `TestFunctionName` (e.g., `TestGetBook`)
- Constants use `UPPER_SNAKE_CASE` (e.g., `API_TOKEN`)
- Module-level private vars prefixed with `_` (e.g., `_books`, `_stock`)

## Good

```python
def create_book(title: str) -> dict:       # verb prefix
class TestCreateBook:                       # PascalCase, mirrors function
_books: dict[str, Book] = {}               # private module var
```

## Bad

```python
def book_creation(title: str) -> dict:     # noun, no verb prefix
class Create_Book_Tests:                    # underscores in class name
books: dict[str, Book] = {}                # missing _ prefix for private
```
