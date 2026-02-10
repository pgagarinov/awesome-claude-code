---
name: audit-codebase
description: Audit codebase for consistency issues, anti-patterns, and missing test coverage
context: fork
agent: Explore
argument-hint: "[focus-area]"
---

# Codebase Audit

Audit this codebase for quality issues. Focus area: **$ARGUMENTS**

If no focus area is specified, perform a full audit.

## Audit Checklist

### 1. Naming Consistency
- Are all functions `snake_case` with verb prefixes?
- Are all classes `PascalCase`?
- Are private helpers prefixed with `_`?
- Are test classes named `TestFunctionName`?

### 2. Import Patterns
- Standard library → third-party → local ordering?
- Absolute imports used (not relative)?
- No wildcard imports?

### 3. Error Handling
- `ValueError` for invalid inputs?
- `KeyError` for missing resources?
- No bare `except:` clauses?
- No silently swallowed exceptions?

### 4. Type Hints
- All function parameters annotated?
- Return types annotated?
- Modern syntax used (`str | None` not `Optional[str]`)?

### 5. Docstrings
- All public functions have docstrings?
- Args/Returns/Raises sections present?
- One-line summary on first line?

### 6. Test Coverage
- Every public function has at least one test?
- Happy path, edge cases, and error cases covered?
- Fixtures used for shared setup?

## Output Format

For each issue found, report:

```
[CATEGORY] file_path:line_number
  Issue: Description of the problem
  Suggestion: How to fix it
```

End with a summary table:

| Category | Issues Found |
|----------|-------------|
| Naming   | N           |
| Imports  | N           |
| Errors   | N           |
| Types    | N           |
| Docs     | N           |
| Tests    | N           |
