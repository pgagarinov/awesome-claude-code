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
claude --model claude-sonnet-4-5-20250929
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
│  --resume <id|name>      Resume specific session by ID or name                  │
│  --no-continue           Start fresh session                                    │
│  --session-id <id>       Use a custom session ID                                │
│  --from-pr <num|url>     Resume session linked to a GitHub PR                   │
│  --fork-session          Fork the resumed session                               │
│                                                                                 │
│  INPUT/OUTPUT                                                                   │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  -p, --print             Non-interactive mode, print response and exit          │
│  --output-format <fmt>   Output format: text, json, stream-json                 │
│  --stream                Stream response in real-time                           │
│  --verbose               Show detailed operation logs                           │
│  --quiet                 Suppress non-essential output                          │
│                                                                                 │
│  CONTEXT                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --cwd <path>            Set working directory                                  │
│  --add-dir <path>        Add additional working directory (can repeat)          │
│  --add-file <file>       Add file to initial context (can repeat)               │
│  --compact               Start in compact mode                                  │
│  --max-tokens <n>        Limit context window size                              │
│                                                                                 │
│  MODEL & AGENT                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --model <name>          Select model (opus, sonnet, haiku)                     │
│  --agent <name>          Use a custom agent configuration                       │
│                                                                                 │
│  PERMISSIONS & TOOLS                                                            │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --dangerously-skip-permissions   Skip all permission prompts                   │
│  --permission-mode <mode>         Set permission level                          │
│  --allowedTools <tools>           Restrict available tools (legacy)             │
│  --disallowedTools <tools>        Explicitly block tools (legacy)               │
│  --tools <tools>                  Restrict built-in tools (interactive mode)    │
│  --disable-slash-commands         Disable all slash commands                     │
│                                                                                 │
│  SYSTEM PROMPT                                                                  │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --system-prompt <text>           Override system prompt (-p mode)               │
│  --system-prompt-file <path>      Load system prompt from file                  │
│  --append-system-prompt <text>    Append to system prompt                       │
│                                                                                 │
│  SETUP & MAINTENANCE                                                            │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --init                  Run Setup hooks for repository initialisation          │
│  --init-only             Run Setup hooks and exit                               │
│  --maintenance           Run Setup hooks tagged as maintenance                  │
│  --settings <path>       Load settings from a JSON file                         │
│                                                                                 │
│  BUDGET                                                                         │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --max-budget-usd <n>    Set maximum spending budget in USD                     │
│                                                                                 │
│  OTHER                                                                          │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  --version               Show version                                           │
│  --help                  Show help                                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

For the complete CLI reference, see the [official CLI documentation](https://code.claude.com/docs/en/cli-reference).

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

## Headless Mode (Advanced)

Headless mode enables fully automated, non-interactive Claude Code usage for scripts, CI/CD pipelines, and programmatic integrations.

### Core Headless Flags

```bash
# Basic headless execution
claude -p "prompt" --output-format json

# Structured output with JSON schema
claude -p "list all functions" --json-schema '{"type":"object","properties":{"functions":{"type":"array"}}}'

# Custom system prompts
claude -p "review code" --system-prompt "You are a security auditor"
claude -p "explain" --append-system-prompt "Focus on performance"

# Restrict available tools
claude -p "analyze code" --allowedTools "Read,Grep,Glob"
claude -p "make changes" --allowedTools "Bash(npm test:*),Edit"
```

> **Note**: `--allowedTools` and `--disallowedTools` are legacy flags. For new projects, use `allowed-tools` and `disallowed-tools` in agent/skill frontmatter configuration.

### Tool Restriction Patterns

The `--allowedTools` flag supports glob patterns:

| Pattern | Description |
|---------|-------------|
| `Read` | Allow all Read operations |
| `Bash(npm *)` | Allow npm commands only |
| `Bash(git diff:*)` | Allow git diff with any args |
| `Edit(src/**)` | Allow edits only in src/ |
| `Bash(npm test),Bash(npm run lint)` | Allow specific commands |

### Structured Output with JSON Schema

```bash
# Define expected output structure
claude -p "list all API endpoints" --json-schema '{
  "type": "object",
  "properties": {
    "endpoints": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "method": {"type": "string"},
          "path": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    }
  }
}'
```

### Session Management in Scripts

```bash
# Run and capture session ID for later resumption
RESULT=$(claude -p "start analysis" --output-format json)
SESSION_ID=$(echo "$RESULT" | jq -r '.session_id')

# Resume later with the session ID
claude --resume "$SESSION_ID" -p "continue with the next step"
```

### Piping with jq

```bash
# Extract specific fields from JSON output
claude -p "list files" --output-format json | jq '.files[]'

# Chain multiple Claude calls
claude -p "find bugs" --output-format json | \
  jq -r '.bugs[].file' | \
  xargs -I {} claude -p "fix bugs in {}"

# Conditional processing
claude -p "check for issues" --output-format json | \
  jq -e '.issues | length > 0' && \
  claude -p "fix all issues"
```

### CI/CD Integration Pattern

```bash
#!/bin/bash
# ci-review.sh - Automated code review in CI

# Run review with restricted permissions
# Note: --allowedTools is legacy; prefer agent frontmatter for tool restrictions
RESULT=$(claude -p "review changes for security issues" \
  --output-format json \
  --allowedTools "Read,Grep,Glob" \
  --max-tokens 50000)

# Check for critical issues
CRITICAL=$(echo "$RESULT" | jq '.issues[] | select(.severity == "critical")')

if [ -n "$CRITICAL" ]; then
  echo "Critical issues found:"
  echo "$CRITICAL" | jq -r '.description'
  exit 1
fi

echo "Review passed"
exit 0
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | API key for direct API access |
| `CLAUDE_CODE_USE_BEDROCK=1` | Use AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX=1` | Use Google Vertex AI |
| `CLAUDE_CONFIG_DIR` | Custom config directory |
| `DISABLE_PROMPT_CACHING` | Disable prompt caching |

### Agent SDK Integration

For more complex programmatic integrations, use the Claude Agent SDK:

```typescript
import { Agent } from "@anthropic-ai/agent";

const agent = new Agent({
  model: "claude-sonnet-4-5-20250929",
});

const result = await agent.run("Review this codebase for bugs");
console.log(result.output);
```

See [Part 16: Agent SDK](16-agent-sdk.md) for comprehensive SDK documentation.

---

## Using Claude as a Unix Utility

Pipe data to Claude for scripted workflows:

```bash
# Analyse file content
cat error.log | claude -p "summarise the errors"

# Output formats
claude -p "list functions" --output-format json
claude -p "explain this" --output-format stream-json
```
