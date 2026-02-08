# Part 22: Claude Code Hooks

## What are Hooks?

Hooks are custom scripts that Claude Code executes at specific points during its workflow. They let you intercept tool calls, validate changes, inject context, and control Claude's behavior without modifying Claude Code itself.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HOOK EXECUTION FLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  User Prompt ──► UserPromptSubmit hook                                      │
│        │                                                                    │
│        ▼                                                                    │
│  Claude thinks ──► PreToolUse hook ──► Tool executes ──► PostToolUse hook   │
│        │                                                                    │
│        ▼                                                                    │
│  Claude stops ──► Stop hook (can block and continue)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Hook Types

| Hook | When It Fires | Use Case |
|------|---------------|----------|
| `PreToolUse` | Before tool execution | Block dangerous commands, modify inputs |
| `PostToolUse` | After tool completes | Format code, validate output, inject feedback |
| `Stop` | When Claude finishes responding | Run validation, prevent premature stops (see [Part 25](25-ralf-loop.md) for Ralf Loop patterns) |
| `SubagentStop` | When a subagent (Task tool) finishes | QA gates on subagent work |
| `UserPromptSubmit` | When user submits a prompt | Add context, block dangerous requests |
| `SessionStart` | Session begins or resumes | Load environment, inject context |
| `SessionEnd` | Session terminates | Cleanup, logging |
| `PreCompact` | Before context compaction | Pre-compaction cleanup |
| `Notification` | Claude sends notifications | Custom notification delivery |
| `PermissionRequest` | User shown permission dialog | Auto-approve or deny |
| `Setup` | `--init`, `--init-only`, `--maintenance` | Repository setup, dependency install |
| `SubagentStart` | Subagent spawned | Track subagent lifecycle |
| `TeammateIdle` | Agent team member goes idle | Multi-agent coordination |
| `TaskCompleted` | Background task finishes | Multi-agent workflow notifications |

## Two Key Distinctions

### A. Functional vs Prompt-Based Hooks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FUNCTIONAL vs PROMPT-BASED HOOKS                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FUNCTIONAL (`type: "command"`):                                            │
│  ┌──────────┐    stdin     ┌──────────────┐   exit code   ┌─────────┐      │
│  │ Claude   │───(JSON)────►│ Your Script  │──────────────►│ Result  │      │
│  │ Code     │              │ (bash/python)│   + stdout    │         │      │
│  └──────────┘              └──────────────┘               └─────────┘      │
│                                                                             │
│  PROMPT-BASED (`type: "prompt"`):                                           │
│  ┌──────────┐   context    ┌──────────────┐    JSON      ┌─────────┐       │
│  │ Claude   │─────────────►│ Claude Haiku │─────────────►│ Decision│       │
│  │ Code     │              │ (fast LLM)   │              │         │       │
│  └──────────┘              └──────────────┘              └─────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Aspect | Functional | Prompt-Based |
|--------|------------|--------------|
| Execution | Local script | LLM API call |
| Speed | Fast (milliseconds) | Slower (seconds) |
| Logic | Deterministic rules | Context-aware reasoning |
| Use case | File protection, auto-format | Intelligent task completion checks |

### B. Exit Code Mode vs JSON Output Mode

**Exit Code Mode** (simple):
```
Exit 0  →  Approve (success)
Exit 2  →  Block (stderr shown to Claude)
Other   →  Non-blocking error
```

**JSON Output Mode** (advanced):
```json
{
  "continue": true,
  "systemMessage": "Warning shown to user",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-approved safe operation"
  }
}
```

## Common JSON Output Fields

These fields work in **all hook types** when using JSON output mode (exit code 0):

| Field | Type | Purpose |
|-------|------|---------|
| `continue` | boolean | Whether Claude should continue after hook execution (default: `true`) |
| `stopReason` | string | Message shown to user when `continue` is `false` (not shown to Claude) |
| `suppressOutput` | boolean | Hide stdout from transcript mode (default: `false`) |
| `systemMessage` | string | Message shown to the user - use for warnings, status updates, or injected context |

### systemMessage Usage

The `systemMessage` field is the primary way to communicate information from your hook to the user:

```python
# Show a warning to the user
write_output({
    "continue_": True,
    "systemMessage": "Warning: This file hasn't been saved yet"
})

# Inject context after an operation
write_output({
    "continue_": True,
    "systemMessage": "CI pipeline started. Run ID: 12345"
})
```

### Stopping Execution

To stop Claude and show a reason to the user:

```python
write_output({
    "continue_": False,
    "stopReason": "Validation failed: 3 tests are failing"
})
```

**Note**: `continue: false` takes precedence over any `decision` field.

### Hook-Specific Fields

Beyond common fields, each hook type has specialised output fields:

| Hook Type | Additional Fields |
|-----------|-------------------|
| PreToolUse | `hookSpecificOutput.permissionDecision`, `updatedInput` |
| PostToolUse | `decision`, `hookSpecificOutput.additionalContext` |
| Stop | `decision`, `reason` |
| UserPromptSubmit | `decision`, `hookSpecificOutput.additionalContext` |

See the [official Hooks documentation](https://code.claude.com/docs/en/hooks#common-json-fields) for complete field reference.

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop_validate.py",
            "timeout": 120000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/ci_watch.py",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

### Matcher Patterns

| Pattern | Matches |
|---------|---------|
| `"Bash"` | Only the Bash tool |
| `"Edit\|Write"` | Edit or Write tools |
| `"*"` | All tools |
| `"mcp__memory__.*"` | MCP memory tools |

For enterprise hook policies and sandbox settings, see the [official Settings documentation](https://code.claude.com/docs/en/settings).

## Real-World Example: Stop Hook for Validation

A Stop hook that runs linting and tests before allowing Claude to finish:

### Configuration (`.claude/settings.json`)

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop_validate.py",
            "timeout": 1200000
          }
        ]
      }
    ]
  }
}
```

### Hook Script (`.claude/hooks/stop_validate.py`)

```python
#!/usr/bin/env python3
"""Stop hook - validation pipeline.

Runs linting and tests on Stop hook events.
Exit codes: 0 = approve, 2 = block.
"""

import json
import subprocess
import sys
from pathlib import Path


def read_input() -> dict | None:
    """Read hook input from stdin."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return None


def run_validation() -> tuple[bool, str]:
    """Run validation steps. Returns (should_block, reason)."""
    steps = [
        ("Lint", ["ruff", "check", "."]),
        ("Type check", ["pyright"]),
        ("Fast tests", ["pytest", "-m", "not slow", "-x"]),
    ]

    for name, cmd in steps:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return True, f"{name} failed:\n{result.stderr or result.stdout}"

    return False, "All checks passed"


def main() -> None:
    inp = read_input()

    # Invalid input is a configuration error
    if inp is None:
        sys.stderr.write("Failed to read hook input")
        sys.exit(1)

    # Only process Stop hooks
    if inp.get("hook_event_name") != "Stop":
        sys.exit(0)

    should_block, reason = run_validation()

    if should_block:
        sys.stderr.write(reason)
        sys.exit(2)  # Block - Claude will see the reason and fix issues
    else:
        sys.exit(0)  # Approve


if __name__ == "__main__":
    main()
```

> **Advanced Pattern**: This Stop hook is a foundational pattern in the Ralf Loop methodology. For advanced patterns like graduated validation, retry limits, and intelligent completion checking, see [Part 25: The Ralf Loop - Preventing Premature Stops](25-ralf-loop.md).

## Real-World Example: PostToolUse Hook for CI Watching

A PostToolUse hook that detects `git push` and injects a reminder to watch CI:

### Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/ci_watch.py",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

### Hook Script (`.claude/hooks/ci_watch.py`)

```python
#!/usr/bin/env python3
"""PostToolUse hook - CI watching.

Detects git push and reminds Claude to watch CI.
Uses JSON output mode (never blocks).
"""

import json
import sys


def read_input() -> dict | None:
    """Read hook input from stdin."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return None


def write_output(output: dict) -> None:
    """Write JSON output, converting continue_ to continue."""
    result = dict(output)
    if "continue_" in result:
        result["continue"] = result.pop("continue_")
    json.dump(result, sys.stdout)
    sys.stdout.flush()


def main() -> None:
    inp = read_input()

    if inp is None:
        sys.exit(1)

    # Only process PostToolUse for Bash
    if inp.get("hook_event_name") != "PostToolUse":
        write_output({"continue_": True})
        sys.exit(0)

    # Check if command was git push
    tool_input = inp.get("tool_input", {})
    command = tool_input.get("command", "")

    if "git push" in command:
        write_output({
            "continue_": True,
            "systemMessage": (
                "You just pushed to remote. Please use the Task tool to "
                "spawn a subagent that watches the GitHub Actions CI run "
                "and reports back when it completes."
            ),
        })
    else:
        write_output({"continue_": True})

    sys.exit(0)


if __name__ == "__main__":
    main()
```

## Writing Your Own hook_sdk

### Why Custom vs Claude Agent SDK?

The [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk) provides hooks for **programmatic API calls**:

```python
# Agent SDK hooks - for programmatic use
async def my_hook(input_data, tool_use_id, context) -> HookJSONOutput:
    return {"permissionDecision": "allow"}

options = ClaudeAgentOptions(hooks={PreToolUse: [my_hook]})
```

But shell hooks (invoked via `.claude/settings.json`) need **stdin/stdout handling**. You have two options:

### Option 1: cchooks Library

```bash
pip install cchooks
```

```python
from cchooks import HookInput, HookOutput, run_hook

def my_hook(input: HookInput) -> HookOutput:
    if input.tool_name == "Bash":
        return HookOutput(block=True, reason="Bash blocked")
    return HookOutput()

run_hook(my_hook)
```

**Limitations**: May be outdated, less flexible for complex scenarios.

### Option 2: Custom hook_sdk (Recommended)

A minimal SDK that handles I/O for shell hooks:

```python
# hook_sdk.py
"""Shell hook I/O helpers."""

import json
import sys
from typing import Any, NoReturn


def read_input() -> dict[str, Any]:
    """Read hook input from stdin as dict."""
    return json.load(sys.stdin)


def safe_read_input() -> dict[str, Any] | None:
    """Read hook input, returning None on any error."""
    try:
        return read_input()
    except Exception:
        return None


def write_output(output: dict[str, Any]) -> None:
    """Write hook output to stdout.

    Converts Python-safe field names to JSON field names:
    - continue_ → continue (continue is a Python keyword)
    """
    result = dict(output)
    if "continue_" in result:
        result["continue"] = result.pop("continue_")
    json.dump(result, sys.stdout)
    sys.stdout.flush()


# --- Exit code helpers (for Stop hooks) ---

def exit_success() -> NoReturn:
    """Exit with code 0 (approve/continue)."""
    sys.exit(0)


def exit_block(reason: str) -> NoReturn:
    """Exit with code 2 (block), write reason to stderr."""
    sys.stderr.write(reason)
    sys.exit(2)


# --- Convenience output builders ---

def accept(*, system_message: str | None = None) -> dict[str, Any]:
    """Build output that accepts/continues."""
    result: dict[str, Any] = {"continue_": True}
    if system_message:
        result["systemMessage"] = system_message
    return result


def block_tool(reason: str, hook_event_name: str) -> dict[str, Any]:
    """Build output that blocks a tool use (for PreToolUse hooks)."""
    return {
        "continue_": True,
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }
```

### Using the Custom SDK

```python
# stop_validate.py
from hook_sdk import safe_read_input, exit_success, exit_block

def validate_body(ctx: dict) -> tuple[bool, str]:
    """Business logic - returns (should_block, reason)."""
    # ... validation logic ...
    return False, "All checks passed"

def main() -> None:
    inp = safe_read_input()
    if inp is None or inp.get("hook_event_name") != "Stop":
        exit_success()

    should_block, reason = validate_body(inp)
    if should_block:
        exit_block(reason)
    else:
        exit_success()

if __name__ == "__main__":
    main()
```

## Testing Hooks: Copy-Replace-Test Pattern

Shell hooks run via `subprocess.run()`, making them hard to mock. The solution: **copy the script to a temp folder and replace the body function with a stub**.

### The Testing Pattern

```python
# test_hook_wiring.py
"""Tests for hook I/O behavior without calling real body functions."""

import json
import re
import subprocess
from pathlib import Path
import pytest

HOOK_SCRIPT = Path(".claude/hooks/stop_validate.py")


def create_test_hook(
    hook_script: Path,
    body_fn_name: str,
    body_stub: str,
    tmp_path: Path,
) -> Path:
    """Copy hook script and replace body function with stub."""
    content = hook_script.read_text()

    # Remove import of real body function
    content = re.sub(
        r"from .+ import " + body_fn_name + r"\n",
        "",
        content,
    )

    # Inject stub before main()
    stub_code = f'''
def {body_fn_name}(ctx, **kwargs):
    """Test stub."""
{body_stub}

'''
    content = content.replace(
        "def main():",
        stub_code + "def main():",
    )

    test_script = tmp_path / hook_script.name
    test_script.write_text(content)
    return test_script


def run_hook_script(script_path: Path, stdin_data: str) -> subprocess.CompletedProcess:
    """Run hook script with stdin data."""
    return subprocess.run(
        ["python", str(script_path)],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=30.0,
    )


class TestStopHookWiring:
    """Test I/O wiring for stop hook."""

    def test_approve_exits_zero(self, tmp_path: Path) -> None:
        """Body returning (False, _) exits 0."""
        test_script = create_test_hook(
            HOOK_SCRIPT,
            "validate_body",
            '    return (False, "All checks passed")',
            tmp_path,
        )

        stdin = json.dumps({
            "hook_event_name": "Stop",
            "session_id": "test-123",
        })

        result = run_hook_script(test_script, stdin)
        assert result.returncode == 0

    def test_block_exits_two(self, tmp_path: Path) -> None:
        """Body returning (True, reason) exits 2."""
        test_script = create_test_hook(
            HOOK_SCRIPT,
            "validate_body",
            '    return (True, "Validation failed")',
            tmp_path,
        )

        stdin = json.dumps({
            "hook_event_name": "Stop",
            "session_id": "test-123",
        })

        result = run_hook_script(test_script, stdin)
        assert result.returncode == 2
        assert "Validation failed" in result.stderr

    def test_non_stop_context_exits_zero(self, tmp_path: Path) -> None:
        """Non-Stop context exits 0 without calling body."""
        test_script = create_test_hook(
            HOOK_SCRIPT,
            "validate_body",
            '    raise AssertionError("Should not be called")',
            tmp_path,
        )

        stdin = json.dumps({
            "hook_event_name": "PreToolUse",  # Not Stop
            "session_id": "test-123",
        })

        result = run_hook_script(test_script, stdin)
        assert result.returncode == 0


class TestPostToolUseHookWiring:
    """Test I/O wiring for PostToolUse hook."""

    def test_with_system_message_outputs_json(self, tmp_path: Path) -> None:
        """Body returning prompt outputs JSON with systemMessage."""
        test_script = create_test_hook(
            Path(".claude/hooks/ci_watch.py"),
            "ci_watch_body",
            '    return "Watch the CI!"',
            tmp_path,
        )

        stdin = json.dumps({
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "git push"},
        })

        result = run_hook_script(test_script, stdin)
        assert result.returncode == 0

        output = json.loads(result.stdout)
        assert output["continue"] is True
        assert "Watch the CI!" in output["systemMessage"]
```

### Why This Pattern Works

1. **Isolated I/O testing**: Test stdin parsing and exit codes without running real validation
2. **No mocking needed**: Replace at source level, not runtime
3. **Fast feedback**: Body function tests can be unit tests (no subprocess)
4. **Clear separation**: Wiring tests vs business logic tests

## Recommended Architecture

```
project/
├── .claude/
│   ├── settings.json              # Hook configuration
│   └── hooks/
│       ├── stop_validate.py       # Thin I/O wrapper
│       └── ci_watch.py            # Thin I/O wrapper
│
└── src/your_package/
    └── claude_hooks/
        ├── hook_sdk.py            # I/O helpers (reusable)
        └── bodies/
            ├── validate.py        # Validation business logic
            └── ci_watch.py        # CI watching business logic
```

**Principles**:
1. Hook scripts are **thin wrappers** - just I/O handling
2. Business logic lives in **separate body functions**
3. The `hook_sdk` provides **reusable I/O helpers**
4. Test wiring and logic **separately**

## Prompt-Based Hook Example

For intelligent, context-aware decisions, use prompt-based hooks:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude has completed the user's request. Consider: 1) Were all requested tasks done? 2) Are there errors that need fixing? 3) Did Claude say it would do something but didn't? Respond with JSON: {\"decision\": \"approve\" or \"block\", \"reason\": \"explanation\"}",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

## Summary

| Aspect | Guidance |
|--------|----------|
| Hook configuration | `.claude/settings.json` |
| Exit code mode | `0` = approve, `2` = block |
| JSON output | `{"continue": true, "systemMessage": "..."}` |
| Functional hooks | Local scripts, fast, deterministic |
| Prompt-based hooks | LLM-powered, context-aware |
| Testing | Copy-replace-test pattern for I/O |
| Architecture | Thin wrappers + separate body functions |
| `disableAllHooks` | Disable all hooks globally (settings.json) |
| `allowManagedHooksOnly` | Enterprise: only managed/SDK hooks (managed-settings.json) |
| `once: true` | Run hook only once per session |
| `timeout` | Per-command timeout (milliseconds) |

## Setup Hooks

Setup hooks run during repository initialisation via `--init`, `--init-only`, or `--maintenance` flags:

```json
{
  "hooks": {
    "Setup": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/setup.sh",
            "timeout": 300000
          }
        ]
      }
    ]
  }
}
```

```bash
# .claude/hooks/setup.sh
#!/bin/bash
# Install dependencies and prepare environment
npm install
pip install -r requirements.txt
echo '{"continue": true, "systemMessage": "Setup complete"}'
```

Use cases:
- `claude --init` — run setup on first launch in a repo
- `claude --init-only` — run setup and exit (CI/CD)
- `claude --maintenance` — run periodic maintenance tasks

## PermissionRequest Hooks

Auto-approve or deny permission requests programmatically:

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/auto_approve.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

```python
#!/usr/bin/env python3
"""Auto-approve safe operations, deny dangerous ones."""
import json, sys

inp = json.load(sys.stdin)
tool_name = inp.get("tool_name", "")
tool_input = inp.get("tool_input", {})

# Auto-approve read operations
if tool_name in ("Read", "Grep", "Glob"):
    json.dump({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Auto-approved read operation"
        }
    }, sys.stdout)
else:
    json.dump({"continue": True}, sys.stdout)
```

## Hook Configuration Options

### once: true

Run a hook only once per session (useful for setup tasks):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/load_env.py",
            "once": true
          }
        ]
      }
    ]
  }
}
```

### Per-Command Timeout

Set custom timeouts for individual hook commands:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "python .claude/hooks/slow_validation.py",
      "timeout": 600000
    }
  ]
}
```

### PreToolUse Hook Modifying Inputs

PreToolUse hooks can modify tool inputs via `updatedInput`:

```python
# Modify the command before execution
json.dump({
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "updatedInput": {
            "command": modified_command
        }
    }
}, sys.stdout)
```

### PreToolUse Hook Adding Context

Inject additional context for Claude to consider:

```python
json.dump({
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": "Note: this file was recently modified by another developer"
    }
}, sys.stdout)
```

## Agent and Skill Hooks

Hooks can be scoped to specific agents or skills via frontmatter:

```yaml
---
name: my-agent
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "python .claude/hooks/agent_bash_guard.py"
  Stop:
    - hooks:
        - type: prompt
          prompt: "Has the agent completed its specific task?"
---
```

## Common Hook Patterns

| Pattern | Hook Type | Example |
|---------|-----------|---------|
| File protection | PreToolUse | Block edits to `.env`, `package-lock.json` |
| Auto-formatting | PostToolUse | Run prettier after Write/Edit |
| Validation gate | Stop | Run tests before allowing stop |
| CI watching | PostToolUse | Detect `git push`, remind to watch CI |
| Context injection | UserPromptSubmit | Add current time, project context |
| Auto-approval | PreToolUse | Auto-approve Read on safe directories |

## Security Hooks

Hooks provide powerful security automation beyond basic permission rules. Use PreToolUse hooks to enforce security policies that run **regardless of permission mode**.

### Dangerous Command Blocking

Block risky bash commands before execution:

```python
#!/usr/bin/env python3
"""PreToolUse hook - block dangerous commands."""

import json
import re
import sys

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",           # rm -rf /
    r"rm\s+-rf\s+~",           # rm -rf ~
    r"chmod\s+777",            # chmod 777
    r"chmod\s+-R\s+777",       # chmod -R 777
    r"curl.*\|\s*bash",        # curl | bash
    r"curl.*\|\s*sh",          # curl | sh
    r"wget.*\|\s*bash",        # wget | bash
    r">\s*/dev/sd",            # > /dev/sda
    r"mkfs\.",                 # mkfs.ext4
    r"dd\s+if=.*of=/dev/",     # dd to disk
    r":\(\)\s*\{\s*:\|:",      # fork bomb
]

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PreToolUse":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    if inp.get("tool_name") != "Bash":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    command = inp.get("tool_input", {}).get("command", "")

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            json.dump({
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Blocked dangerous pattern: {pattern}"
                }
            }, sys.stdout)
            sys.exit(0)

    json.dump({"continue": True}, sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### File Protection Hook

Protect sensitive files from being read or modified:

```python
#!/usr/bin/env python3
"""PreToolUse hook - protect sensitive files."""

import json
import sys
from pathlib import Path

PROTECTED_PATTERNS = [
    ".env",
    ".env.",
    "id_rsa",
    "id_ed25519",
    ".pem",
    "credentials.json",
    "secrets/",
    ".claude/hooks/",      # Protect hooks from modification
    ".claude/settings",    # Protect settings
]

def is_protected(file_path: str) -> bool:
    """Check if file matches any protected pattern."""
    path_lower = file_path.lower()
    for pattern in PROTECTED_PATTERNS:
        if pattern in path_lower:
            return True
    return False

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PreToolUse":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    tool_name = inp.get("tool_name", "")
    tool_input = inp.get("tool_input", {})

    # Check file-related tools
    if tool_name in ("Read", "Edit", "Write"):
        file_path = tool_input.get("file_path", "")
        if is_protected(file_path):
            json.dump({
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Protected file: {file_path}"
                }
            }, sys.stdout)
            sys.exit(0)

    json.dump({"continue": True}, sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Secrets Detection Hook

Scan Claude's outputs for accidentally exposed secrets:

```python
#!/usr/bin/env python3
"""PostToolUse hook - detect secrets in output."""

import json
import re
import sys

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Token"),
    (r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----", "Private Key"),
    (r"sk-ant-[a-zA-Z0-9-]{90,}", "Anthropic API Key"),
]

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PostToolUse":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    tool_output = str(inp.get("tool_output", ""))

    for pattern, secret_type in SECRET_PATTERNS:
        if re.search(pattern, tool_output):
            json.dump({
                "continue": True,
                "systemMessage": f"⚠️ WARNING: Possible {secret_type} detected in output. "
                                 "Review before sharing or committing."
            }, sys.stdout)
            sys.exit(0)

    json.dump({"continue": True}, sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Audit Logging Hook

Log all tool usage for security review:

```python
#!/usr/bin/env python3
"""PostToolUse hook - audit logging."""

import json
import sys
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path.home() / ".claude" / "audit.log"

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PostToolUse":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    # Log the tool usage
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": inp.get("session_id"),
        "tool_name": inp.get("tool_name"),
        "tool_input": inp.get("tool_input"),
        "cwd": inp.get("cwd"),
    }

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    json.dump({"continue": True}, sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Production Safeguards Hook

Block deployment commands without explicit confirmation:

```python
#!/usr/bin/env python3
"""PreToolUse hook - production safeguards."""

import json
import re
import sys

PRODUCTION_PATTERNS = [
    r"deploy\s+prod",
    r"--production",
    r"kubectl.*--context.*prod",
    r"aws.*--profile.*prod",
    r"terraform\s+apply",
    r"pulumi\s+up",
]

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PreToolUse":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    if inp.get("tool_name") != "Bash":
        json.dump({"continue": True}, sys.stdout)
        sys.exit(0)

    command = inp.get("tool_input", {}).get("command", "")

    for pattern in PRODUCTION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            json.dump({
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason":
                        f"Production command blocked. Use explicit deployment workflow."
                }
            }, sys.stdout)
            sys.exit(0)

    json.dump({"continue": True}, sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Security Hook Configuration

Enable multiple security hooks in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/block_dangerous.py",
            "timeout": 5000
          },
          {
            "type": "command",
            "command": "python .claude/hooks/production_safeguards.py",
            "timeout": 5000
          }
        ]
      },
      {
        "matcher": "Read|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/protect_files.py",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/audit_log.py",
            "timeout": 5000
          },
          {
            "type": "command",
            "command": "python .claude/hooks/detect_secrets.py",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

### Security Hooks vs Permission Rules

| Feature | Permission Rules | Security Hooks |
|---------|------------------|----------------|
| Bypass with `--dangerously-skip-permissions` | Yes | **No** |
| Pattern matching | Glob patterns | Regex, custom logic |
| Runtime inspection | No | Yes (full context) |
| Audit logging | No | Yes |
| Dynamic decisions | No | Yes |

**Best practice**: Use both - permission rules for basic protection, hooks for advanced security logic.
