# Docstrings

## Rules

- All public functions have docstrings
- One-line summary on first line (imperative mood)
- `Args:` section listing each parameter with description
- `Returns:` section describing the return value
- `Raises:` section if the function raises exceptions
- Private helpers need at minimum a one-liner

## Good

```python
def create_book(title: str, author: str, price_cents: int) -> dict:
    """Create a new book and add it to the catalog.

    Args:
        title: The book's title.
        author: The author's full name.
        price_cents: Price in cents.

    Returns:
        Dict with the created book's details and a "status" key.

    Raises:
        ValueError: If title is empty or price_cents is negative.
    """
```

## Bad

```python
def create_book(title: str, author: str, price_cents: int) -> dict:
    # Creates a book                # comment instead of docstring

def get_book(key: str) -> dict:
    """gets book"""                  # lowercase, no sections, no period
```
