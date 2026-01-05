# Part 21: SSH Multiplexing for Remote Development

## The Use Case

Sometimes you need to work with code on a remote server but cannot or do not want to install Claude Code directly on that server. Common scenarios:

- **No installation permissions**: Restricted server access, can't install software
- **Shared servers**: Don't want to install per-user tools on shared infrastructure
- **Security policies**: Organization restricts what can be installed on production-like environments
- **Temporary access**: Working with ephemeral or short-lived remote environments
- **Resource constraints**: Remote server has limited disk space or dependencies

SSH multiplexing lets you run Claude Code **locally** while working with **remote files** efficiently.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SSH MULTIPLEXING ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐    SSH Multiplexing    ┌─────────────────────┐    │
│  │  Local Machine      │◄─────────────────────►│  Remote Server      │    │
│  │                     │   Persistent Master     │                     │    │
│  │  ┌───────────────┐  │   Connection (shared)   │  ┌──────────────┐  │    │
│  │  │ Claude Code   │──┼──────────ssh───────────┼─►│ Tools execute│  │    │
│  │  │ (runs here)   │  │   ║║║║║║║║║║║           │  │ here via ssh │  │    │
│  │  └───────────────┘  │   ║║║║║║║║║║║           │  │              │  │    │
│  │         │           │   ║║║║║║║║║║║           │  │ • bash       │  │    │
│  │         │ initiates │   ▼▼▼▼▼▼▼▼▼▼▼           │  │ • cat/read   │  │    │
│  │         │ remote    │   Multiple SSH          │  │ • grep       │  │    │
│  │         │ commands  │   sessions share        │  │ • write      │  │    │
│  │         └──────via──┼──► ONE connection       │  └──────────────┘  │    │
│  │            ssh      │                         │                     │    │
│  │                     │                         │  ┌──────────────┐  │    │
│  │                     │                         │  │ Project Files│  │    │
│  │                     │                         │  │              │  │    │
│  └─────────────────────┘                         └─────────────────────┘    │
│                                                                             │
│  Claude Code runs locally, logs in via SSH, executes tools on remote       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## SSH Multiplexing Configuration

SSH multiplexing maintains a persistent master connection that all subsequent SSH operations share, dramatically reducing latency.

Add to `~/.ssh/config`:

```
Host dev-server
    HostName your.server.com
    User username
    IdentityFile ~/.ssh/id_rsa

    # Multiplexing settings
    ControlMaster auto
    ControlPath ~/.ssh/control-%h-%p-%r
    ControlPersist 600
```

### Configuration Options Explained

| Option | Value | Description |
|--------|-------|-------------|
| `ControlMaster` | `auto` | Automatically use existing connection or create new master |
| `ControlPath` | `~/.ssh/control-%h-%p-%r` | Socket file path (host-port-user) |
| `ControlPersist` | `600` | Keep connection alive for 10 minutes (600s) after last use |

### How It Works

1. **First SSH command** creates a master connection and a socket file
2. **Subsequent commands** (file reads, bash commands, etc.) reuse that socket
3. **No repeated authentication** or handshakes
4. **Master persists** for 10 minutes after the last command finishes

### Benefits

- **Reduced latency**: No SSH handshake for each Claude Code tool call (Read, Bash, etc.)
- **Faster file operations**: Multiple file operations share one connection
- **Session persistence**: Connection survives brief network interruptions
- **Authentication once**: No repeated password/key prompts

## Using Claude Code with SSH Multiplexing

Once SSH multiplexing is configured, use Claude Code normally on your local machine:

```bash
# On local machine
cd /local/path/to/project

# Configure remote access (if using SSHFS or similar)
# OR use Claude Code's native SSH support with Bash tool

# Start Claude Code locally
claude
```

Claude Code's tools (Bash, Read, Write, etc.) will automatically benefit from the multiplexed SSH connection when accessing remote files.

### Example Workflow

```bash
# Local: Mount remote filesystem (optional, one approach)
sshfs dev-server:/path/to/project ~/mnt/remote-project
cd ~/mnt/remote-project

# Local: Start Claude Code
claude

# In Claude Code session:
# "Read the main.py file and refactor the authentication logic"
# Claude's Read tool uses SSH multiplexing → fast read
# Claude's Write tool uses SSH multiplexing → fast write
```

## VSCode Remote Development Integration

If you use VSCode Remote - SSH extension, SSH multiplexing works seamlessly:

1. **Configure SSH multiplexing** in `~/.ssh/config` (as shown above)
2. **Connect to remote** via VSCode Remote - SSH
3. **Start Claude Code locally** in a terminal
4. **VSCode serves files** from remote, Claude Code reads/writes via SSH

This combines VSCode's remote file access with Claude Code running on your local machine.

## Environment Detection

Claude Code sets `$CLAUDE_CODE_REMOTE=true` when it detects remote operations. Use this for conditional configuration:

```bash
# In a hook script
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
    # Remote-specific behavior
    echo "Running on remote server"
    # Maybe skip certain hooks that require local-only tools
fi
```

## Managing SSH Sessions

### Check Active Multiplexed Connections

```bash
# List control sockets
ls ~/.ssh/control-*

# Check specific connection status
ssh -O check dev-server
```

Output:
```
Master running (pid=12345)
```

### Manually Close Connections

```bash
# Gracefully close specific connection
ssh -O exit dev-server

# Or remove socket file (force close)
rm ~/.ssh/control-dev-server-22-username
```

### Restart Stale Connection

```bash
# Kill old master
ssh -O exit dev-server

# Next SSH command creates fresh master
ssh dev-server "echo Connection established"
```

## When to Use SSH Multiplexing vs. Direct Install

| Scenario | Approach |
|----------|----------|
| No installation permissions on remote | **SSH Multiplexing** (this article) |
| Shared production-like servers | **SSH Multiplexing** (this article) |
| Security policy restricts remote installs | **SSH Multiplexing** (this article) |
| Temporary/ephemeral remote environments | **SSH Multiplexing** (this article) |
| Your own dedicated development server | Direct install (see [Part 1: Getting Started](01-getting-started.md)) |
| Need maximum performance for remote work | Direct install (no network latency) |

## Troubleshooting

### Connection Hangs

If multiplexed connections hang:

```bash
# Kill master connection
ssh -O exit dev-server

# Remove stale socket
rm ~/.ssh/control-dev-server-*

# Reconnect (creates new master)
ssh dev-server
```

### Permission Denied on Control Socket

```bash
# Fix permissions on socket directory
chmod 700 ~/.ssh

# Ensure socket path is writable
mkdir -p ~/.ssh
```

### ControlPath Too Long

Some systems have limits on socket path length. Use a shorter path:

```
ControlPath ~/.ssh/c-%C
```

The `%C` is a hash of the connection parameters, keeping the path short while remaining unique.

### Slow File Operations Despite Multiplexing

Check that the master connection is actually established:

```bash
ssh -O check dev-server
```

If you see "No ControlPath specified" or "Control socket connect(...): No such file or directory", the multiplexing isn't working. Verify your `~/.ssh/config` has the correct `ControlMaster`, `ControlPath`, and `ControlPersist` settings.

## Summary

| Task | Command/Config |
|------|----------------|
| Enable multiplexing | `ControlMaster auto` in `~/.ssh/config` |
| Socket path | `ControlPath ~/.ssh/control-%h-%p-%r` |
| Keep alive duration | `ControlPersist 600` (seconds) |
| Check connection | `ssh -O check hostname` |
| Close connection | `ssh -O exit hostname` |
| Remote environment var | `$CLAUDE_CODE_REMOTE` |
| Best for | When you can't/won't install Claude Code on remote server |

SSH multiplexing enables efficient remote development with Claude Code running locally - no remote installation required.
