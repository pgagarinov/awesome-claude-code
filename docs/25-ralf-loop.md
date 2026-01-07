# Part 25: The Ralf Loop - Preventing Premature Stops

## What is the Ralf Loop?

The Ralf loop (also called "Ralph loop" or "RALF" - **R**un, **A**nalyze, **L**earn, **F**ix) is a pattern that prevents Claude Code from stopping work before truly completing tasks. It uses Stop hooks to block Claude's attempt to finish, forcing it to verify completion criteria before being allowed to stop.

The concept originated from [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code), which implements an external loop that repeatedly invokes Claude Code until all tasks are genuinely complete.

## The Problem: Premature Stops

Claude Code sometimes stops before finishing work:

```
┌─────────────────────────────────────────────────────────────┐
│ WITHOUT RALF LOOP                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ User: "Implement login and run all tests"                  │
│   ↓                                                         │
│ Claude: *implements login*                                  │
│   ↓                                                         │
│ Claude: "I've implemented the login feature."               │
│   ↓                                                         │
│ [STOPS - forgot to run tests!]                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ WITH RALF LOOP                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ User: "Implement login and run all tests"                  │
│   ↓                                                         │
│ Claude: *implements login*                                  │
│   ↓                                                         │
│ Claude: "I've implemented the login feature."               │
│   ↓                                                         │
│ Stop Hook: "Tests haven't run. Block."                      │
│   ↓                                                         │
│ Claude: *runs tests, finds 3 failures*                      │
│   ↓                                                         │
│ Claude: *fixes failures*                                    │
│   ↓                                                         │
│ Stop Hook: "All tests pass. Approve."                       │
│   ↓                                                         │
│ [STOPS - task actually complete]                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Two Approaches

### Approach 1: Validation-Based Stop Hook

Block Claude until concrete validation passes (tests, linting, builds).

**Pros**:
- Deterministic, objective criteria
- Fast (no LLM call)
- Catches real issues (broken tests, lint errors)

**Cons**:
- Can't detect "forgot to do X" if X passes validation
- Requires defining what "done" means programmatically
- May block on unrelated validation failures

> **Note**: This approach uses Stop hooks. For a detailed guide on hook syntax, configuration, and best practices, see [Part 22: Claude Code Hooks](22-hooks.md).

**Example** (`.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop_validate.py",
            "timeout": 300000
          }
        ]
      }
    ]
  }
}
```

**Hook implementation** (`.claude/hooks/stop_validate.py`):

```python
#!/usr/bin/env python3
"""Stop hook - validation pipeline.

Blocks Claude from stopping until validation passes.
Exit codes: 0 = approve, 2 = block.
"""

import json
import subprocess
import sys


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
        ("Tests", ["pytest", "-x"]),
    ]

    errors = []
    for name, cmd in steps:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"{name} failed:\n{result.stderr or result.stdout}")

    if errors:
        return True, "\n\n".join(errors)

    return False, "All validation passed"


def main() -> None:
    inp = read_input()

    if inp is None:
        sys.stderr.write("Failed to read hook input\n")
        sys.exit(1)

    # Only process Stop hooks
    if inp.get("hook_event_name") != "Stop":
        sys.exit(0)

    should_block, reason = run_validation()

    if should_block:
        sys.stderr.write(reason)
        sys.exit(2)  # Block - Claude sees reason and fixes
    else:
        sys.exit(0)  # Approve


if __name__ == "__main__":
    main()
```

### Approach 2: Prompt-Based Stop Hook

Use an LLM to intelligently evaluate if Claude truly finished the task.

**Pros**:
- Context-aware reasoning about task completion
- Can detect "forgot to do X" even if validation passes
- Flexible - understands intent, not just rules

**Cons**:
- Slower (requires LLM API call)
- Non-deterministic
- Costs money per stop
- May hallucinate or misunderstand

**Example** (`.claude/settings.json`):

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the conversation and determine if Claude has TRULY completed the user's request. Ask yourself:\n\n1. Did Claude do everything the user asked?\n2. Did Claude say it would do something but then forget?\n3. Are there failing tests or errors that need fixing?\n4. Did Claude run all required validation (tests, builds, etc)?\n\nIf ANY of these is problematic, respond with:\n{\"decision\": \"block\", \"reason\": \"Specific issue here\"}\n\nOnly approve if you're confident the task is 100% complete:\n{\"decision\": \"approve\", \"reason\": \"All tasks completed\"}",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

### Approach 3: Hybrid (Recommended)

Combine both: fast validation first, then prompt-based reasoning.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/stop_validate.py",
            "timeout": 300000
          },
          {
            "type": "prompt",
            "prompt": "The validation passed. Now check if Claude completed ALL user requests, not just the ones that have validation. Did Claude forget anything? Only approve if genuinely complete.",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

## Advanced: Graduated Validation with Retry Limit

Real implementations often use tiered validation that gets more thorough on each retry, with a maximum retry limit to prevent infinite loops.

```python
#!/usr/bin/env python3
"""Stop hook - graduated validation with retry limit."""

import json
import os
import subprocess
import sys
from pathlib import Path


RETRY_MARKER = ".claude_stop_retries"
MAX_RETRIES = 3


def read_input() -> dict | None:
    try:
        return json.load(sys.stdin)
    except Exception:
        return None


def get_retry_count() -> int:
    """Track how many times we've blocked this stop attempt."""
    marker = Path(RETRY_MARKER)
    if not marker.exists():
        return 0
    try:
        return int(marker.read_text())
    except Exception:
        return 0


def increment_retry_count() -> None:
    """Increment retry counter."""
    count = get_retry_count() + 1
    Path(RETRY_MARKER).write_text(str(count))


def reset_retry_count() -> None:
    """Reset retry counter on successful validation."""
    Path(RETRY_MARKER).unlink(missing_ok=True)


def run_tier(tier: int) -> tuple[bool, str]:
    """Run validation tier. Returns (should_block, reason).

    Tier 0: Lint only (fast)
    Tier 1: Lint + type check
    Tier 2: Lint + type check + fast tests
    Tier 3: Full test suite
    """
    steps = []

    if tier >= 0:
        steps.append(("Lint", ["ruff", "check", "."]))

    if tier >= 1:
        steps.append(("Type check", ["pyright"]))

    if tier >= 2:
        steps.append(("Fast tests", ["pytest", "-m", "not slow", "-x"]))

    if tier >= 3:
        steps.append(("Full tests", ["pytest"]))

    for name, cmd in steps:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return True, f"{name} failed:\n{result.stderr or result.stdout}"

    return False, f"Tier {tier} validation passed"


def main() -> None:
    inp = read_input()

    if inp is None:
        sys.stderr.write("Failed to read hook input\n")
        sys.exit(1)

    if inp.get("hook_event_name") != "Stop":
        sys.exit(0)

    retry_count = get_retry_count()

    # Force approve after max retries (circuit breaker)
    if retry_count >= MAX_RETRIES:
        reset_retry_count()
        print(f"Max retries ({MAX_RETRIES}) reached. Approving to prevent infinite loop.")
        sys.exit(0)

    # Run increasingly thorough validation
    should_block, reason = run_tier(retry_count)

    if should_block:
        increment_retry_count()
        sys.stderr.write(f"[Retry {retry_count + 1}/{MAX_RETRIES}]\n\n{reason}")
        sys.exit(2)
    else:
        reset_retry_count()
        sys.exit(0)


if __name__ == "__main__":
    main()
```

## When to Use the Ralf Loop

| Use Case | Recommended Approach |
|----------|---------------------|
| Long-running features with tests | Validation-based |
| Quick fixes where validation is overkill | Prompt-based |
| Critical production changes | Hybrid (validation + prompt) |
| Exploratory/research tasks | None (let Claude stop naturally) |
| Working with flaky tests | Graduated with retry limit |

## Debugging Ralf Loops

### Problem: Infinite Loop

**Symptom**: Hook blocks forever, Claude can't fix the issue.

**Solution**: Add circuit breaker (max retries) and better error messages:

```python
if retry_count >= MAX_RETRIES:
    sys.stderr.write(
        f"Still failing after {MAX_RETRIES} attempts. "
        "Issue may require manual intervention. Approving stop."
    )
    sys.exit(0)
```

### Problem: Hook Too Strict

**Symptom**: Claude can't stop even when task is complete.

**Solution**: Make validation context-aware. Only validate what's relevant:

```python
def should_run_tests(context: dict) -> bool:
    """Only run tests if code changed."""
    last_message = context.get("last_message", "")
    return any(tool in last_message for tool in ["Edit", "Write", "NotebookEdit"])
```

### Problem: Hook Too Lenient

**Symptom**: Claude stops with broken tests or incomplete work.

**Solution**: Add explicit checks for common issues:

```python
def check_todos_completed(context: dict) -> tuple[bool, str]:
    """Verify no pending TODOs."""
    result = subprocess.run(
        ["grep", "-r", "TODO:", "src/"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True, f"Pending TODOs:\n{result.stdout}"
    return False, ""
```

## The External Ralph Loop

The original [ralph-claude-code](https://github.com/frankbria/ralph-claude-code) implements the loop **externally** - a wrapper script that repeatedly invokes `claude` until a completion criteria is met:

```bash
while true; do
  claude --prompt "Continue working on tasks in @fix_plan.md"

  # Check if truly done
  if all_tasks_complete; then
    break
  fi

  # Safety: prevent infinite loops
  if [ $iterations -gt 50 ]; then
    echo "Max iterations reached"
    break
  fi
done
```

This approach:
- Works without Stop hooks
- Gives more control over the loop logic
- Can track state across invocations
- Useful for fully autonomous workflows

**Internal Stop hooks** (what this article focuses on) keep the loop inside a single Claude Code session, which is simpler and more interactive.

## Summary

| Aspect | Guidance |
|--------|----------|
| **What** | Pattern to prevent Claude from stopping prematurely |
| **How** | Stop hook that blocks until completion criteria met |
| **Types** | Validation-based (fast, deterministic) or prompt-based (smart, slow) |
| **Best practice** | Hybrid: validation + prompt reasoning |
| **Safety** | Always include circuit breaker (max retries) |
| **When to use** | Long tasks with clear completion criteria |
| **When to avoid** | Exploratory work, research, simple fixes |

> **Hardening**: To prevent Claude from circumventing the Ralf Loop by modifying hook scripts or test configuration, use permission deny rules. See [Part 23: Permission Settings & Hardening](23-permissions.md).

## Real-World Example

A production-ready Ralf loop for a Python web service:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "pixi run python .claude/hooks/stop_validate.py",
            "timeout": 600000
          }
        ]
      }
    ]
  }
}
```

```python
# .claude/hooks/stop_validate.py
"""Production-grade stop validation with graduated tiers."""

import json
import subprocess
import sys
from pathlib import Path

RETRY_MARKER = ".claude/.stop_retries"
MAX_RETRIES = 4

# Validation tiers - gets more thorough each retry
TIERS = [
    [("Lint", ["ruff", "check", "."])],
    [("Lint", ["ruff", "check", "."]),
     ("Type check", ["pyright"])],
    [("Lint", ["ruff", "check", "."]),
     ("Type check", ["pyright"]),
     ("Unit tests", ["pytest", "-m", "not integration", "-x"])],
    [("Lint", ["ruff", "check", "."]),
     ("Type check", ["pyright"]),
     ("All tests", ["pytest"])],
]


def get_retry_count() -> int:
    marker = Path(RETRY_MARKER)
    marker.parent.mkdir(exist_ok=True)
    if not marker.exists():
        return 0
    try:
        return int(marker.read_text())
    except Exception:
        return 0


def set_retry_count(count: int) -> None:
    Path(RETRY_MARKER).write_text(str(count))


def run_tier(tier_idx: int) -> tuple[bool, str]:
    """Run validation tier."""
    tier = TIERS[min(tier_idx, len(TIERS) - 1)]

    for name, cmd in tier:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        if result.returncode != 0:
            output = result.stderr or result.stdout
            return True, f"{name} failed:\n{output[:1000]}"  # Truncate long output

    return False, "Validation passed"


def main() -> None:
    try:
        inp = json.load(sys.stdin)
    except Exception:
        sys.stderr.write("Failed to read hook input\n")
        sys.exit(1)

    if inp.get("hook_event_name") != "Stop":
        sys.exit(0)

    retry_count = get_retry_count()

    # Circuit breaker
    if retry_count >= MAX_RETRIES:
        set_retry_count(0)
        print(f"\nValidation retries exhausted ({MAX_RETRIES}). Approving stop.")
        sys.exit(0)

    # Run validation
    should_block, reason = run_tier(retry_count)

    if should_block:
        set_retry_count(retry_count + 1)
        sys.stderr.write(
            f"\n🔄 Validation retry {retry_count + 1}/{MAX_RETRIES}\n\n{reason}\n"
        )
        sys.exit(2)
    else:
        set_retry_count(0)
        sys.exit(0)


if __name__ == "__main__":
    main()
```

This ensures Claude Code doesn't stop until code is clean, typed, and tested - perfect for maintaining high quality standards in production codebases.
