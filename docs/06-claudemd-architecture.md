# Part 6: CLAUDE.md & Information Architecture

## What is CLAUDE.md?

CLAUDE.md is a special markdown file that provides Claude Code with persistent context about your project. It's like giving Claude a briefing document before starting work.

## File Hierarchy

Claude Code reads CLAUDE.md files from multiple locations:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE.MD HIERARCHY                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  LOADING ORDER (all are loaded and combined):                                   │
│                                                                                 │
│  1. ~/.claude/CLAUDE.md                    ← Global (all projects)              │
│     │                                                                           │
│     │   Your personal preferences, common patterns, global settings             │
│     │                                                                           │
│  2. ./CLAUDE.md                            ← Project root                       │
│     │                                                                           │
│     │   Project overview, architecture, build commands                          │
│     │                                                                           │
│  3. ./src/CLAUDE.md                        ← Subdirectory                       │
│     │                                                                           │
│     │   Module-specific patterns, local conventions                             │
│     │                                                                           │
│  4. ./src/components/CLAUDE.md             ← Deeper subdirectory                │
│                                                                                 │
│        Component-specific guidelines                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Information Routing

Instead of putting everything in one massive file, use **references** to route Claude to relevant documentation:

```markdown
# CLAUDE.md (Project Root)

## Project Overview
E-commerce API built with FastAPI and PostgreSQL.

## Quick Commands
- Run server: `uvicorn main:app --reload`
- Run tests: `pytest`
- Format code: `black . && isort .`

## Detailed Documentation
For specific topics, refer to:
- API Design: See `docs/api-design.md`
- Database Schema: See `docs/database-schema.md`
- Authentication: See `docs/auth-flow.md`

## When Working On...
- **API endpoints**: Read `docs/api-design.md` first
- **Database changes**: Consult `docs/database-schema.md`
- **Authentication**: Check `docs/auth-flow.md`
```

## Recommended Project Structure

```
project/
├── CLAUDE.md                    # High-level overview, routing
├── .claude/
│   ├── commands/                # Custom slash commands
│   │   ├── review.md
│   │   └── deploy.md
│   └── settings.json            # Claude Code settings
├── docs/
│   ├── api-design.md            # Detailed API documentation
│   ├── database-schema.md       # Schema details, migrations
│   ├── auth-flow.md             # Authentication architecture
│   └── deployment.md            # Deployment procedures
├── src/
│   ├── CLAUDE.md                # Source code conventions
│   ├── api/
│   │   └── CLAUDE.md            # API module patterns
│   ├── models/
│   │   └── CLAUDE.md            # Model conventions
│   └── services/
│       └── CLAUDE.md            # Service layer patterns
└── tests/
    └── CLAUDE.md                # Testing conventions
```

## `.claude/` vs `docs/` - Where to Put Documentation

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              WHERE TO STORE CLAUDE-RELATED DOCUMENTATION                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  .claude/                              docs/                                    │
│  ──────────────────────────────────    ───────────────────────────────────────  │
│                                                                                 │
│  Claude Code-SPECIFIC files:           GENERAL project documentation:          │
│  • Custom slash commands               • API design docs                        │
│  • settings.json (Claude config)       • Architecture documentation             │
│  • Hooks configuration                 • Database schema docs                   │
│  • MCP server configs                  • Deployment guides                      │
│                                        • User guides                            │
│                                        • Changelog                              │
│                                                                                 │
│  NOT automatically loaded              Referenced FROM CLAUDE.md               │
│  (except settings.json)                when needed                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Differences

| Aspect | `.claude/` | `docs/` |
|--------|------------|---------|
| **Purpose** | Claude Code tool configuration | General project documentation |
| **Auto-loaded** | Only `settings.json` | No (referenced from CLAUDE.md) |
| **Git** | Usually in `.gitignore` (local settings) | Always committed |
| **Shared with team** | Commands yes, settings maybe | Yes, always |
| **Contains** | Commands, hooks, MCP configs | Human & AI-readable docs |

### Best Practice

Use `docs/` for documentation that Claude should read when referenced:

```markdown
# CLAUDE.md

## Documentation
When working on the API, first read `docs/api-design.md`.
When working on the database, consult `docs/database-schema.md`.
```

Use `.claude/` only for Claude Code configuration:

```
.claude/
├── commands/           # Slash commands (shared with team)
│   ├── review.md
│   └── test.md
├── settings.json       # Local settings (often .gitignore'd)
└── settings.local.json # Personal overrides (always .gitignore'd)
```

### Why Not Put Docs in `.claude/`?

1. **Visibility**: `docs/` is a standard, discoverable location
2. **Tooling**: Many tools expect docs in `docs/` (GitHub, MkDocs, etc.)
3. **Separation**: Keep config (`.claude/`) separate from content (`docs/`)
4. **Git**: `.claude/` often has local-only files; `docs/` is always shared

## Example CLAUDE.md

````markdown
# MyApp - E-commerce API

## Overview
FastAPI-based REST API for e-commerce platform. Uses PostgreSQL with SQLAlchemy ORM.

## Architecture
- **API Layer**: FastAPI routers in `src/api/`
- **Service Layer**: Business logic in `src/services/`
- **Data Layer**: SQLAlchemy models in `src/models/`
- **Schemas**: Pydantic models in `src/schemas/`

## Development Commands
```bash
# Start development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest -v

# Run tests with coverage
pytest --cov=src --cov-report=html

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"

# Code formatting
black src tests
isort src tests
```

## Code Style
- Use type hints everywhere
- Docstrings for all public functions (Google style)
- Keep functions under 30 lines
- Prefer composition over inheritance

## Important Patterns

### API Endpoints
All endpoints follow this pattern:
```python
@router.get("/{id}", response_model=schemas.ItemResponse)
async def get_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.ItemResponse:
    """Get item by ID."""
    item = await services.item.get(db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

### Error Handling
Use custom exceptions from `src/exceptions.py`:
```python
from src.exceptions import NotFoundError, ValidationError

if not item:
    raise NotFoundError("Item", id)
```

## Testing
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Use fixtures from `tests/conftest.py`
- Mock external services, never hit real APIs in tests

## Known Issues
- Rate limiting not implemented yet (TODO)
- Image upload limited to 5MB (server constraint)
````
