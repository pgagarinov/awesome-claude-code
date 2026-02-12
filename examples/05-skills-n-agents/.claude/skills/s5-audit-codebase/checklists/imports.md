# Import Patterns

## Rules

- Order: standard library → third-party → local (blank line between groups)
- Use absolute imports, not relative (`from models.book import Book`)
- No wildcard imports (`from module import *`)
- Import only what you need (no unused imports)

## Good

```python
import re                          # stdlib first

import pytest                      # third-party second

from models.book import Book       # local third, absolute path
from api.catalog import create_book
```

## Bad

```python
from models.book import Book       # local before stdlib
import re
from .book import Book             # relative import
from api.catalog import *          # wildcard import
```
