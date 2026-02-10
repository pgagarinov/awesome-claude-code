# Acceptance Criteria: Hello Python

1. **greet function exists**: `from main import greet` succeeds without error.
2. **greet returns correct string**: `greet("World")` returns exactly `"Hello, World!"`.
3. **greet handles other names**: `greet("Alice")` returns `"Hello, Alice!"`.
4. **test file exists**: `test_main.py` exists in the project root.
5. **tests pass**: Running `python -m pytest test_main.py -v` exits with code 0 and shows at least 3 passing tests.
