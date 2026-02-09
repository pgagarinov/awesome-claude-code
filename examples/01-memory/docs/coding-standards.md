# Coding Standards

This doc is hard-imported via `@docs/coding-standards.md` in `CLAUDE.md`.
It loads in **every** conversation regardless of which files are being edited.

## Error Handling

- All functions that can fail must return a tuple: `(result, error_message)`
- Never raise exceptions for expected failure cases
- Use `None` as the result on failure: `return (None, "not found")`

## Logging

- Every module must call `import logging` and create a logger:
  `logger = logging.getLogger(__name__)`
