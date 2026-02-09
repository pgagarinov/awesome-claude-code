# API Design Standards

This doc loads automatically when editing files in `api/` (hard-included via
`@docs/api-design.md` in `.claude/rules/api.md`).

## Endpoint Structure

All endpoints return a standard response shape:

```json
{"data": { ... }, "error": null}
```

## Naming

| Resource | Endpoint       | Method |
|----------|----------------|--------|
| List     | `/items`       | GET    |
| Create   | `/items`       | POST   |
| Read     | `/items/{id}`  | GET    |
| Update   | `/items/{id}`  | PUT    |
| Delete   | `/items/{id}`  | DELETE |
