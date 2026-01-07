# Part 26: Dev Containers with Claude Code

## What are Dev Containers?

Dev Containers let you define your development environment as code - a Docker container with all tools, dependencies, and configurations your project needs. VSCode's Remote - Containers extension connects to these containers, giving you a consistent, reproducible development environment.

With Claude Code installed in a dev container, you get:
- **Reproducible environments**: Same setup for every team member
- **Isolated dependencies**: No conflicts with your local machine
- **Version-controlled tooling**: Dev environment lives in your repo
- **Onboarding simplicity**: New developers run one command

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DEV CONTAINER ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐              ┌─────────────────────────┐          │
│  │  Local Machine      │              │  Docker Container       │          │
│  │                     │              │                         │          │
│  │  ┌──────────────┐   │              │  ┌──────────────────┐  │          │
│  │  │ VSCode       │   │  connects    │  │  Claude Code     │  │          │
│  │  │ (UI only)    │◄──┼──────────────┼─►│  (running here)  │  │          │
│  │  └──────────────┘   │              │  └──────────────────┘  │          │
│  │                     │              │                         │          │
│  └─────────────────────┘              │  ┌──────────────────┐  │          │
│                                       │  │ Project Files    │  │          │
│                                       │  │ Dependencies     │  │          │
│                                       │  │ Tools (node, py) │  │          │
│                                       │  └──────────────────┘  │          │
│                                       │                         │          │
│                                       └─────────────────────────┘          │
│                                                                             │
│  Benefits: Consistent environments, isolated from local machine             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Basic Dev Container Configuration

Create `.devcontainer/devcontainer.json` in your project root:

```json
{
  "name": "Claude Code Development",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    }
  },
  "postCreateCommand": "curl -fsSL https://claude.ai/install.sh | bash",
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

### Configuration Breakdown

| Field | Purpose |
|-------|---------|
| `name` | Display name in VSCode |
| `image` | Base Docker image (Ubuntu, Alpine, etc.) |
| `features` | Pre-built feature installers (Node, Python, Git, etc.) |
| `postCreateCommand` | Commands to run after container creation (install Claude Code) |
| `remoteUser` | User account inside container |
| `customizations.vscode.extensions` | VSCode extensions to auto-install |

## Python Project Example

For a Python project with specific dependencies:

```json
{
  "name": "Python + Claude Code",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {}
  },
  "postCreateCommand": "pip install -r requirements.txt && curl -fsSL https://claude.ai/install.sh | bash",
  "remoteUser": "vscode",
  "customizations": {
    "vscode": {
      "extensions": [
        "anthropic.claude-code",
        "ms-python.python",
        "ms-python.vscode-pylance"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python"
      }
    }
  }
}
```

## Node.js Project Example

For a Node.js/TypeScript project:

```json
{
  "name": "Node.js + Claude Code",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20",
  "postCreateCommand": "npm install && curl -fsSL https://claude.ai/install.sh | bash",
  "remoteUser": "node",
  "customizations": {
    "vscode": {
      "extensions": [
        "anthropic.claude-code",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ]
    }
  },
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/node/.ssh,type=bind,consistency=cached"
  ]
}
```

**Note**: The `mounts` field shares your SSH keys with the container, useful for git operations.

## Custom Dockerfile

For more control, use a custom Dockerfile:

```dockerfile
# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Claude Code
RUN curl -fsSL https://claude.ai/install.sh | bash

# Set working directory
WORKDIR /workspace
```

Reference it from `devcontainer.json`:

```json
{
  "name": "Custom Environment",
  "build": {
    "dockerfile": "Dockerfile"
  },
  "remoteUser": "vscode",
  "customizations": {
    "vscode": {
      "extensions": ["anthropic.claude-code"]
    }
  }
}
```

## Using the Dev Container

### First Time Setup

1. **Install VSCode extensions**:
   - Remote - Containers (`ms-vscode-remote.remote-containers`)
   - Docker Desktop (or Docker Engine on Linux)

2. **Open project in container**:
   - Open project folder in VSCode
   - `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
   - Select "Remote-Containers: Reopen in Container"
   - VSCode builds the container (first time takes a few minutes)

3. **Authenticate Claude Code**:
   ```bash
   # Inside container terminal
   claude auth
   ```

4. **Start working**:
   ```bash
   claude
   ```

### Rebuilding the Container

After changing `devcontainer.json`:

- `Cmd+Shift+P` → "Remote-Containers: Rebuild Container"

This recreates the container with new configuration.

## Sharing Credentials with Container

### SSH Keys

Share SSH keys for git operations:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached"
  ]
}
```

### Environment Variables

Pass environment variables from host:

```json
{
  "remoteEnv": {
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}",
    "DATABASE_URL": "${localEnv:DATABASE_URL}"
  }
}
```

### Git Configuration

Share git config:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.gitconfig,target=/home/vscode/.gitconfig,type=bind,consistency=cached"
  ]
}
```

## Pre-commit Hooks in Containers

If using pre-commit hooks, ensure they work in the container:

```json
{
  "postCreateCommand": "pip install pre-commit && pre-commit install && curl -fsSL https://claude.ai/install.sh | bash"
}
```

## Performance Considerations

### Volume Mounts for Large Projects

For better performance with large codebases, use named volumes:

```json
{
  "workspaceMount": "source=my-project-volume,target=/workspace,type=volume",
  "workspaceFolder": "/workspace"
}
```

This keeps files in a Docker volume instead of mounting from host filesystem.

### Skip Unnecessary Files

Add `.dockerignore` to exclude files from container:

```
node_modules/
.git/
.vscode/
*.log
.DS_Store
```

## Team Onboarding Workflow

1. **Developer clones repo**:
   ```bash
   git clone https://github.com/company/project
   cd project
   ```

2. **Opens in VSCode**:
   - VSCode detects `.devcontainer/`
   - Prompts: "Reopen in Container?"
   - Click "Reopen in Container"

3. **Container builds automatically**:
   - Installs dependencies
   - Installs Claude Code
   - Developer is ready to work

No manual setup needed!

## When to Use Dev Containers

| Use Case | Recommendation |
|----------|----------------|
| Team needs consistent environments | ✅ **Use dev containers** |
| Onboarding new developers frequently | ✅ **Use dev containers** |
| Complex dependency setups | ✅ **Use dev containers** |
| Testing on different OS/environments | ✅ **Use dev containers** |
| Solo developer, simple project | ⚠️  Optional (local install may be simpler) |
| Need maximum performance | ⚠️  Consider local install (no virtualization overhead) |
| Cannot install Docker | ❌ Use local install or SSH multiplexing ([Part 21](21-ssh-multiplexing.md)) |

## Troubleshooting

### Container Build Fails

Check the build output in VSCode's terminal:
- `View` → `Terminal`
- Look for error messages during `docker build`

Common issues:
- Network errors: Check internet connection
- Permission errors: Ensure Docker has proper permissions
- Port conflicts: Another container using the same port

### Claude Code Not Found in Container

Verify installation in `postCreateCommand`:

```bash
# Inside container terminal
which claude
# Should output: /usr/local/bin/claude (or similar)

# If not found, manually install:
curl -fsSL https://claude.ai/install.sh | bash
```

### Authentication Issues

If `claude auth` fails in container:

1. Check network connectivity:
   ```bash
   curl -I https://claude.ai
   ```

2. Ensure container has internet access (some corporate networks block container networking)

### Files Not Syncing

If changes don't appear:
- Check if VSCode is connected (bottom-left should show "Dev Container: [name]")
- Rebuild container: `Cmd+Shift+P` → "Rebuild Container"

## Summary

| Aspect | Details |
|--------|---------|
| **Configuration file** | `.devcontainer/devcontainer.json` |
| **Install Claude Code** | `postCreateCommand: "curl -fsSL https://claude.ai/install.sh \| bash"` |
| **Open in container** | `Cmd+Shift+P` → "Reopen in Container" |
| **Rebuild** | `Cmd+Shift+P` → "Rebuild Container" |
| **Best for** | Teams, consistent environments, complex dependencies |
| **Requires** | Docker Desktop, VSCode Remote - Containers extension |

Dev containers provide reproducible, isolated development environments with Claude Code pre-installed, perfect for teams and complex projects.
