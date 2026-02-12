# Type Hints

## Rules

- All function parameters annotated
- Return types annotated
- Modern union syntax: `str | None` not `Optional[str]`
- Use built-in generics: `dict[str, int]` not `Dict[str, int]`
- Dataclass fields annotated (required for `@dataclass`)

## Good

```python
def get_book(key: str) -> dict:
    ...

def validate_isbn(isbn: str) -> bool:
    ...

isbn: str | None = None            # modern union syntax
_stock: dict[str, int] = {}        # built-in generic
```

## Bad

```python
from typing import Optional, Dict

def get_book(key):                  # missing parameter type
    ...

def validate_isbn(isbn: str):      # missing return type
    ...

isbn: Optional[str] = None         # old Optional syntax
_stock: Dict[str, int] = {}        # old Dict from typing
```
