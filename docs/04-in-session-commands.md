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
