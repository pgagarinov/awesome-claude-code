# Claude Code Training Programme

```
   ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗     ██████╗ ██████╗ ██████╗ ███████╗
  ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██║     ██║   ██║██║  ██║█████╗
  ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║     ██║   ██║██║  ██║██╔══╝
  ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
```

A comprehensive guide to mastering Claude Code - from first launch to advanced automation.

---

## Table of Contents

1. [Getting Started](#part-1-getting-started)
2. [The Claude Code Interface](#part-2-the-claude-code-interface)
3. [CLI Commands & Flags](#part-3-cli-commands--flags)
4. [In-Session Commands](#part-4-in-session-commands)
5. [Keyboard Shortcuts](#part-5-keyboard-shortcuts)
6. [CLAUDE.md & Information Architecture](#part-6-claudemd--information-architecture)
7. [Effective Prompting](#part-7-effective-prompting)
8. [Context Management](#part-8-context-management)
9. [Working with Large Files](#part-9-working-with-large-files)
10. [Subagents](#part-10-subagents)
11. [Multi-Modal: Screenshots & Images](#part-11-multi-modal-screenshots--images)
12. [Custom Slash Commands](#part-12-custom-slash-commands)
13. [Skills](#part-13-skills)
14. [MCP Servers](#part-14-mcp-servers)
15. [Claude Code SDK (Python)](#part-15-claude-code-sdk-python)
16. [GitHub Actions Integration](#part-16-github-actions-integration)
17. [Best Practices & Tips](#part-17-best-practices--tips)

---

# Part 1: Getting Started

## Installation

```bash
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code
```

## First Launch

```bash
# Navigate to your project
cd your-project

# Start Claude Code
claude
```

On first run, Claude Code will open your browser for authentication. No API keys needed - just log in with your Anthropic account.

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Welcome to Claude Code!                                       │
│                                                                 │
│   Opening browser for authentication...                         │
│   Once authenticated, return here to continue.                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Official Documentation

- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Getting Started Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

# Part 2: The Claude Code Interface

When you run `claude`, you enter an interactive terminal session:

```
╭────────────────────────────────────────────────────────────────────────────────╮
│ Claude Code                                                    v1.0.0 (Opus)   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ~/projects/my-app                                                             │
│                                                                                │
│  ┌─ Context ─────────────────────────────────────────────────────────────────┐ │
│  │ Files: 42  │  Tokens: 12,450 / 200,000  │  Session: 5m 32s               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  > What would you like to do?                                                  │
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Type your message, or use:                                                │ │
│  │   /help     - Show available commands                                     │ │
│  │   /status   - Show session info                                           │ │
│  │   Ctrl+C    - Cancel current operation                                    │ │
│  │   Ctrl+D    - Exit Claude Code                                            │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
╰────────────────────────────────────────────────────────────────────────────────╯
```

## Interface Elements

| Element | Description |
|---------|-------------|
| **Status Bar** | Shows version, model, and connection status |
| **Working Directory** | Current project path |
| **Context Indicator** | Files loaded, tokens used, session duration |
| **Input Area** | Where you type prompts and commands |
| **Output Area** | Claude's responses, tool outputs, and status messages |

---

# Part 3: CLI Commands & Flags

## Starting Claude Code

### Basic Usage

```bash
# Start interactive session in current directory
claude

# Start with an initial prompt
claude "explain this codebase"

# Start in a specific directory
claude --cwd /path/to/project
```

### Session Management

```bash
# Resume the most recent session
claude --continue
claude -c

# Resume a specific session by ID
claude --resume <session-id>

# Start fresh (ignore previous session)
claude --no-continue
```

### Output Modes

```bash
# Print-only mode (non-interactive, outputs and exits)
claude -p "list all Python files"
claude --print "count lines of code"

# Output as JSON (useful for scripts)
claude -p "list functions" --output-format json

# Stream output in real-time
claude -p "explain main.py" --stream
```

### Model Selection

```bash
# Use a specific model
claude --model claude-sonnet-4-20250514
claude --model opus

# Use Haiku for quick, simple tasks
claude --model haiku
```

### Context Control

```bash
# Start in compact mode (reduced context usage)
claude --compact

# Limit context window
claude --max-tokens 100000

# Add specific files to initial context
claude --add-file src/main.py --add-file README.md
```

### Permission Modes

```bash
# Allow all tool operations without prompting
claude --dangerously-skip-permissions

# Run with specific permission profile
claude --permission-mode default
claude --permission-mode trusted
```

## Complete Flag Reference

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE CLI FLAGS                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  SESSION                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  -c, --continue          Resume most recent session                             │
│  --resume <id>           Resume specific session                                │
│  --no-continue           Start fresh session                                    │
│                                                                                 │
│  INPUT/OUTPUT                                                                   │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  -p, --print             Non-interactive mode, print response and exit          │
│  --output-format <fmt>   Output format: text, json, markdown                    │
│  --stream                Stream response in real-time                           │
│  --verbose               Show detailed operation logs                           │
│  --quiet                 Suppress non-essential output                          │
│                                                                                 │
│  CONTEXT                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --cwd <path>            Set working directory                                  │
│  --add-file <file>       Add file to initial context (can repeat)               │
│  --compact               Start in compact mode                                  │
│  --max-tokens <n>        Limit context window size                              │
│                                                                                 │
│  MODEL                                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --model <name>          Select model (opus, sonnet, haiku)                     │
│                                                                                 │
│  PERMISSIONS                                                                    │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --dangerously-skip-permissions   Skip all permission prompts                   │
│  --permission-mode <mode>         Set permission level                          │
│                                                                                 │
│  OTHER                                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --version               Show version                                           │
│  --help                  Show help                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Practical Examples

```bash
# Quick code review (non-interactive)
claude -p "review src/auth.py for security issues"

# Generate tests and save to file
claude -p "write pytest tests for utils.py" > tests/test_utils.py

# Explain codebase structure as JSON
claude -p "list all modules and their purposes" --output-format json

# Resume yesterday's debugging session
claude --continue

# Start fresh session with specific files pre-loaded
claude --add-file pyproject.toml --add-file src/main.py "help me add a new dependency"
```

---

# Part 4: In-Session Commands

Once inside Claude Code, you have access to slash commands and special operations.

## Essential Commands

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SLASH COMMANDS                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  HELP & INFO                                                                    │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /help              Show all available commands                                 │
│  /status            Show session status, context usage, model info              │
│  /version           Show Claude Code version                                    │
│                                                                                 │
│  SESSION CONTROL                                                                │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /clear             Clear conversation history                                  │
│  /compact           Summarise context to save tokens                            │
│  /exit or /quit     Exit Claude Code                                            │
│                                                                                 │
│  CONTEXT MANAGEMENT                                                             │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /add-file <path>   Add file to context                                         │
│  /init              Generate CLAUDE.md for current project                      │
│                                                                                 │
│  WORKFLOW                                                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /plan              Enter plan mode for complex tasks                           │
│  /review            Review current changes                                      │
│  /security-review   Run security analysis                                       │
│                                                                                 │
│  CONFIGURATION                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /config            Show current configuration                                  │
│  /model <name>      Switch model mid-session                                    │
│  /permissions       Show/modify permission settings                             │
│                                                                                 │
│  TOOLS                                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /tools             List available tools                                        │
│  /mcp               Show MCP server status                                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Command Examples

### /status - View Session Information

```
> /status

╭─ Session Status ────────────────────────────────────────────────────────────────╮
│                                                                                 │
│  Model:           claude-opus-4-20250514                                        │
│  Session ID:      ses_abc123def456                                              │
│  Duration:        12m 34s                                                       │
│                                                                                 │
│  Context Usage:                                                                 │
│  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  32% (64,000 / 200,000 tokens)       │
│                                                                                 │
│  Files in Context: 8                                                            │
│  Messages:         24                                                           │
│                                                                                 │
│  Working Directory: ~/projects/my-app                                           │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

### /compact - Reduce Context Usage

```
> /compact

╭─ Compacting Context ────────────────────────────────────────────────────────────╮
│                                                                                 │
│  Before: 64,000 tokens                                                          │
│  After:  28,500 tokens                                                          │
│  Saved:  35,500 tokens (55%)                                                    │
│                                                                                 │
│  Summary preserved:                                                             │
│  • Project structure and architecture                                           │
│  • Key decisions made in this session                                           │
│  • Current task context                                                         │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

### /init - Generate CLAUDE.md

```
> /init

╭─ Generating CLAUDE.md ──────────────────────────────────────────────────────────╮
│                                                                                 │
│  Analysing project structure...                                                 │
│                                                                                 │
│  Detected:                                                                      │
│  • Language: Python                                                             │
│  • Framework: FastAPI                                                           │
│  • Package Manager: Poetry                                                      │
│  • Test Framework: pytest                                                       │
│                                                                                 │
│  Created: ./CLAUDE.md                                                           │
│                                                                                 │
│  Review and customise the generated file to improve Claude's                    │
│  understanding of your project.                                                 │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

### /plan - Enter Plan Mode

```
> /plan Refactor the authentication system to use JWT

╭─ Plan Mode ─────────────────────────────────────────────────────────────────────╮
│                                                                                 │
│  Planning: Refactor authentication system to use JWT                            │
│                                                                                 │
│  I'll analyse the codebase and create a detailed implementation plan            │
│  before making any changes.                                                     │
│                                                                                 │
│  [Exploring codebase...]                                                        │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

---

# Part 5: Keyboard Shortcuts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         KEYBOARD SHORTCUTS                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ESSENTIAL                                                                      │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  Ctrl + C          Cancel current operation / Interrupt Claude                  │
│  Ctrl + D          Exit Claude Code                                             │
│  Ctrl + L          Clear screen                                                 │
│                                                                                 │
│  NAVIGATION                                                                     │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  ↑ / ↓             Navigate through prompt history                              │
│  Ctrl + R          Search prompt history                                        │
│  Tab               Autocomplete file paths and commands                         │
│                                                                                 │
│  EDITING                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  Ctrl + A          Move cursor to beginning of line                             │
│  Ctrl + E          Move cursor to end of line                                   │
│  Ctrl + W          Delete word before cursor                                    │
│  Ctrl + U          Delete entire line                                           │
│                                                                                 │
│  MULTI-LINE INPUT                                                               │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  Shift + Enter     New line (continue input)                                    │
│  Enter             Submit prompt                                                │
│                                                                                 │
│  PERMISSIONS                                                                    │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  y                 Accept permission request                                    │
│  n                 Deny permission request                                      │
│  a                 Accept all similar requests this session                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

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

## Example CLAUDE.md

```markdown
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
```

---

# Part 7: Effective Prompting

## Prompting Regimes

### 1. Direct Execution (Default)
For straightforward tasks where you trust Claude's approach:

```
> Add input validation to the create_user endpoint

> Fix the TypeError in services/payment.py line 45

> Write pytest tests for the UserService class
```

### 2. Plan Mode
For complex tasks where you want to review the approach first:

```
> /plan Refactor the authentication system to use OAuth2

> I want to add caching. Enter plan mode and design the approach before implementing.
```

**When to use Plan Mode:**
- Architectural changes
- Multi-file refactoring
- Unfamiliar codebases
- When multiple valid approaches exist

### 3. Exploration Mode
When you need information before acting:

```
> Before making any changes, explore how error handling currently
  works across the codebase and summarise the patterns used.

> Don't modify anything yet - just explain how the payment flow works.
```

### 4. Extended Thinking
For complex reasoning tasks:

```
> Think deeply about how to optimise this database query.
  Consider indexes, query structure, and caching strategies.
```

## Prompt Patterns

### The Context-Setting Pattern

```
Context: We're building a REST API for a mobile app.
Constraint: Must support offline-first architecture.
Task: Design the sync mechanism for user data.
Output: Implementation plan with code examples.
```

### The Step-by-Step Pattern

```
Implement user authentication:
1. First, show me your planned approach
2. Wait for my approval
3. Then implement step by step
4. Test each component before moving on
```

### The Constraint Pattern

```
Refactor this function with these constraints:
- No external dependencies
- Must remain backwards compatible
- Keep under 50 lines
- Include error handling
```

### The Example-Driven Pattern

```
Add a new API endpoint following the exact pattern used in
src/api/users.py - same structure, error handling, and response format
```

### The Negative Pattern

```
Update the database schema.
Do NOT:
- Drop any existing columns
- Change column types
- Modify indexes on production tables
```

## Multi-Phase Workflows

```
Let's refactor the payment module:

Phase 1 - Analysis:
- Map all payment-related files
- Identify dependencies
- Document current flow

Phase 2 - Planning:
- Propose new structure
- Identify breaking changes
- Plan migration path

Phase 3 - Implementation:
- Implement changes incrementally
- Update tests after each change
- Verify no regressions

Start with Phase 1 and wait for my go-ahead before each phase.
```

---

# Part 8: Context Management

## Understanding Context

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         THE CONTEXT WINDOW                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Everything in your session consumes context:                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │   Your Prompts                    ████░░░░░░░░░░░░░░░░  ~10%            │   │
│  │   Claude's Responses              ████████░░░░░░░░░░░░  ~25%            │   │
│  │   File Contents Read              ████████████████░░░░  ~50%            │   │
│  │   Tool Outputs                    ███░░░░░░░░░░░░░░░░░  ~10%            │   │
│  │   System Context                  ██░░░░░░░░░░░░░░░░░░  ~5%             │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Context Window: 200,000 tokens (Opus)                                          │
│                                                                                 │
│  When context fills up:                                                         │
│  • Older messages may be summarised                                             │
│  • Performance may degrade                                                      │
│  • You should use /compact or start fresh                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Context Economy Strategies

### 1. Start Fresh for New Tasks

```bash
# New task? Fresh session
claude

# Only continue for related follow-ups
claude --continue
```

### 2. Use Compact Mode

```bash
# Start in compact mode
claude --compact

# Or mid-session
> /compact
```

### 3. Be Specific

```
# BAD: Vague, leads to broad exploration
> Help me understand this codebase

# GOOD: Focused, minimal context needed
> Explain how user authentication works in src/auth/
```

### 4. Use Subagents for Exploration

```
# Instead of exploring yourself (fills YOUR context),
# let a subagent explore (uses SEPARATE context)

> Search the codebase for all error handling patterns and summarise them
```

### 5. Structured Queries

```
# BAD: Multiple back-and-forths
> What files handle auth?
> Now show me the login function
> What about the logout?

# GOOD: Single comprehensive request
> Show me the login and logout functions in the auth module
```

## Context Cheatsheet

| Technique | Savings | When to Use |
|-----------|---------|-------------|
| Subagents for exploration | High | Research, understanding code |
| Targeted file reading | Medium | Working with specific functions |
| `/compact` | Medium | Long sessions |
| Fresh sessions | High | Switching tasks |
| Avoiding full file reads | High | Large files (500+ lines) |

---

# Part 9: Working with Large Files

## The Problem

Large files (500+ lines) consume significant context. Reading them entirely is often unnecessary.

## Strategies

### 1. Targeted Reading

```
# BAD: Read entire file
> Read src/legacy/monolith.py

# GOOD: Read specific sections
> Show me lines 1-50 of src/legacy/monolith.py (the imports)

> Read the UserService class in src/legacy/monolith.py

> Find and show me the process_payment function in src/legacy/monolith.py
```

### 2. Structural Overview First

```
> Give me an outline of src/legacy/monolith.py - list all classes,
  functions, and their line numbers without reading the full content
```

### 3. Search Before Reading

```
> Search for 'validate_user' in src/legacy/monolith.py and show
  me just that function with 10 lines of context
```

### 4. Use Subagents for Analysis

```
> Analyse src/legacy/monolith.py and create a summary of:
  - All exported functions and their purposes
  - Dependencies and imports
  - Potential issues or code smells
  Don't show me the full file, just the analysis.
```

### 5. Chunked Refactoring

```
# Step 1: Understand structure
> Outline the structure of src/legacy/giant_module.py

# Step 2: Identify extraction candidates
> Identify functions that could be extracted into separate modules

# Step 3: Extract incrementally
> Extract the validation logic (lines 150-220) into src/utils/validation.py
```

---

# Part 10: Subagents

## What Are Subagents?

Subagents are separate Claude instances that handle specific tasks with their **own isolated context**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HOW SUBAGENTS WORK                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      MAIN SESSION (Your Context)                        │   │
│  │                                                                         │   │
│  │  You: "Find all security vulnerabilities in the codebase"               │   │
│  │                              │                                          │   │
│  │                              ▼                                          │   │
│  │                    [Spawns Subagent]                                    │   │
│  └──────────────────────────────┼──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    SUBAGENT (Separate Context)                          │   │
│  │                                                                         │   │
│  │  • Reads 20+ files                                                      │   │
│  │  • Searches patterns                                                    │   │
│  │  • Analyses code                                                        │   │
│  │  • Builds understanding                                                 │   │
│  │                                                                         │   │
│  │  All this work stays HERE (doesn't fill your main context)              │   │
│  └──────────────────────────────┼──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      MAIN SESSION (Your Context)                        │   │
│  │                                                                         │   │
│  │  Summary returned: "Found 3 SQL injection risks in api/users.py,        │   │
│  │  api/orders.py, and api/products.py. Also found hardcoded secrets..."   │   │
│  │                                                                         │   │
│  │  Your context only grew by ~200 tokens (the summary)                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Subagent Types

| Type | Use Case | Tools Available |
|------|----------|-----------------|
| `Explore` | Codebase exploration | Read, Glob, Grep |
| `Plan` | Architecture planning | All tools |
| `general-purpose` | Complex multi-step tasks | All tools |

## When to Use Subagents

**Good for Subagents:**
- Codebase exploration ("How does X work?")
- Pattern searching ("Find all uses of Y")
- Research tasks ("What libraries handle Z?")
- Parallel independent tasks
- Tasks requiring reading many files

**Keep in Main Session:**
- Actual code editing
- Interactive decision-making
- Tasks requiring conversation context
- Sequential dependent operations

## Triggering Subagents

Subagents are triggered automatically for appropriate tasks:

```
> Search the entire codebase for deprecated API usage
  # Claude will spawn an Explore subagent

> Explore how the caching layer works across all services
  # Good candidate for subagent

> Analyse these three areas in parallel:
  1. Authentication security
  2. API rate limiting
  3. Data validation
  # May spawn multiple parallel subagents
```

---

# Part 11: Multi-Modal: Screenshots & Images

## Claude's Vision Capabilities

Claude Code can analyse:
- Screenshots of UI/applications
- Error message screenshots
- Design mockups and wireframes
- Architecture diagrams
- Charts and graphs
- Photos of whiteboards

## Providing Images

### Method 1: File Path

```
> Analyse the screenshot at ./screenshots/error.png

> Review the UI mockup at ./designs/homepage-v2.png
```

### Method 2: Drag and Drop

In terminal emulators that support it, drag an image directly into the session.

## Use Cases

### Debugging Visual Issues

```
> Here's a screenshot of the bug: ./screenshots/layout-broken.png
  The sidebar should be on the left but it's overlapping the content.
  Find and fix the CSS issue.
```

### Error Analysis

```
> This screenshot shows the error in my browser console:
  ./screenshots/console-error.png
  Help me debug this issue.
```

### Design Implementation

```
> Implement this UI component based on the mockup at
  ./designs/card-component.png using our existing design system.
```

### Architecture Understanding

```
> Here's a diagram of our system architecture: ./docs/architecture.png
  Explain how data flows from the user request to the database.
```

## Best Practices

```
# BAD: No context
> What's wrong here? [image]

# GOOD: Context + specific focus
> This screenshot shows our checkout page. Users report the 'Submit'
  button is unresponsive. What might cause this? [image]
```

---

# Part 12: Custom Slash Commands

## Creating Custom Commands

Create `.claude/commands/` directory in your project with markdown files:

```
project/
└── .claude/
    └── commands/
        ├── review.md
        ├── test.md
        └── deploy-check.md
```

## Command Structure

```markdown
# .claude/commands/review.md

Review the current changes for:
- Code quality issues
- Potential bugs
- Security vulnerabilities
- Performance concerns

Provide specific, actionable feedback.
```

**Usage:** `/project:review`

## Examples

### Code Review Command

```markdown
# .claude/commands/review.md

Review the staged changes (git diff --cached) for:

1. **Code Quality**
   - Naming conventions
   - Function length and complexity
   - DRY violations

2. **Potential Bugs**
   - Edge cases
   - Null/None handling
   - Error handling

3. **Security**
   - Input validation
   - SQL injection
   - Sensitive data exposure

4. **Testing**
   - Are new functions tested?
   - Are edge cases covered?

Provide specific line-by-line feedback.
```

### New Feature Command

```markdown
# .claude/commands/new-feature.md

Create a new feature following our project patterns:

Feature: $ARGUMENTS

Steps:
1. Create model in src/models/
2. Create schema in src/schemas/
3. Create service in src/services/
4. Create API routes in src/api/
5. Add tests in tests/
6. Update API documentation

Follow patterns from existing features. Ask clarifying questions if needed.
```

**Usage:** `/project:new-feature user preferences`

### Debug Command

```markdown
# .claude/commands/debug.md

Debug the following issue:

Issue: $ARGUMENTS

Process:
1. Identify relevant files
2. Trace the code path
3. Identify root cause
4. Propose fix
5. Wait for approval before implementing
```

**Usage:** `/project:debug users can't log in after password reset`

---

# Part 13: Skills

## What Are Skills?

Skills are pre-packaged capabilities that extend Claude Code for specific file types or tasks. They provide specialised handling that goes beyond default file reading.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SKILLS                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Skills enhance Claude Code's ability to work with specific file types          │
│  or perform specialised tasks.                                                  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Without Skill:                                                         │   │
│  │  PDF → Raw binary / basic text extraction                               │   │
│  │                                                                         │   │
│  │  With PDF Skill:                                                        │   │
│  │  PDF → Structured content + tables + images + metadata                  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Available Skills:                                                              │
│                                                                                 │
│  • pdf        - Enhanced PDF reading and analysis                               │
│  • xlsx       - Excel spreadsheet handling                                      │
│  • docx       - Word document processing                                        │
│  • images     - Advanced image analysis                                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Using Skills

Skills are invoked automatically when relevant, or you can invoke them explicitly:

```
> Analyse the quarterly report at ./reports/Q4-2024.pdf

  [PDF skill activated - extracting structured content...]
```

```
> Extract all tables from ./data/financial-data.xlsx and summarise the trends

  [XLSX skill activated - parsing spreadsheet...]
```

## Skill Capabilities

### PDF Skill
- Extract text with formatting preserved
- Parse tables into structured data
- Extract embedded images
- Read metadata (author, creation date, etc.)
- Handle multi-page documents

### XLSX Skill
- Read multiple sheets
- Parse formulas and values
- Handle merged cells
- Extract charts as data
- Process large spreadsheets efficiently

### DOCX Skill
- Extract formatted text
- Parse tables and lists
- Handle images and diagrams
- Read comments and track changes
- Extract document metadata

## When Skills Activate

Skills activate automatically based on:
1. File extension (.pdf, .xlsx, .docx)
2. File content type
3. Explicit invocation

```
> Read ./docs/specification.pdf
  # PDF skill auto-activates

> What does the spreadsheet at ./data/metrics.xlsx show?
  # XLSX skill auto-activates
```

---

# Part 14: MCP Servers

## What is MCP?

MCP (Model Context Protocol) extends Claude Code with additional tools by connecting to external servers.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MCP ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│  │             │         │             │         │             │               │
│  │ Claude Code │ ◄─────► │ MCP Server  │ ◄─────► │  Database   │               │
│  │             │         │             │         │             │               │
│  └─────────────┘         └─────────────┘         └─────────────┘               │
│                                                                                 │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│  │             │         │             │         │             │               │
│  │ Claude Code │ ◄─────► │ MCP Server  │ ◄─────► │  External   │               │
│  │             │         │             │         │    API      │               │
│  └─────────────┘         └─────────────┘         └─────────────┘               │
│                                                                                 │
│  MCP servers provide Claude Code with:                                          │
│  • Database access (query, understand schema)                                   │
│  • External API integration                                                     │
│  • Custom tools specific to your workflow                                       │
│  • Access to internal systems                                                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Configuring MCP Servers

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["-m", "mcp_server_postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Using MCP Tools

Once configured, MCP tools appear alongside built-in tools:

```
> /mcp

╭─ MCP Servers ───────────────────────────────────────────────────────────────────╮
│                                                                                 │
│  database (connected)                                                           │
│  ├── query          - Execute SQL query                                         │
│  ├── schema         - Get database schema                                       │
│  └── tables         - List all tables                                           │
│                                                                                 │
│  github (connected)                                                             │
│  ├── list_prs       - List pull requests                                        │
│  ├── get_issue      - Get issue details                                         │
│  └── create_pr      - Create pull request                                       │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

```
> Show me the database schema for the users table

  [Using MCP: database.schema]

  Table: users
  ├── id (integer, primary key)
  ├── email (varchar(255), unique)
  ├── password_hash (varchar(255))
  ├── created_at (timestamp)
  └── updated_at (timestamp)
```

---

# Part 15: Claude Code SDK (Python)

## Overview

The Claude Code SDK allows you to control Claude Code programmatically - perfect for automation, CI/CD integration, and building custom tools.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SDK vs CLI                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Aspect              │ CLI                    │ SDK                             │
│  ────────────────────┼────────────────────────┼──────────────────────────────── │
│  Interface           │ Interactive terminal   │ Python code                     │
│  Authentication      │ Browser OAuth          │ Uses existing CLI auth          │
│  Best for            │ Interactive work       │ Automation, scripts             │
│  Customisation       │ Slash commands         │ Full programmatic control       │
│                                                                                 │
│  KEY POINT: The SDK uses your existing Claude Code authentication.              │
│  If `claude` works in your terminal, the SDK works too.                         │
│  No API keys needed.                                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install claude-code-sdk
```

## Basic Usage

```python
from claude_code_sdk import ClaudeCode

# No API key needed - uses your existing Claude Code authentication
claude = ClaudeCode()

# Run a simple task
result = claude.run(
    prompt="Explain the main function in src/main.py",
    cwd="/path/to/project"
)

print(result.response)
```

## Practical Examples

### Batch Code Review

```python
from claude_code_sdk import ClaudeCode
from pathlib import Path

claude = ClaudeCode()

def review_python_files(directory: str) -> dict:
    """Review all Python files in a directory."""
    results = {}

    for py_file in Path(directory).glob("**/*.py"):
        print(f"Reviewing {py_file}...")

        result = claude.run(
            prompt=f"""Review {py_file} for:
            - Code quality issues
            - Potential bugs
            - Security vulnerabilities

            Be concise. List issues with line numbers.""",
            cwd=directory
        )

        results[str(py_file)] = result.response

    return results


if __name__ == "__main__":
    reviews = review_python_files("./src")

    for file, review in reviews.items():
        print(f"\n{'='*60}")
        print(f"FILE: {file}")
        print('='*60)
        print(review)
```

### Automated Documentation Generator

```python
from claude_code_sdk import ClaudeCode
from pathlib import Path

claude = ClaudeCode()

def generate_module_docs(module_path: str) -> str:
    """Generate documentation for a Python module."""

    result = claude.run(
        prompt=f"""Analyse {module_path} and generate documentation in Markdown format:

        1. Module overview (2-3 sentences)
        2. List of classes with brief descriptions
        3. List of functions with signatures and descriptions
        4. Usage examples

        Output only the Markdown, no explanations.""",
        cwd="."
    )

    return result.response


def document_project(src_dir: str, output_dir: str):
    """Generate documentation for all modules in a project."""

    Path(output_dir).mkdir(exist_ok=True)

    for py_file in Path(src_dir).glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue

        print(f"Documenting {py_file}...")

        docs = generate_module_docs(str(py_file))

        # Create output path
        relative = py_file.relative_to(src_dir)
        output_path = Path(output_dir) / relative.with_suffix(".md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(docs)
        print(f"  → {output_path}")


if __name__ == "__main__":
    document_project("./src", "./docs/api")
```

### Test Generator

```python
from claude_code_sdk import ClaudeCode
from pathlib import Path

claude = ClaudeCode()

def generate_tests(source_file: str) -> str:
    """Generate pytest tests for a source file."""

    result = claude.run(
        prompt=f"""Generate comprehensive pytest tests for {source_file}.

        Requirements:
        - Use pytest fixtures where appropriate
        - Include edge cases
        - Mock external dependencies
        - Follow AAA pattern (Arrange, Act, Assert)
        - Add docstrings explaining each test

        Output only the Python code, no explanations.""",
        cwd="."
    )

    return result.response


def generate_missing_tests(src_dir: str, test_dir: str):
    """Generate tests for source files that don't have them."""

    for src_file in Path(src_dir).glob("**/*.py"):
        if src_file.name.startswith("_"):
            continue

        # Determine expected test file path
        relative = src_file.relative_to(src_dir)
        test_file = Path(test_dir) / f"test_{relative}"

        if test_file.exists():
            print(f"Tests exist for {src_file}, skipping")
            continue

        print(f"Generating tests for {src_file}...")

        tests = generate_tests(str(src_file))

        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(tests)
        print(f"  → {test_file}")


if __name__ == "__main__":
    generate_missing_tests("./src", "./tests")
```

### Custom Code Analysis Tool

```python
from claude_code_sdk import ClaudeCode
from dataclasses import dataclass
from pathlib import Path
import json

claude = ClaudeCode()

@dataclass
class SecurityIssue:
    file: str
    line: int
    severity: str
    description: str
    recommendation: str


def security_scan(directory: str) -> list[SecurityIssue]:
    """Scan a directory for security issues."""

    result = claude.run(
        prompt=f"""Perform a security audit of the Python code in {directory}.

        Look for:
        - SQL injection vulnerabilities
        - Command injection
        - Hardcoded secrets
        - Insecure deserialization
        - Path traversal
        - XSS vulnerabilities

        Output as JSON array with this structure:
        [{{
            "file": "path/to/file.py",
            "line": 42,
            "severity": "high|medium|low",
            "description": "What the issue is",
            "recommendation": "How to fix it"
        }}]

        Output ONLY the JSON, no other text.""",
        cwd=directory
    )

    # Parse the JSON response
    issues_data = json.loads(result.response)

    return [SecurityIssue(**issue) for issue in issues_data]


def print_security_report(issues: list[SecurityIssue]):
    """Print a formatted security report."""

    print("\n" + "="*70)
    print("SECURITY SCAN REPORT")
    print("="*70)

    # Group by severity
    high = [i for i in issues if i.severity == "high"]
    medium = [i for i in issues if i.severity == "medium"]
    low = [i for i in issues if i.severity == "low"]

    for severity, items in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if items:
            print(f"\n{severity} SEVERITY ({len(items)} issues)")
            print("-"*40)
            for issue in items:
                print(f"\n  File: {issue.file}:{issue.line}")
                print(f"  Issue: {issue.description}")
                print(f"  Fix: {issue.recommendation}")

    print("\n" + "="*70)
    print(f"Total: {len(high)} high, {len(medium)} medium, {len(low)} low")
    print("="*70)


if __name__ == "__main__":
    issues = security_scan("./src")
    print_security_report(issues)
```

### Integration with Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook using Claude Code SDK."""

from claude_code_sdk import ClaudeCode
import subprocess
import sys

claude = ClaudeCode()

def get_staged_files() -> list[str]:
    """Get list of staged Python files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]


def review_changes() -> tuple[bool, str]:
    """Review staged changes for issues."""

    files = get_staged_files()
    if not files:
        return True, "No Python files to review"

    result = claude.run(
        prompt=f"""Review the staged changes (git diff --cached) for critical issues only:

        Files changed: {', '.join(files)}

        Check for:
        1. Obvious bugs (null references, infinite loops, etc.)
        2. Security vulnerabilities
        3. Syntax errors

        If there are critical issues, output them clearly.
        If no critical issues, just say "LGTM".

        Be concise.""",
        cwd="."
    )

    response = result.response.strip()

    if "LGTM" in response:
        return True, response
    else:
        return False, response


if __name__ == "__main__":
    passed, message = review_changes()
    print(message)
    sys.exit(0 if passed else 1)
```

## SDK Configuration

```python
from claude_code_sdk import ClaudeCode

# Basic configuration
claude = ClaudeCode(
    cwd="/path/to/default/project",  # Default working directory
    model="opus",                     # Default model
    compact=True,                     # Use compact mode
)

# Run with overrides
result = claude.run(
    prompt="Analyse this code",
    cwd="/different/project",  # Override for this call
    model="haiku",             # Use faster model for simple task
)
```

---

# Part 16: GitHub Actions Integration

## Automated PR Reviews

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: review
```

## Issue Triage

```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: triage
          issue_number: ${{ github.event.issue.number }}
```

## Security Review on PRs

```yaml
# .github/workflows/security-review.yml
name: Security Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Perform a security review of the changes in this PR.
            Focus on:
            - Authentication/authorization issues
            - Input validation
            - SQL injection
            - XSS vulnerabilities
            - Sensitive data exposure

            Report findings as comments on specific lines.
```

---

# Part 17: Best Practices & Tips

## Do's and Don'ts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BEST PRACTICES                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  DO ✓                                                                           │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Create a CLAUDE.md for every project                                         │
│  • Be specific in your requests                                                 │
│  • Use /plan for complex changes                                                │
│  • Start fresh sessions for new tasks                                           │
│  • Let subagents handle exploration                                             │
│  • Review generated code before committing                                      │
│  • Use custom commands for repetitive workflows                                 │
│                                                                                 │
│  DON'T ✗                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Don't read entire large files unnecessarily                                  │
│  • Don't continue sessions across unrelated tasks                               │
│  • Don't give vague prompts ("fix this", "improve this")                        │
│  • Don't skip reviewing generated code                                          │
│  • Don't forget to use /compact in long sessions                                │
│  • Don't ignore permission prompts - understand what's being done               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Productivity Tips

### 1. Create Project-Specific Commands

```markdown
# .claude/commands/pr.md
Create a pull request for the current branch:
1. Summarise all commits since branching from main
2. Generate a clear PR title and description
3. Create the PR using gh cli
```

### 2. Use Templates in CLAUDE.md

```markdown
## Code Patterns

When creating new endpoints, follow this template:
\```python
@router.post("/", response_model=schemas.Response)
async def create_item(
    data: schemas.CreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.Response:
    """Create a new item."""
    return await services.item.create(db, data=data, user=user)
\```
```

### 3. Leverage Non-Interactive Mode for Scripts

```bash
# Quick checks
claude -p "are there any TODO comments in src/?"

# Generate and save
claude -p "write a README for this project" > README.md

# Chain with other tools
claude -p "list all API endpoints" | grep POST
```

### 4. Use Keyboard Shortcuts

- `Ctrl+C` to interrupt long operations
- `↑` to recall previous prompts
- `Tab` to autocomplete paths

### 5. Regular Context Maintenance

```
# Check context usage periodically
> /status

# Compact when above 50%
> /compact

# Start fresh for unrelated tasks
$ claude  # (not --continue)
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE QUICK REFERENCE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  STARTING                          SESSION COMMANDS                             │
│  claude                            /help         - Show help                    │
│  claude "prompt"                   /status       - Session info                 │
│  claude -c (continue)              /compact      - Reduce context               │
│  claude -p "prompt" (print)        /clear        - Clear history                │
│  claude --compact                  /plan         - Enter plan mode              │
│                                                                                 │
│  KEYBOARD                          PROMPTING                                    │
│  Ctrl+C    - Cancel                Be specific, not vague                       │
│  Ctrl+D    - Exit                  Use /plan for complex tasks                  │
│  ↑/↓       - History               Add constraints explicitly                   │
│  Tab       - Autocomplete          Reference existing patterns                  │
│                                                                                 │
│  CONTEXT TIPS                      FILES                                        │
│  Fresh session = new task          Use CLAUDE.md for project context            │
│  /compact when > 50% full          Route to detailed docs                       │
│  Subagents for exploration         Read sections, not whole files               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Additional Resources

### Official Documentation
- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Common Workflows](https://docs.anthropic.com/en/docs/claude-code/common-workflows)
- [Settings Reference](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

### Repositories
- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 2025 | Initial programme |
| 2.0 | December 2025 | Complete rewrite: CLI focus, Python examples, visual guides, skills documentation |

---

*This training programme is based on official Anthropic documentation. For the latest updates, refer to [docs.anthropic.com](https://docs.anthropic.com).*
