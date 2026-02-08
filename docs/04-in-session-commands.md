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
│  /doctor            Diagnose installation and configuration issues              │
│  /debug             Ask Claude to help troubleshoot the current session         │
│  /usage             Show plan usage and limits                                  │
│  /stats             Show session statistics (favourite model, usage graph)      │
│  /context           Show context token breakdown and usage                      │
│                                                                                 │
│  SESSION CONTROL                                                                │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /clear             Clear conversation history                                  │
│  /compact           Summarise context to save tokens                            │
│  /resume            Open session picker or resume by name                       │
│  /rename <name>     Name the current session for easy recall                    │
│  /rewind            Undo conversation to a previous point                       │
│  /export            Export conversation for sharing                             │
│  /exit or /quit     Exit Claude Code                                            │
│                                                                                 │
│  CONTEXT MANAGEMENT                                                             │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /add-file <path>   Add file to context                                         │
│  /add-dir <path>    Add additional working directory                            │
│  /init              Generate CLAUDE.md for current project                      │
│  /memory            Edit memory files (CLAUDE.md and imports)                   │
│                                                                                 │
│  WORKFLOW                                                                       │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /plan              Enter plan mode for complex tasks                           │
│  /review            Review current changes                                      │
│  /security-review   Run security analysis                                       │
│  /tasks             View and manage background tasks                            │
│                                                                                 │
│  CONFIGURATION                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /config             Open configuration settings                                │
│  /model <name>       Switch model mid-session                                   │
│  /fast               Toggle fast mode (same model, faster output)              │
│  /permissions        Show/modify permission settings                            │
│  /keybindings        Configure custom keyboard shortcuts                        │
│  /terminal-setup     Configure terminal for optimal Claude Code usage           │
│  /theme              Open theme picker                                          │
│                                                                                 │
│  TOOLS & EXTENSIONS                                                             │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  /tools             List available tools                                        │
│  /mcp               Show MCP server status, enable/disable servers              │
│  /sandbox            Show sandbox status and toggle sandbox mode                │
│  /skills             List available skills and slash commands                    │
│  /agents             Create and manage custom subagents                         │
│  /plugins            Install, enable, and manage plugins                        │
│  /hooks              Configure hooks interactively                              │
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

## Session Management

### Naming Sessions

Name sessions for easy recall:
```
> /rename auth-refactor
```

Later resume by name:
```bash
claude --resume auth-refactor
```

### Session Picker

`claude --resume` opens an interactive picker with keyboard shortcuts:
- `↑`/`↓` - Navigate sessions
- `Enter` - Select session
- `P` - Preview session
- `R` - Rename session
- `/` - Search sessions
- `B` - Filter by git branch

Sessions are grouped by repository and worktree.

See [Common Workflows: Resume Sessions](https://code.claude.com/docs/en/common-workflows#resume-previous-conversations).
