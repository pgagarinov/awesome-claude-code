# API Module (Subtree Router)

This loads when Claude works in `api/`. It supplements the root CLAUDE.md.

## Local Rules

- All endpoints MUST include a `version` parameter defaulting to `"v1"`
- Use `async def` for all endpoint functions

## Local Commands

| Command | Description |
|---------|-------------|
| `pytest api/` | Run API tests only |
