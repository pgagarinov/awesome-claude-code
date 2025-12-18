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
