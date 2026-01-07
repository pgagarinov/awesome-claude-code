# Part 29: Statusline Customization

## What is the Statusline?

The status line is a customizable display at the bottom of the Claude Code interface, similar to terminal prompts (PS1) in shells like Oh-my-zsh. It shows contextual information about your current session and updates in real-time.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATUSLINE POSITION                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                                                                  │       │
│  │  Claude Code conversation area                                   │       │
│  │                                                                  │       │
│  │                                                                  │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ > Your input prompt                                              │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │ [Opus] 📁 my-project | 🌿 main | Context: 23%                   │ ← Statusline
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Setup

Use the `/statusline` command:

```bash
> /statusline
```

This attempts to reproduce your terminal's prompt. Add custom instructions:

```bash
> /statusline show the model name in orange and git branch
```

## Manual Configuration

Add to `.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 0
  }
}
```

| Option | Description |
|--------|-------------|
| `type` | Must be `"command"` |
| `command` | Path to your status line script |
| `padding` | Set to `0` for edge-to-edge display |

## How It Works

1. **Update frequency**: At most every 300ms when conversation changes
2. **Output**: First line of stdout becomes the status line text
3. **Styling**: ANSI color codes are supported
4. **Input**: Script receives JSON data via stdin

## JSON Input Structure

Your script receives this context:

```json
{
  "hook_event_name": "Status",
  "session_id": "abc123...",
  "transcript_path": "/path/to/transcript.json",
  "cwd": "/current/working/directory",
  "model": {
    "id": "claude-opus-4-1",
    "display_name": "Opus"
  },
  "workspace": {
    "current_dir": "/current/working/directory",
    "project_dir": "/original/project/directory"
  },
  "version": "1.0.80",
  "cost": {
    "total_cost_usd": 0.01234,
    "total_duration_ms": 45000,
    "total_lines_added": 156,
    "total_lines_removed": 23
  },
  "context_window": {
    "total_input_tokens": 15234,
    "total_output_tokens": 4521,
    "context_window_size": 200000,
    "current_usage": {
      "input_tokens": 8500,
      "output_tokens": 1200,
      "cache_creation_input_tokens": 5000,
      "cache_read_input_tokens": 2000
    }
  }
}
```

## Available Data Fields

| Field | Description |
|-------|-------------|
| `model.display_name` | Model name (Opus, Sonnet, Haiku) |
| `model.id` | Full model ID |
| `workspace.current_dir` | Current working directory |
| `workspace.project_dir` | Original project directory |
| `cost.total_cost_usd` | Session cost in USD |
| `cost.total_duration_ms` | Total API time |
| `cost.total_lines_added` | Lines of code added |
| `cost.total_lines_removed` | Lines of code removed |
| `context_window.context_window_size` | Total context limit |
| `context_window.current_usage` | Current token usage breakdown |

## Example Scripts

### Simple Bash Script

```bash
#!/bin/bash
# ~/.claude/statusline.sh

input=$(cat)
MODEL_DISPLAY=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')

echo "[$MODEL_DISPLAY] 📁 ${CURRENT_DIR##*/}"
```

### Git-Aware Status Line

```bash
#!/bin/bash
# ~/.claude/statusline.sh

input=$(cat)
MODEL_DISPLAY=$(echo "$input" | jq -r '.model.display_name')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir')

# Get git branch if in a repo
GIT_BRANCH=""
if git -C "$CURRENT_DIR" rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH=" | 🌿 $BRANCH"
    fi
fi

echo "[$MODEL_DISPLAY] 📁 ${CURRENT_DIR##*/}$GIT_BRANCH"
```

### Context Usage Display

```bash
#!/bin/bash
# Show context window usage percentage

input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size')
USAGE=$(echo "$input" | jq '.context_window.current_usage')

if [ "$USAGE" != "null" ]; then
    CURRENT_TOKENS=$(echo "$USAGE" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    PERCENT_USED=$((CURRENT_TOKENS * 100 / CONTEXT_SIZE))

    # Color based on usage
    if [ $PERCENT_USED -gt 75 ]; then
        COLOR="\033[31m"  # Red
    elif [ $PERCENT_USED -gt 50 ]; then
        COLOR="\033[33m"  # Yellow
    else
        COLOR="\033[32m"  # Green
    fi

    echo -e "[$MODEL] Context: ${COLOR}${PERCENT_USED}%\033[0m"
else
    echo "[$MODEL] Context: 0%"
fi
```

### Cost Tracking Display

```bash
#!/bin/bash
# Show session cost

input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
LINES_ADDED=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')

# Format cost
if [ "$COST" != "0" ]; then
    COST_FMT=$(printf "%.4f" "$COST")
    echo "[$MODEL] 💰 \$$COST_FMT | +$LINES_ADDED/-$LINES_REMOVED lines"
else
    echo "[$MODEL]"
fi
```

### Python Example

```python
#!/usr/bin/env python3
# ~/.claude/statusline.py

import json
import sys
import os

data = json.load(sys.stdin)

model = data['model']['display_name']
current_dir = os.path.basename(data['workspace']['current_dir'])

# Get context usage
usage = data.get('context_window', {}).get('current_usage')
if usage:
    total = usage.get('input_tokens', 0) + usage.get('cache_creation_input_tokens', 0)
    size = data['context_window']['context_window_size']
    pct = int(total * 100 / size)
    print(f"[{model}] 📁 {current_dir} | Context: {pct}%")
else:
    print(f"[{model}] 📁 {current_dir}")
```

## Full-Featured Status Line

```bash
#!/bin/bash
# ~/.claude/statusline.sh - Full featured status line

input=$(cat)

# Parse JSON
MODEL=$(echo "$input" | jq -r '.model.display_name')
CWD=$(echo "$input" | jq -r '.workspace.current_dir')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size')
USAGE=$(echo "$input" | jq '.context_window.current_usage')

# Directory name
DIR_NAME="${CWD##*/}"

# Git branch
GIT_INFO=""
if git -C "$CWD" rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git -C "$CWD" branch --show-current 2>/dev/null)
    STATUS=$(git -C "$CWD" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ -n "$BRANCH" ]; then
        if [ "$STATUS" -gt 0 ]; then
            GIT_INFO=" 🌿 $BRANCH*"
        else
            GIT_INFO=" 🌿 $BRANCH"
        fi
    fi
fi

# Context percentage
CTX_PCT=""
if [ "$USAGE" != "null" ]; then
    TOKENS=$(echo "$USAGE" | jq '.input_tokens + .cache_creation_input_tokens + .cache_read_input_tokens')
    PCT=$((TOKENS * 100 / CONTEXT_SIZE))
    CTX_PCT=" | 📊 ${PCT}%"
fi

# Cost
COST_INFO=""
if [ "$COST" != "0" ]; then
    COST_FMT=$(printf "%.3f" "$COST")
    COST_INFO=" | 💰 \$$COST_FMT"
fi

echo "[$MODEL] 📁 $DIR_NAME$GIT_INFO$CTX_PCT$COST_INFO"
```

## Installation

1. Create your status line script:
```bash
mkdir -p ~/.claude
cat > ~/.claude/statusline.sh << 'EOF'
#!/bin/bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
echo "[$MODEL] ${DIR##*/}"
EOF
chmod +x ~/.claude/statusline.sh
```

2. Configure Claude Code:
```bash
# Add to ~/.claude/settings.json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh"
  }
}
```

3. Restart Claude Code to see your new status line.

## Tips & Troubleshooting

**Tips:**
- Keep output concise (single line)
- Use ANSI colors for visual distinction
- Use `jq` for JSON parsing in bash
- Test manually: `echo '{"model":{"display_name":"Test"},...}' | ./statusline.sh`

**Troubleshooting:**
- Ensure script is executable: `chmod +x statusline.sh`
- Output must go to stdout (not stderr)
- Script must complete within timeout
- Use `jq -r` to avoid quoted strings

## Official Documentation

- [Statusline Configuration](https://code.claude.com/docs/en/statusline)
