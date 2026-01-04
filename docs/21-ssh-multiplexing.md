# Part 21: SSH Multiplexing for Remote Development

## The Challenge

When working with remote servers, you often want Claude Code's assistance without installing it directly on the server. SSH multiplexing and proper remote configuration can provide smoother remote development experiences.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      REMOTE DEVELOPMENT OPTIONS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Option A: Full Remote Install                                              │
│  ┌──────────┐      SSH      ┌───────────────────────────────────┐          │
│  │  Local   │──────────────►│  Remote Server                    │          │
│  │  Terminal│               │  ┌─────────────────────────────┐  │          │
│  └──────────┘               │  │  Claude Code (full install) │  │          │
│                             │  └─────────────────────────────┘  │          │
│                             └───────────────────────────────────┘          │
│                                                                             │
│  Option B: SSH Multiplexing + Local Claude                                  │
│  ┌─────────────────────┐    SSH     ┌─────────────────────┐                │
│  │  Local Machine      │◄──mux────►│  Remote Server      │                │
│  │  ┌───────────────┐  │   ││       │  (files only)       │                │
│  │  │ Claude Code   │  │   ││       └─────────────────────┘                │
│  │  └───────────────┘  │   ││                                              │
│  └─────────────────────┘   ││                                              │
│       Persistent connection ▼▼                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## SSH Multiplexing Configuration

SSH multiplexing maintains a persistent connection, reducing latency for subsequent commands:

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
| `ControlPersist` | `600` | Keep connection alive for 10 minutes after last use |

### Benefits

- **Reduced latency**: No SSH handshake for each command
- **Faster file operations**: Multiple commands share one connection
- **Session persistence**: Connection survives brief network interruptions

## Approach 1: Full Remote Install (Recommended)

For the best experience, install Claude Code directly on the remote server:

```bash
# SSH to remote server
ssh dev-server

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Authenticate
claude auth

# Start working
cd /path/to/project
claude
```

**Benefits**:
- Full feature support
- Native file access speeds
- No network latency for file reads
- Hooks and plugins work normally

## Approach 2: JetBrains Remote Development

If you use JetBrains IDEs with Remote Development:

1. **Install plugin on the remote host** (not the local client)
2. Connect to remote via JetBrains Gateway
3. In the remote IDE, open Settings → Plugins (Host)
4. Install Claude Code plugin
5. Run Claude from the remote terminal

```bash
# In remote terminal within JetBrains
cd /project
claude
```

## Approach 3: Dev Containers

For consistent, reproducible remote environments, use Claude Code's official devcontainer:

```json
// .devcontainer/devcontainer.json
{
  "name": "Claude Code Development",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    }
  },
  "postCreateCommand": "npm install -g @anthropic-ai/claude-code",
  "remoteUser": "vscode",
  "customizations": {
    "vscode": {
      "extensions": [
        "anthropic.claude-code"
      ]
    }
  }
}
```

**Features**:
- Pre-configured Node.js 20
- Security firewall with allowlisted domains
- Works on macOS, Windows, and Linux
- VS Code Remote - Containers integration

## Environment Detection

Claude Code sets `$CLAUDE_CODE_REMOTE=true` when running in a remote context. Use this for conditional configuration:

```bash
# In a hook script
if [ "$CLAUDE_CODE_REMOTE" = "true" ]; then
    # Remote-specific behavior
    echo "Running on remote server"
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

### Manually Close Connections

```bash
# Close specific connection
ssh -O exit dev-server

# Or remove socket file
rm ~/.ssh/control-dev-server-22-username
```

## Comparison: When to Use Each Approach

| Scenario | Recommended Approach |
|----------|----------------------|
| Daily development on remote | Full remote install |
| Occasional remote access | SSH multiplexing + local |
| Team with shared environments | Dev containers |
| JetBrains Remote Development | Plugin on remote host |
| Restricted server (no npm) | SSH multiplexing + local |

## Troubleshooting

### Connection Hangs

If multiplexed connections hang:

```bash
# Kill master connection
ssh -O exit dev-server

# Remove stale socket
rm ~/.ssh/control-dev-server-*

# Reconnect
ssh dev-server
```

### Permission Denied on Control Socket

```bash
# Fix permissions on socket directory
chmod 700 ~/.ssh
```

### ControlPath Too Long

Use a shorter path:

```
ControlPath ~/.ssh/c-%C
```

The `%C` is a hash of the connection parameters, keeping the path short.

## Summary

| Task | Command/Config |
|------|----------------|
| Enable multiplexing | `ControlMaster auto` in `~/.ssh/config` |
| Socket path | `ControlPath ~/.ssh/control-%h-%p-%r` |
| Keep alive duration | `ControlPersist 600` (seconds) |
| Check connection | `ssh -O check hostname` |
| Close connection | `ssh -O exit hostname` |
| Remote environment var | `$CLAUDE_CODE_REMOTE` |
