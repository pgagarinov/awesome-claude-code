# Part 30: Sandboxing

## What is Sandboxing?

Sandboxing provides OS-level security isolation for Claude Code, restricting filesystem access and network connectivity to protect your system from unintended modifications.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SANDBOXING OVERVIEW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  WITHOUT SANDBOX                      WITH SANDBOX                          │
│  ────────────────────                 ──────────────────────                │
│                                                                             │
│  Claude Code                          Claude Code                           │
│      │                                    │                                 │
│      ├── Full filesystem access           ├── Project directory only        │
│      ├── All network access               ├── No network (or limited)       │
│      ├── System modifications             ├── Read-only system files        │
│      └── External command execution       └── Restricted command scope      │
│                                                                             │
│  ⚠️  Higher risk                        ✓ Reduced attack surface            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

Enable sandboxing with the `/sandbox` command:

```bash
> /sandbox on
```

Check current sandbox status:

```bash
> /sandbox
```

Disable sandboxing:

```bash
> /sandbox off
```

## Sandbox Modes

| Mode | Description |
|------|-------------|
| `off` | No sandboxing (default) |
| `on` | Enable sandboxing with OS-level isolation |
| `permissive` | Sandbox enabled but allows more operations |

## How It Works

### Linux (bubblewrap)

On Linux, Claude Code uses [bubblewrap](https://github.com/containers/bubblewrap) for containerized isolation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LINUX SANDBOX (BUBBLEWRAP)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Filesystem Restrictions:                                                   │
│  • Project directory: Read/Write                                            │
│  • Home directory: Read-only (selected paths)                               │
│  • System paths (/usr, /lib): Read-only                                     │
│  • Sensitive paths (/etc/shadow): Blocked                                   │
│                                                                             │
│  Network Restrictions:                                                      │
│  • Outbound connections: Blocked by default                                 │
│  • Local services: Accessible                                               │
│                                                                             │
│  Process Restrictions:                                                      │
│  • New namespaces: User, mount, network, PID                                │
│  • Privilege escalation: Blocked                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Install bubblewrap:**
```bash
# Ubuntu/Debian
sudo apt install bubblewrap

# Fedora/RHEL
sudo dnf install bubblewrap

# Arch Linux
sudo pacman -S bubblewrap
```

### macOS (Seatbelt)

On macOS, Claude Code uses the built-in Seatbelt sandboxing framework:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MACOS SANDBOX (SEATBELT)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Filesystem Restrictions:                                                   │
│  • Project directory: Read/Write                                            │
│  • /tmp: Read/Write (for temporary files)                                   │
│  • Home directory: Limited access                                           │
│  • System directories: Read-only                                            │
│                                                                             │
│  Network Restrictions:                                                      │
│  • Outbound connections: Blocked                                            │
│  • DNS resolution: Allowed (for error messages)                             │
│                                                                             │
│  Mach Services:                                                             │
│  • Limited to required system services                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

Seatbelt is built into macOS - no installation required.

### Windows

Windows sandboxing uses filesystem virtualization and restricted tokens. Limited compared to Linux/macOS implementations.

## Configuration

### Settings File

Configure sandboxing in `.claude/settings.json`:

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "strict",
    "allowedPaths": [
      "/tmp",
      "~/.npm",
      "~/.cache"
    ],
    "allowNetwork": false
  }
}
```

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `enabled` | boolean | Enable/disable sandboxing |
| `mode` | string | `strict` or `permissive` |
| `allowedPaths` | array | Additional paths with read/write access |
| `allowNetwork` | boolean | Allow outbound network connections |

## Security Benefits

### Protection Against Prompt Injection

Sandboxing limits damage from prompt injection attacks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT INJECTION MITIGATION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Attack Scenario:                                                           │
│  Malicious content in file tricks Claude into running harmful commands      │
│                                                                             │
│  WITHOUT Sandbox:                                                           │
│  • rm -rf / could delete system files                                       │
│  • curl | bash could download malware                                       │
│  • cat ~/.ssh/id_rsa could exfiltrate secrets                               │
│                                                                             │
│  WITH Sandbox:                                                              │
│  • Filesystem writes restricted to project                                  │
│  • Network access blocked                                                   │
│  • Sensitive files inaccessible                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Defense in Depth

Sandboxing works alongside other security measures:

| Layer | Protection |
|-------|------------|
| Permission system | Tool-level approval/denial |
| Security hooks | Custom validation logic |
| Sandboxing | OS-level isolation |
| Git safety | Prevents destructive git operations |

## Limitations

### What Sandboxing Cannot Prevent

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SANDBOX LIMITATIONS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚠️  Domain Fronting                                                        │
│      Requests to allowed domains could proxy to malicious endpoints         │
│                                                                             │
│  ⚠️  Unix Sockets                                                           │
│      Local socket communication may bypass network restrictions             │
│                                                                             │
│  ⚠️  Allowed Path Abuse                                                     │
│      Writable paths could be used for data staging                          │
│                                                                             │
│  ⚠️  Time-of-Check-Time-of-Use (TOCTOU)                                     │
│      Race conditions between validation and execution                       │
│                                                                             │
│  ⚠️  Container Escapes                                                      │
│      Kernel vulnerabilities could allow sandbox bypass (rare)               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Performance Considerations

- Sandbox initialization adds slight startup overhead
- Filesystem operations may be marginally slower
- Network-dependent operations will fail if network blocked

## Use Cases

### High-Security Development

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "strict",
    "allowNetwork": false,
    "allowedPaths": []
  }
}
```

Use when:
- Working with untrusted codebases
- Reviewing third-party code
- Handling sensitive data

### Development with External Dependencies

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "permissive",
    "allowNetwork": true,
    "allowedPaths": [
      "~/.npm",
      "~/.cache/pip",
      "~/.cargo"
    ]
  }
}
```

Use when:
- Installing packages
- Running builds that fetch dependencies
- Testing API integrations

### Disabled (Default)

```json
{
  "sandbox": {
    "enabled": false
  }
}
```

Use when:
- Full system access required
- Trusted codebase
- Complex build processes

## Combining with Other Security Features

### Sandbox + Permission Rules

```json
{
  "sandbox": {
    "enabled": true
  },
  "permissions": {
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl*|*bash)",
      "Edit(~/.ssh/*)"
    ]
  }
}
```

### Sandbox + Security Hooks

Use hooks for validation that runs before sandbox enforcement:

```python
#!/usr/bin/env python3
# Pre-tool validation before sandbox

import json
import sys

event = json.load(sys.stdin)

if event["tool"] == "Bash":
    command = event["input"].get("command", "")
    # Log all commands for audit
    with open("/var/log/claude-audit.log", "a") as f:
        f.write(f"{command}\n")

print(json.dumps({"continue": True}))
```

## Troubleshooting

### "Sandbox not available" Error

**Linux:**
```bash
# Check if bubblewrap is installed
which bwrap

# Install if missing
sudo apt install bubblewrap
```

**macOS:**
Seatbelt should be available by default. If issues persist:
```bash
# Check sandbox-exec availability
which sandbox-exec
```

### Operation Blocked by Sandbox

If legitimate operations are blocked:

1. Check if path needs to be in `allowedPaths`
2. Consider `permissive` mode for development
3. Temporarily disable with `/sandbox off`

### Network Operations Failing

```bash
# Enable network access for current session
> /sandbox permissive

# Or configure in settings
{
  "sandbox": {
    "enabled": true,
    "allowNetwork": true
  }
}
```

## Best Practices

1. **Start strict, loosen as needed**: Begin with strict mode, add allowed paths only when necessary

2. **Document exceptions**: Note why paths are added to `allowedPaths`

3. **Layer security**: Don't rely on sandboxing alone - use with permissions and hooks

4. **Test sandbox configuration**: Verify expected operations work before relying on restrictions

5. **Monitor for bypasses**: Watch for unexpected behavior that might indicate sandbox issues

## Official Documentation

- [Sandboxing Guide](https://code.claude.com/docs/en/sandboxing)
