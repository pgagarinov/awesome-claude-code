# Part 24: Permission Settings & Hardening

## Why Protect Files from Claude?

When using Stop hooks for validation (Ralf Loop, [Part 14](14-ralf-loop.md)), Claude might try to "cheat" by:
- Modifying hook scripts to skip validation
- Editing `pyproject.toml` to disable tests
- Changing test files to make them pass

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE CIRCUMVENTION PROBLEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Stop Hook: "3 tests failing. Fix them."                                    │
│      ↓                                                                      │
│  Claude (thinking): "I could just... delete the tests"                      │
│      ↓                                                                      │
│  Without protection: Claude modifies test config                            │
│      ↓                                                                      │
│  Stop Hook: "All tests pass!" (because no tests run)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Permission Deny Rules

Configure in `.claude/settings.json` or `.claude/settings.local.json`:

```json
{
  "permissions": {
    "deny": [
      "Edit(.claude/hooks/**)",
      "Write(.claude/hooks/**)",
      "Edit(pyproject.toml)",
      "Edit(pytest.ini)",
      "Edit(.claude/settings.json)"
    ]
  }
}
```

Files matching deny patterns are **invisible to Claude Code** - it cannot read, edit, or even see they exist.

## Hardening the Ralf Loop

To prevent Claude from circumventing validation hooks, protect your validation infrastructure:

| File/Directory | Purpose |
|---------------|---------|
| `.claude/hooks/**` | Hook scripts |
| `.claude/settings.json` | Hook configuration |
| `pyproject.toml` | Test configuration (pytest, coverage) |
| `pytest.ini`, `setup.cfg` | Additional test config |
| `tox.ini` | Test matrix configuration |

### Complete Hardening Configuration

```json
{
  "permissions": {
    "deny": [
      "Edit(.claude/**)",
      "Write(.claude/**)",
      "Edit(pyproject.toml)",
      "Edit(pytest.ini)",
      "Edit(setup.cfg)",
      "Edit(tox.ini)",
      "Edit(Makefile)"
    ]
  }
}
```

> **Note**: This prevents Claude from modifying your hooks and test configuration. If you need Claude to help you edit these files, temporarily remove the relevant deny rules.

## Protecting Sensitive Files

Beyond hardening validation, deny rules protect secrets from accidental exposure:

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./config/credentials.json)",
      "Read(./**/secret*)"
    ]
  }
}
```

## Settings Precedence

Settings are evaluated in this order (highest precedence first):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SETTINGS PRECEDENCE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Managed settings (Enterprise)       ← Cannot be overridden              │
│      ↓                                                                      │
│  2. Command line arguments              ← --dangerously-skip-permissions    │
│      ↓                                                                      │
│  3. Local project settings              ← .claude/settings.local.json       │
│      ↓                                                                      │
│  4. Shared project settings             ← .claude/settings.json             │
│      ↓                                                                      │
│  5. User settings                       ← ~/.claude/settings.json           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Disabling --dangerously-skip-permissions

For enterprise environments, you can completely disable the bypass permissions mode:

```json
{
  "permissions": {
    "disableBypassPermissionsMode": "disable"
  }
}
```

This setting:
- Must be configured in `managed-settings.json` (system-level)
- Blocks the `--dangerously-skip-permissions` flag entirely
- Cannot be overridden by users
- Ensures deny rules are always enforced

## Wildcard Permission Patterns

Permission rules support wildcard patterns for flexible matching:

### Bash Wildcards

```json
{
  "permissions": {
    "allow": [
      "Bash(npm *)",
      "Bash(* install)",
      "Bash(git * main)",
      "Bash(*)"
    ]
  }
}
```

`Bash(*)` matches all bash commands and is equivalent to `Bash` without arguments.

### MCP Tool Wildcards

Allow or deny all tools from a specific MCP server:

```json
{
  "permissions": {
    "allow": [
      "mcp__playwright__*"
    ],
    "deny": [
      "mcp__untrusted_server__*"
    ]
  }
}
```

### Enterprise MCP Allowlist/Denylist

Enterprises can control which MCP servers are permitted via managed settings:

```json
{
  "mcpAllowlist": ["playwright", "github"],
  "mcpDenylist": ["untrusted-server"]
}
```

Configure in `managed-settings.json` at the system level.

### Disabling Specific Tools for Custom Agents

Use `disallowedTools` in agent definitions to block tools:

```yaml
---
name: read-only-agent
disallowedTools: Edit, Write, Bash
---
```

### allowUnsandboxedCommands

Disable the `dangerouslyDisableSandbox` escape hatch at policy level:

```json
{
  "sandbox": {
    "allowUnsandboxedCommands": false
  }
}
```

### Searching Permission Rules

Use `/permissions` and press `/` to filter rules by tool name for quick navigation.

## Using Hooks as an Alternative

PreToolUse hooks run **regardless of permission mode**, providing another layer of protection:

```python
#!/usr/bin/env python3
"""PreToolUse hook - protect validation files."""

import json
import sys
from pathlib import Path

PROTECTED_PATTERNS = [
    ".claude/hooks/",
    ".claude/settings",
    "pyproject.toml",
    "pytest.ini",
]

def main():
    inp = json.load(sys.stdin)

    if inp.get("hook_event_name") != "PreToolUse":
        sys.exit(0)

    tool_name = inp.get("tool_name", "")
    tool_input = inp.get("tool_input", {})

    # Check Edit and Write tools
    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "")
        for pattern in PROTECTED_PATTERNS:
            if pattern in file_path:
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

See [Part 13: Claude Code Hooks](13-hooks.md) for hook configuration details.

## Summary

| Method | Protects Against | Requires |
|--------|------------------|----------|
| `permissions.deny` | Normal operations | Settings file |
| Managed settings | All operations including bypass | Enterprise/admin access |
| PreToolUse hooks | All operations | Hook script |

## Official Documentation

- [Permission Settings](https://code.claude.com/docs/en/settings#permission-settings)
- [Settings Reference](https://docs.anthropic.com/en/docs/claude-code/settings)
