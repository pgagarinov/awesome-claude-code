# Error Handling

## Rules

- `ValueError` for invalid inputs (empty strings, negative numbers)
- `KeyError` for missing resources (book not found, key not in store)
- No bare `except:` clauses — always catch specific exceptions
- No silently swallowed exceptions (empty `except` blocks)
- Error messages should be descriptive and include the invalid value

## Good

```python
def create_book(title: str, price_cents: int) -> dict:
    if not title:
        raise ValueError("Title cannot be empty")
    if price_cents < 0:
        raise ValueError("Price cannot be negative")
```

## Bad

```python
def create_book(title: str, price_cents: int) -> dict:
    try:
        book = Book(title=title, price_cents=price_cents)
    except:                        # bare except — catches everything
        pass                       # silently swallowed
    if price_cents < 0:
        raise Exception("bad")    # generic exception, vague message
```
