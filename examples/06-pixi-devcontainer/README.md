# Sandboxed Claude Code Devcontainer

**Problem:** Running Claude Code on your host machine gives it broad network and
filesystem access. For security-sensitive work, you want Claude contained in an
environment where it can only reach approved services.

**Solution:** A devcontainer with an iptables firewall that whitelists only the
domains Claude needs (GitHub, npm, PyPI, Anthropic API, etc.) and blocks
everything else.

## What's Inside

| Component | Purpose |
|-----------|---------|
| **iptables firewall** | Blocks all outbound traffic except whitelisted domains |
| **pixi** | Fast conda/PyPI package manager (replaces conda + pip) |
| **Claude Code CLI** | Pre-installed and on `$PATH` |
| **GitHub CLI (`gh`)** | For PR workflows inside the container |
| **git-delta** | Better diffs in the terminal |
| **zsh + Powerlevel10k** | Themed shell with git status, completions |
| **Persistent volumes** | Bash history, `.claude/` config, and `.pixi/` cache survive rebuilds |

## Network Firewall

The firewall (`init-firewall.sh`) runs at container start and:

1. Sets the default iptables policy to **DROP** all outbound traffic
2. Resolves and whitelists only these domains:

```
GitHub          (API, web, git — full CIDR ranges from api.github.com/meta)
api.anthropic.com
claude.ai
statsig.anthropic.com / statsig.com
registry.npmjs.org
conda.anaconda.org / prefix.dev / repo.prefix.dev
pypi.org / files.pythonhosted.org
VS Code marketplace / blob storage / update server
```

3. Verifies the firewall works:
   - Confirms `https://example.com` is **blocked**
   - Confirms `https://api.github.com` is **reachable**

If Claude (or any process) tries to reach an unapproved domain, the connection
is immediately rejected. This is enforced at the kernel level — no process in the
container can bypass it.

## Option A: VS Code

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Steps

1. Open this folder in VS Code
2. When prompted "Reopen in Container", click it — or run the command palette
   (`Cmd+Shift+P`) and select **Dev Containers: Reopen in Container**
3. Wait for the build (first time takes a few minutes, rebuilds are cached)
4. The container opens with zsh, Claude Code on `$PATH`, and the firewall active

The `devcontainer.json` auto-installs these VS Code extensions inside the container:

- `anthropic.claude-code` — Claude Code extension
- `dbaeumer.vscode-eslint` — ESLint
- `esbenp.prettier-vscode` — Prettier (set as default formatter)
- `eamodio.gitlens` — GitLens

Open the integrated terminal and run `claude` to start a session.

## Option B: Devcontainer CLI

Use this when you want a sandboxed Claude session without VS Code — from any
terminal, in CI, or on a remote server.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- devcontainer CLI: `npm install -g @devcontainers/cli`

### Steps

```bash
# 1. Build the container
devcontainer build --workspace-folder .

# 2. Start the container and get a shell
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . zsh
```

From the shell inside the container:

```bash
# Verify Claude is available
claude --version

# Verify the firewall is active
curl -s --connect-timeout 3 https://example.com    # should fail
curl -s --connect-timeout 3 https://api.github.com  # should work

# Start a Claude session
claude
```

### One-liner for headless use

Run a single Claude prompt in the sandbox and exit:

```bash
devcontainer exec --workspace-folder . claude -p "explain this codebase"
```

### Stopping the container

```bash
# Find the container ID
docker ps --filter label=devcontainer.local_folder=$(pwd) -q

# Stop it
docker stop $(docker ps --filter label=devcontainer.local_folder=$(pwd) -q)
```

## Customizing the Allowlist

Edit the domain list in `.devcontainer/init-firewall.sh` to add or remove
allowed domains:

```bash
for domain in \
    "registry.npmjs.org" \
    "api.anthropic.com" \
    "your-custom-domain.com" \    # <-- add your domains here
    ...
```

Rebuild the container after changes. GitHub IP ranges are fetched dynamically
from the GitHub API at each container start, so they stay current automatically.

## Architecture

```
.devcontainer/
├── Dockerfile          # Base image + pixi + git-delta + Claude Code + zsh
├── devcontainer.json   # Container config, volumes, VS Code settings
└── init-firewall.sh    # iptables firewall (runs at container start)
```

The container uses `--cap-add=NET_ADMIN` and `--cap-add=NET_RAW` to allow
iptables inside the container. These capabilities are scoped to the container's
network namespace — they don't affect the host.

### Volume Mounts

Three named volumes keep state across rebuilds:

| Volume | Mounted at | Purpose |
|--------|-----------|---------|
| `claude-code-bashhistory-*` | `/commandhistory` | Shell history |
| `claude-code-config-*` | `/home/vscode/.claude` | Claude Code config and auth |
| `*-pixi` | `/workspace/.pixi` | Pixi package cache |

Your workspace is bind-mounted at `/workspace` with `consistency=delegated` for
better filesystem performance on macOS.

### How Claude Credentials Are Stored

When you run `claude` and authenticate (via OAuth or API key), credentials are
written to `/home/vscode/.claude` inside the container. This path is backed by
the `claude-code-config-*` named Docker volume, so:

- Credentials **never touch your host filesystem** — they live only in the Docker volume
- Credentials **survive container rebuilds** — the named volume persists independently
- Credentials **are scoped per project** — the `${devcontainerId}` suffix makes each volume unique
- If you `docker volume rm` the volume, credentials are deleted and you must re-authenticate

Alternatively, you can skip the interactive auth flow entirely by setting
`ANTHROPIC_API_KEY` in the `containerEnv` section of `devcontainer.json`.

### What Is `devcontainerId`?

The `*` in volume names like `claude-code-config-*` is `${devcontainerId}` — a
built-in variable from the devcontainer spec. It's a unique hash automatically
computed from:

- The **workspace folder path** on your host machine
- The **devcontainer config file path**

This means:

| Action | ID changes? | Effect on volumes |
|--------|:-----------:|-------------------|
| Rebuild the container | No | State preserved |
| Stop and restart the container | No | State preserved |
| Edit `devcontainer.json` contents | No | State preserved |
| Update Docker or VS Code | No | State preserved |
| Move the project folder to a new path | **Yes** | New volumes — must re-authenticate |
| Rename the `.devcontainer/` config path | **Yes** | New volumes — must re-authenticate |

Note: `devcontainer build` only builds the Docker image — it doesn't create a
container, so the devcontainer ID isn't involved at all. The ID is computed
when `devcontainer up` creates the container.

To see your actual volume names:

```bash
docker volume ls | grep claude-code
```

## GUI Apps in the Container

**Web apps** work out of the box — VS Code automatically forwards ports from the
container to your host, so you can open `localhost:<port>` in your host browser.
Port forwarding uses the local network, which the firewall allows.

**Desktop GUI apps** (Qt, GTK, Tkinter, Electron) require extra setup since
containers don't have a display server. Options:

1. **`desktop-lite` feature** — adds a lightweight VNC desktop accessible via
   browser at `localhost:6080`:

   ```json
   "features": {
       "ghcr.io/devcontainers/features/desktop-lite:1": {}
   }
   ```

2. **X11 forwarding** (Linux hosts only) — mount the host X11 socket:

   ```json
   "mounts": [
       "source=/tmp/.X11-unix,target=/tmp/.X11-unix,type=bind"
   ],
   "containerEnv": {
       "DISPLAY": "${localEnv:DISPLAY}"
   }
   ```

If your GUI app needs external network access beyond the allowlist, add the
required domains to `init-firewall.sh`.
