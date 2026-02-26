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
| **Playwright MCP** | Browser automation — headless Chromium or host Chrome via CDP |
| **playwright-cli** | Token-efficient browser automation via CLI skills |
| **Persistent volumes** | Bash history, `.claude/` config, and `.pixi/` cache survive rebuilds |

---

## Getting Started

### VS Code

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
and VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

1. Open this folder in VS Code
2. When prompted "Reopen in Container", click it — or run the command palette
   (`Cmd+Shift+P`) → **Dev Containers: Reopen in Container**
3. Wait for the build (first time takes a few minutes, rebuilds are cached)
4. Open the integrated terminal and run `claude`

The following VS Code extensions are auto-installed inside the container:
`anthropic.claude-code`, `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`,
`eamodio.gitlens`.

### Devcontainer CLI

Use this when you want a sandboxed Claude session without VS Code — from any
terminal, in CI, or on a remote server.

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/)
and the devcontainer CLI (`npm install -g @devcontainers/cli`).

```bash
# Build and start the container
devcontainer build --workspace-folder .
devcontainer up --workspace-folder .

# Get a shell
devcontainer exec --workspace-folder . zsh

# Or run a one-liner
devcontainer exec --workspace-folder . claude -p "explain this codebase"
```

From the shell inside the container:

```bash
claude --version        # verify Claude is available
claude                  # start an interactive session
```

### Stopping the container

```bash
docker stop $(docker ps --filter label=devcontainer.local_folder=$(pwd) -q)
```

---

## Browser Automation

The container supports three browser automation regimes, each working in two
modes (container or host). All six combinations are tested and supported:

| | **Container** (headless Chromium) | **Host** (Chrome on host via CDP) |
|---|---|---|
| **MCP** — `@playwright/mcp` tools (`browser_navigate`, `browser_snapshot`, etc.) | Headless Chromium inside the container, sandboxed by the firewall | Connects to Chrome on your machine via CDP relay |
| **playwright-cli skills** — CLI commands via Bash (`playwright-cli goto`, `playwright-cli snapshot`, etc.) | Same headless Chromium, but invoked through token-efficient CLI skills | Same CDP connection, driven by CLI skills |
| **pytest** — `pytest-playwright` browser tests in `tests/` | Launches Chromium via pixi-managed Playwright | Connects to host Chrome via CDP for visual test runs |

### Container mode (default) — headless Chromium

The container ships with Chromium baked into the Docker image. Claude controls a
headless browser inside the container — no host setup needed. The browser is
sandboxed by the firewall (it can only reach whitelisted domains).

The `.mcp.json` uses a unified launcher that auto-detects the mode:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "bash",
      "args": [".devcontainer/playwright-launcher.sh"]
    }
  }
}
```

In container mode, the launcher runs:
`npx @playwright/mcp --headless --no-sandbox --isolated --browser chromium`

### playwright-cli skills

[`playwright-cli`](https://github.com/microsoft/playwright-cli) provides
CLI-based browser automation as "skills" — more token-efficient than MCP tool
schemas because Claude uses simple Bash commands instead of JSON tool calls.

**Install the skills** (once per container):

```bash
playwright-cli install --skills
```

This generates skill files in `.claude/skills/playwright-cli/` (gitignored).
Claude Code discovers them automatically on next start. When both MCP and
skills are available, Claude may use either; to force skills-only, temporarily
rename `.mcp.json`.

### Host browser mode — Chrome on your machine via CDP

Connect Claude to Chrome running on your host machine. Use this when you need to
see what Claude is doing in a visible browser, access authenticated sessions, or
work with sites that block headless browsers.

**Step 1:** Launch Chrome with remote debugging on your host:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 --user-data-dir=%TEMP%\chrome-debug
```

`--user-data-dir` is required when using `--remote-debugging-port` — Chrome
refuses to start without it.

**Step 2:** Switch to host mode inside the container:

```bash
.devcontainer/toggle-browser.sh host
```

**Step 3:** Restart Claude Code to pick up the mode change.

**How it works:** Chrome's CDP endpoint returns WebSocket URLs pointing to
`ws://localhost/...`, but from inside the container `localhost` is the
container itself. The `cdp-relay.sh` script resolves the real WebSocket URL
from Chrome's `/json/version` endpoint and rewrites `localhost` to
`host.docker.internal:9222` before passing it to Playwright MCP.

**Verify connectivity** (from inside the container):

```bash
# Check Chrome is reachable
curl -sf -H "Host: localhost" http://host.docker.internal:9222/json/version | jq .

# Check CDP port with netcat
nc -zv host.docker.internal 9222
```

### Switching modes

```bash
.devcontainer/toggle-browser.sh              # show current mode
.devcontainer/toggle-browser.sh container    # headless Chromium (default)
.devcontainer/toggle-browser.sh host         # Chrome on host via CDP
```

The script writes `container` or `host` to the `.devcontainer/.browser-mode`
dotfile. The launcher (`playwright-launcher.sh`) reads this at startup.
You can also override the mode with `BROWSER_MODE=host` (env var wins over
the dotfile). Restart Claude Code after switching.

### Running each regime

All commands below are run **inside the container** (via `devcontainer exec`
or the VS Code integrated terminal).

#### MCP — container mode

No setup needed. Start Claude Code and ask it to use browser tools:

```bash
claude
# > Navigate to https://example.com and take a snapshot
```

Or non-interactively:

```bash
claude -p "Use the playwright MCP tool to navigate to https://api.github.com/zen \
  and tell me what the page says." --permission-mode bypassPermissions
```

#### MCP — host mode

Start Chrome with remote debugging on your host (see [Host browser mode](#host-browser-mode--chrome-on-your-machine-via-cdp)), then:

```bash
.devcontainer/toggle-browser.sh host
# Restart Claude Code, then:
claude
# > Navigate to https://example.com and take a snapshot
```

Or with a one-shot env var override (no toggle needed):

```bash
BROWSER_MODE=host claude -p "Use the playwright MCP tool to navigate to \
  https://api.github.com/zen and tell me what the page says." \
  --permission-mode bypassPermissions
```

#### playwright-cli skills — container mode

Install skills first (once), then disable MCP to ensure skills are used:

```bash
playwright-cli install --skills

# Rename .mcp.json so Claude uses skills instead of MCP tools
mv .mcp.json .mcp.json.bak

claude -p "Use playwright-cli to open a browser, navigate to \
  https://api.github.com/zen, take a snapshot, and tell me what the page says." \
  --allowedTools "Bash(playwright-cli:*)" --permission-mode bypassPermissions

# Restore MCP when done
mv .mcp.json.bak .mcp.json
```

#### playwright-cli skills — host mode

Same as above, but with `BROWSER_MODE=host` and Chrome running on the host:

```bash
mv .mcp.json .mcp.json.bak

BROWSER_MODE=host claude -p "Use playwright-cli to open a browser, navigate to \
  https://api.github.com/zen, take a snapshot, and tell me what the page says." \
  --allowedTools "Bash(playwright-cli:*)" --permission-mode bypassPermissions

mv .mcp.json.bak .mcp.json
```

#### pytest — container mode

The Panel app must be running for the tests to connect to:

```bash
# Start the Panel app in the background
pixi run panel serve src/06_pixi_devcontainer/app.py --port 5006 &

# Wait for it to be ready
for i in $(seq 1 30); do nc -z localhost 5006 2>/dev/null && break; sleep 1; done

# Run tests (container mode is the default)
pixi run test

# Stop the app
kill %1
```

#### pytest — host mode

The Panel app runs inside the container; port 5006 is forwarded to the host
(via `-p 5006:5006` in `runArgs`) so the host Chrome can reach it. You need
Chrome running with remote debugging on the host:

```bash
# Start the Panel app in the background
pixi run panel serve src/06_pixi_devcontainer/app.py --port 5006 &

# Wait for it to be ready
for i in $(seq 1 30); do nc -z localhost 5006 2>/dev/null && break; sleep 1; done

# Run tests with host browser
BROWSER_MODE=host pixi run test

# Stop the app
kill %1
```

The host Chrome navigates to `http://localhost:5006/app` — this works because
Docker forwards port 5006 from the container to the host.

---

## Network Firewall

The firewall (`init-firewall.sh`) runs at every container start and:

1. Sets the default iptables policy to **DROP** all outbound traffic
2. Resolves and whitelists only approved domains
3. Verifies the firewall works (blocked site fails, allowed site succeeds)

If Claude (or any process) tries to reach an unapproved domain, the connection
is immediately rejected at the kernel level — no process can bypass it.

### Allowed domains

| Domain | Purpose |
|--------|---------|
| GitHub (full CIDR ranges from `api.github.com/meta`) | API, web, git |
| `api.anthropic.com` | Claude API |
| `claude.ai` | Claude Code authentication |
| `sentry.io` | Error reporting |
| `statsig.anthropic.com` / `statsig.com` | Feature flags and analytics |
| `registry.npmjs.org` | npm package downloads |
| `conda.anaconda.org` / `prefix.dev` / `repo.prefix.dev` | Conda/pixi packages |
| `pypi.org` / `files.pythonhosted.org` | PyPI packages |
| VS Code marketplace / blob storage / update server | VS Code extensions |
| `host.docker.internal` (dynamic) | Container-to-host communication (CDP, etc.) |

### Customizing the allowlist

Edit the domain list in `.devcontainer/init-firewall.sh`:

```bash
for domain in \
    "registry.npmjs.org" \
    "api.anthropic.com" \
    "your-custom-domain.com" \    # <-- add your domains here
    ...
```

Rebuild the container after changes. GitHub IP ranges are fetched dynamically
from the GitHub API at each container start, so they stay current automatically.

### Verifying the firewall

```bash
curl -s --connect-timeout 3 https://example.com    # should fail (blocked)
curl -s --connect-timeout 3 https://api.github.com  # should work (allowed)
```

---

## Credentials & Volumes

### Volume mounts

Three named volumes keep state across container rebuilds:

| Volume | Mounted at | Purpose |
|--------|-----------|---------|
| `claude-code-bashhistory-*` | `/commandhistory` | Shell history |
| `claude-code-config-*` | `/home/vscode/.claude` | Claude Code config and auth |
| `*-pixi` | `/workspace/.pixi` | Pixi package cache |

Your workspace is bind-mounted at `/workspace` with `consistency=delegated` for
better filesystem performance on macOS.

### How credentials are stored

When you run `claude` and authenticate (via OAuth or API key), credentials are
written to `/home/vscode/.claude` inside the container. This path is backed by
the `claude-code-config-*` named Docker volume, so:

- Credentials **never touch your host filesystem** — they live only in the Docker volume
- Credentials **survive container rebuilds** — the named volume persists independently
- Credentials **are scoped per project** — the `${devcontainerId}` suffix makes each volume unique
- If you `docker volume rm` the volume, credentials are deleted and you must re-authenticate

Alternatively, set `ANTHROPIC_API_KEY` in the `containerEnv` section of
`devcontainer.json` to skip interactive auth entirely.

### What is `devcontainerId`?

The `*` in volume names is `${devcontainerId}` — a unique hash computed from
the workspace folder path and devcontainer config path.

| Action | ID changes? | Effect on volumes |
|--------|:-----------:|-------------------|
| Rebuild the container | No | State preserved |
| Stop and restart the container | No | State preserved |
| Edit `devcontainer.json` contents | No | State preserved |
| Update Docker or VS Code | No | State preserved |
| Move the project folder to a new path | **Yes** | New volumes — must re-authenticate |
| Rename the `.devcontainer/` config path | **Yes** | New volumes — must re-authenticate |

`devcontainer build` only builds the Docker image — it doesn't create a
container, so the ID isn't involved. The ID is computed when `devcontainer up`
creates the container.

```bash
docker volume ls | grep claude-code    # see your actual volume names
```

---

## GUI Apps in the Container

**Web apps** work out of the box — VS Code automatically forwards ports from the
container to your host, so you can open `localhost:<port>` in your host browser.

**Desktop GUI apps** (Qt, GTK, Tkinter, Electron) require extra setup:

1. **`desktop-lite` feature** — lightweight VNC desktop at `localhost:6080`:

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

---

## Architecture

```
.devcontainer/
├── Dockerfile              # Base image + pixi + Playwright + Node.js + playwright-cli + Claude Code + zsh
├── devcontainer.json       # Container config, volumes, VS Code settings
├── init-firewall.sh        # iptables firewall (runs at every container start)
├── cdp-relay.sh            # Rewrites Chrome's WebSocket URL for container→host CDP
├── playwright-launcher.sh  # Reads browser mode and launches Playwright MCP accordingly
└── toggle-browser.sh       # Writes .browser-mode dotfile to switch container/host modes
.mcp.json                   # Active Playwright MCP config (auto-discovered by Claude Code)
pyproject.toml              # Python project config with pixi workspace + test dependencies
tests/                      # Playwright browser tests
```

The container uses `--cap-add=NET_ADMIN` and `--cap-add=NET_RAW` to allow
iptables inside the container. These capabilities are scoped to the container's
network namespace — they don't affect the host.

### Build hardening (ARM64 / OrbStack)

The Dockerfile includes workarounds for Docker BuildKit networking issues that
affect ARM64 hosts and OrbStack users:

| Fix | Why |
|-----|-----|
| `Acquire::http::Pipeline-Depth "0"` | OrbStack drops pipelined HTTP connections during `docker build`, causing apt `400 Bad Request` errors |
| `curl -4 --retry 5 --retry-all-errors` on all downloads | Forces IPv4 and retries on intermittent SSL failures (`error:0A000126`) |
| `"options": ["--network=host"]` in devcontainer.json build config | Bypasses BuildKit's extra network namespace that causes TLS failures |

---

## Reference: devcontainer.json Line by Line

The devcontainer spec supports JSONC (JSON with Comments). The file is fully
commented in-source; this section provides a higher-level walkthrough.

### Container Identity and Build

| Key | Value | Why |
|-----|-------|-----|
| `name` | `"Claude Code Sandbox"` | Display name in VS Code's Remote Explorer and window title |
| `build.dockerfile` | `"Dockerfile"` | Points to our custom Dockerfile in the same directory |
| `build.options` | `["--network=host"]` | Bypasses BuildKit SSL issues on ARM64/OrbStack (see [Build hardening](#build-hardening-arm64--orbstack)) |
| `build.args.TZ` | `"${localEnv:TZ:America/Los_Angeles}"` | Propagates host timezone so container timestamps match local time. `${localEnv:TZ}` reads the host's `$TZ`; falls back to `America/Los_Angeles` |
| `build.args.PIXI_VERSION` | `"v0.63.2"` | Pins pixi version for reproducible builds |
| `build.args.GIT_DELTA_VERSION` | `"0.18.2"` | Pins git-delta version |
| `build.args.ZSH_IN_DOCKER_VERSION` | `"1.2.0"` | Pins zsh-in-docker installer version |
| `build.args.NODE_MAJOR` | `"22"` | Pins Node.js major version. Required by `@playwright/mcp` and `@playwright/cli` (pinned to 0.0.61 in the Dockerfile) |

### Features

| Key | Why |
|-----|-----|
| `ghcr.io/devcontainers/features/github-cli:1` | Installs GitHub CLI (`gh`) for PR workflows, issue management, and API calls inside the container |

### Runtime Capabilities

| Key | Value | Why |
|-----|-------|-----|
| `runArgs` | `["--cap-add=NET_ADMIN", "--cap-add=NET_RAW", "-p", "5006:5006"]` | `NET_ADMIN`/`NET_RAW`: required for `iptables` firewall rules (scoped to container namespace). `-p 5006:5006`: forwards the Panel dev-server port so host-mode browser tests can reach `http://localhost:5006` from Chrome on the host via CDP |

### VS Code Customizations

**Extensions:**

| Extension | Purpose |
|-----------|---------|
| `anthropic.claude-code` | Claude Code extension for VS Code |
| `dbaeumer.vscode-eslint` | ESLint linting integration |
| `esbenp.prettier-vscode` | Prettier code formatter (set as default) |
| `eamodio.gitlens` | Git blame, history, and annotations |

**Settings:**

| Setting | Value | Why |
|---------|-------|-----|
| `editor.formatOnSave` | `true` | Auto-format on every save |
| `editor.defaultFormatter` | `esbenp.prettier-vscode` | Prettier handles all formatting |
| `editor.codeActionsOnSave` | `source.fixAll.eslint: "explicit"` | Run ESLint auto-fix on save; `"explicit"` means it only runs when explicitly triggered (not on every keystroke) |
| `terminal.integrated.defaultProfile.linux` | `"zsh"` | Default to zsh (where Powerlevel10k and completions are configured) |

### User and Volumes

| Key | Value | Why |
|-----|-------|-----|
| `remoteUser` | `"vscode"` | Run as non-root. The base image creates this user with sudo access |
| `mounts[0]` | `claude-code-bashhistory-${devcontainerId}` → `/commandhistory` | Shell history persists across rebuilds. Uses `${devcontainerId}` for per-project isolation |
| `mounts[1]` | `claude-code-config-${devcontainerId}` → `/home/vscode/.claude` | Claude Code config and auth tokens. Credentials live only in this volume, never on the host |
| `mounts[2]` | `${localWorkspaceFolderBasename}-pixi` → `${containerWorkspaceFolder}/.pixi` | Pixi package cache. Uses the human-readable workspace folder name instead of a hash |

### Environment Variables

| Key | Value | Why |
|-----|-------|-----|
| `CLAUDE_CONFIG_DIR` | `/home/vscode/.claude` | Tells Claude Code where its config lives (must match the volume mount) |
| `POWERLEVEL9K_DISABLE_GITSTATUS` | `"true"` | Disables Powerlevel10k's background `gitstatus` process — it can be slow on Docker volumes and large repos |

### Workspace Mount

| Key | Value | Why |
|-----|-------|-----|
| `workspaceMount` | `source=${localWorkspaceFolder},target=/workspace,...,consistency=delegated` | Bind-mounts the host project into the container. `consistency=delegated` lets the container's view lag slightly behind the host, improving macOS filesystem performance |
| `workspaceFolder` | `"/workspace"` | Where VS Code opens — matches the bind mount target above |

### Lifecycle Commands

| Key | Value | When | Why |
|-----|-------|------|-----|
| `postCreateCommand` | `pixi install` | Once, after first creation | Reconciles the volume-mounted `.pixi` with the image-baked environment. No `sudo chown` needed — `.pixi` is already vscode-owned from the image |
| `postStartCommand` | `sudo /usr/local/bin/init-firewall.sh` | Every container start | Configures the iptables firewall with the domain allowlist |
| `waitFor` | `"postStartCommand"` | Before user gets terminal | Ensures the firewall is fully active before the user can run commands. Without this, there's a window where the network is unrestricted |

---

## Reference: Dockerfile Line by Line

Each instruction in the Dockerfile is commented in-source. This section provides
the full rationale for every block.

### Base Image

```dockerfile
FROM mcr.microsoft.com/devcontainers/base:jammy
```

Microsoft's devcontainer base image built on **Ubuntu 22.04 LTS (Jammy)**. It
comes pre-configured with: a `vscode` user, sudo, git, curl, wget, zsh, gnupg2,
less, procps, man-db, and unzip. Using this base means we don't need to set up
user accounts or basic tooling.

### Timezone

```dockerfile
ARG TZ
ENV TZ="$TZ"
```

The `TZ` build arg is passed from `devcontainer.json`'s `build.args.TZ`, which
reads the host's `$TZ` environment variable. Setting `ENV TZ` propagates it into
the running container so logs, git commits, and `date` output use local time.

### Apt Pipeline Fix

```dockerfile
RUN echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/99-orbstack-fix
```

Disables HTTP pipelining for apt. OrbStack's virtual network drops pipelined
connections during `docker build`, causing `400 Bad Request` errors. This must
come before any `apt-get` command.

### System Packages

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
  fzf iptables ipset iproute2 dnsutils aggregate jq nano vim netcat-openbsd
```

| Package | Why |
|---------|-----|
| `fzf` | Fuzzy finder for shell history search (`Ctrl+R`) and file navigation |
| `iptables` | Kernel-level firewall — used by `init-firewall.sh` to DROP/ACCEPT traffic |
| `ipset` | Efficient IP set matching — stores the allowed CIDR ranges as a set that iptables matches against in a single rule |
| `iproute2` | Provides the `ip route` command to detect the Docker host network gateway |
| `dnsutils` | Provides the `dig` command to resolve domain names to IP addresses for the firewall |
| `aggregate` | Merges overlapping CIDR ranges — compacts GitHub's large IP list into fewer, non-overlapping ranges |
| `jq` | JSON parser — extracts IP ranges from the GitHub API `/meta` endpoint |
| `nano` | Terminal editor — set as `$EDITOR` so Claude Code uses it for file operations |
| `vim` | Alternative terminal editor for users who prefer it |
| `netcat-openbsd` | Network utility (`nc`) for testing TCP connectivity (e.g., CDP port checks) |

`--no-install-recommends` keeps the image lean by skipping suggested packages.
The `apt-get clean && rm -rf /var/lib/apt/lists/*` cleanup reduces the layer size.

### Pixi

```dockerfile
ARG PIXI_VERSION=v0.63.2
RUN curl -4 -fsSL --compressed --retry 5 --retry-all-errors \
    -o /usr/local/bin/pixi \
    "https://...pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi info
```

Direct binary download — no package manager needed. The `musl` build is used for
portability across container base images (musl binaries don't depend on specific
glibc versions). `pixi info` is a smoke test that verifies the binary runs.
`-4` forces IPv4 and `--retry` handles intermittent SSL failures on ARM64.

### git-delta

```dockerfile
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  curl -4 -fsSL --retry 5 --retry-all-errors \
    -o "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" \
    "https://...git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_...deb" && rm "git-delta_...deb"
```

Installs the pre-built `.deb` package (handles dependencies automatically).
`dpkg --print-architecture` returns `amd64` or `arm64` for multi-arch support,
so the same Dockerfile works on Intel and Apple Silicon hosts.

### Node.js

```dockerfile
ARG NODE_MAJOR=22
RUN curl -4 -fsSL --retry 5 --retry-all-errors \
    https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
  && apt-get install -y --no-install-recommends nodejs
```

Node.js is installed from NodeSource for two npm packages:
`@playwright/mcp` (the MCP server for Claude Code browser automation) and
`@playwright/cli` (token-efficient browser skills), both pinned to **0.0.61**
so they use **chromium-1208** — the same revision as pixi's stable playwright
1.58.0. This lets all three share a single Chromium binary. The Python
`playwright-mcp` package (v0.1.0) hardcodes `headless=False`, so we use the
mature npm version.

### Playwright + Chromium

```dockerfile
COPY pyproject.toml pixi.lock* /workspace/
ENV PLAYWRIGHT_BROWSERS_PATH=/home/vscode/.cache/ms-playwright
RUN cd /workspace && pixi install && \
    chown -R vscode:vscode /workspace/.pixi

RUN npm install -g @playwright/mcp@0.0.61 @playwright/cli@0.0.61

RUN .pixi/envs/default/bin/playwright install --with-deps chromium && \
    chown -R vscode:vscode /home/vscode/.cache
```

Pixi manages the Python environment including `pytest-playwright` (which pulls in
the `playwright` Python library). `pixi install` reads `pyproject.toml` and
creates the environment at `/workspace/.pixi`.

All three Playwright consumers — pixi's `playwright` 1.58.0, `@playwright/mcp`
0.0.61, and `@playwright/cli` 0.0.61 — use the same **chromium-1208** revision.
By pinning the npm packages to 0.0.61, a single `playwright install --with-deps
chromium` satisfies all of them. This downloads one Chromium binary (~300 MB)
and runs `apt-get` once for system dependencies (fonts, shared libs, xvfb),
instead of the two separate installs that unpinned versions would require.

The `conftest.py` browser fixture uses `playwright.chromium.launch(headless=True)`
which auto-resolves the matching Chromium for the pixi-installed version.

The `chown` fixes ownership of `.cache` and `.pixi` (created as root during
build) so the `vscode` user owns them when Docker copies to empty volumes on
first mount.

### Claude Code CLI

```dockerfile
USER vscode
RUN curl -4 -fsSL --retry 5 --retry-all-errors https://claude.ai/install.sh | bash
ENV PATH="/home/vscode/.local/bin:$PATH"
```

Installed as `vscode` user via the official install script. The binary lands at
`/home/vscode/.local/bin/claude`, which is not affected by any volume mount.

### Bash History Persistence

```dockerfile
RUN mkdir /commandhistory && \
  touch /commandhistory/.bash_history && \
  chown -R vscode /commandhistory
```

Creates a directory at a **volume-mountable path outside `$HOME`**. The
`devcontainer.json` mounts a named volume here, so shell history survives
container rebuilds.

### Shell and Editor

```dockerfile
ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano
```

- `SHELL` — default shell for new terminal sessions (matches our zsh theme setup)
- `EDITOR` — used by Claude Code and git for editing operations
- `VISUAL` — used by programs that want a full-screen editor

### zsh-in-docker

```dockerfile
RUN sh -c "$(curl -4 -fsSL --retry 5 --retry-all-errors .../zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a 'eval "$(pixi completion -s zsh)"' \
  -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  -x
```

| Flag | Effect |
|------|--------|
| `-p git` | Enable Oh My Zsh git plugin (aliases: `gst`, `gco`, `gd`, etc.) |
| `-p fzf` | Enable fzf plugin (`Ctrl+R` history search, `Ctrl+T` file finder) |
| `-a 'eval "$(pixi completion -s zsh)"'` | Append pixi tab completions to `.zshrc` |
| `-a "export PROMPT_COMMAND=... && export HISTFILE=..."` | Flush history after each command and store in the mounted volume |
| `-x` | Skip automatic Powerlevel10k theme configuration (we customize colors below) |

### Powerlevel10k Color Customization

Injects `POWERLEVEL9K_*` color variables into `.zshrc` **before** the
`source $ZSH/oh-my-zsh.sh` line. Uses Python instead of sed to avoid
shell newline-escaping issues across platforms.

**Color codes** (256-color palette):

| Code | Color | Used for |
|------|-------|----------|
| 108 | Moss green | User segment background, OK status background |
| 151 | Sage green | Directory background, modified VCS background |
| 158 | Mint | Clean VCS background, untracked VCS background |
| 0 | Black | All foreground text (high contrast on light backgrounds) |
| 231 | White | Error status foreground |
| 131 | Dusty rose | Error status background |
| 238 | Dark gray | Shortened directory segment foreground |

### Firewall Script Setup

```dockerfile
COPY init-firewall.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/init-firewall.sh && \
  echo "vscode ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/vscode-firewall && \
  echo "vscode ALL=(root) NOPASSWD: /bin/chown" > /etc/sudoers.d/vscode-chown && \
  chmod 0440 /etc/sudoers.d/vscode-firewall /etc/sudoers.d/vscode-chown
USER vscode
```

1. `COPY` places the script in the image
2. `USER root` switches to root for permission changes
3. Two separate `sudoers.d` files grant **passwordless sudo for only**:
   - `/usr/local/bin/init-firewall.sh` — the firewall initialization script
   - `/bin/chown` — needed by `postCreateCommand` to fix `.pixi` volume ownership
4. `chmod 0440` — required by sudo; sudoers files must not be world-readable
5. `USER vscode` — the final image layer runs as non-root

---

## Reference: init-firewall.sh Line by Line

The firewall script runs at every container start (`postStartCommand`). It
configures iptables to block all outbound traffic except explicitly allowed
domains.

### Script Safety

```bash
set -euo pipefail  # Exit on error, undefined vars, and pipeline failures
IFS=$'\n\t'        # Stricter word splitting (no space splitting)
```

`set -euo pipefail` ensures the script fails fast on any error — critical for a
security script where partial execution could leave the network open. `IFS`
prevents accidental word-splitting bugs.

### Step 1: Save Docker DNS Rules

```bash
DOCKER_DNS_RULES=$(iptables-save -t nat | grep "127\.0\.0\.11" || true)
```

Docker uses an internal DNS resolver at `127.0.0.11` with NAT rules to route DNS
queries. These rules are saved **before** flushing because we need to restore
them — without Docker DNS, the container can't resolve any domain names.

### Step 2: Flush Existing Rules

```bash
iptables -F      # Flush filter table (INPUT/OUTPUT/FORWARD chains)
iptables -X      # Delete user-defined chains
iptables -t nat -F / -X    # Flush NAT table
iptables -t mangle -F / -X  # Flush mangle table
ipset destroy allowed-domains 2>/dev/null || true
```

Clean slate. Every rule from previous runs is cleared so the script is
idempotent — running it twice produces the same result.

### Step 3: Restore Docker DNS

```bash
if [ -n "$DOCKER_DNS_RULES" ]; then
    iptables -t nat -N DOCKER_OUTPUT 2>/dev/null || true
    iptables -t nat -N DOCKER_POSTROUTING 2>/dev/null || true
    echo "$DOCKER_DNS_RULES" | xargs -L 1 iptables -t nat
fi
```

Re-creates the Docker NAT chains and replays the saved rules. Without this,
`dig` and `curl` would fail because the container couldn't resolve DNS.

### Step 4: Base Allow Rules

```bash
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT    # Outbound DNS
iptables -A INPUT -p udp --sport 53 -j ACCEPT     # DNS responses
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT     # Outbound SSH
iptables -A INPUT -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT  # SSH responses
iptables -A INPUT -i lo -j ACCEPT                  # Localhost in
iptables -A OUTPUT -o lo -j ACCEPT                 # Localhost out
```

These rules are added **before** the DROP policy:
- **DNS (port 53)** — required for the script itself to resolve domains
- **SSH (port 22)** — allows git-over-SSH operations
- **Localhost** — processes inside the container need to talk to each other (e.g., VS Code server ↔ extensions)

### Step 5: Create ipset

```bash
ipset create allowed-domains hash:net
```

Creates an ipset of type `hash:net` — a hash table that supports CIDR notation.
This is more efficient than individual iptables rules per IP: a single iptables
rule can match against the entire set.

### Step 6: Fetch and Add GitHub IP Ranges

```bash
gh_ranges=$(curl -s https://api.github.com/meta)
echo "$gh_ranges" | jq -r '(.web + .api + .git)[]' | aggregate -q
```

1. Fetches GitHub's published IP ranges from their API
2. Extracts the `web`, `api`, and `git` CIDR blocks with `jq`
3. Pipes through `aggregate -q` to merge overlapping ranges (fewer rules)
4. Validates each CIDR against a regex before adding to the ipset
5. Exits with an error if the API response is missing required fields

### Step 7: Resolve and Add Individual Domains

```bash
for domain in "registry.npmjs.org" "api.anthropic.com" ...; do
    ips=$(dig +noall +answer A "$domain" | awk '$4 == "A" {print $5}')
    ipset add allowed-domains "$ip" -exist
done
```

For domains that don't publish CIDR ranges, the script resolves their A records
with `dig` and adds each IP individually. The `-exist` flag prevents errors if
an IP was already added (e.g., two domains resolving to the same CDN IP).

Each IP is validated against a regex to guard against DNS poisoning or
malformed responses.

### Step 8: Detect Host Network

```bash
HOST_IP=$(ip route | grep default | cut -d" " -f3)
HOST_NETWORK=$(echo "$HOST_IP" | sed "s/\.[0-9]*$/.0\/24/")
iptables -A INPUT -s "$HOST_NETWORK" -j ACCEPT
iptables -A OUTPUT -d "$HOST_NETWORK" -j ACCEPT
```

Detects the Docker host's gateway IP from the default route, then allows the
entire `/24` subnet. This is necessary for:
- VS Code server ↔ container communication
- Docker port forwarding
- Host ↔ container file sync

### Step 9: Allow host.docker.internal

```bash
DOCKER_HOST_IP=$(getent hosts host.docker.internal 2>/dev/null | awk '{print $1}' || true)
if [ -n "$DOCKER_HOST_IP" ]; then
    iptables -A INPUT -s "$DOCKER_HOST_IP" -j ACCEPT
    iptables -A OUTPUT -d "$DOCKER_HOST_IP" -j ACCEPT
fi
```

On OrbStack, `host.docker.internal` resolves to an IP (e.g., `0.250.250.254`)
outside the default gateway's `/24` subnet, so Step 8's rule doesn't cover it.
This step dynamically resolves the IP and adds it. Needed for CDP browser
automation and any other container-to-host communication. Re-resolved at every
container start, so no rebuild is needed when the host IP changes.

### Step 10: Default DROP Policy

```bash
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
```

**The security boundary.** After all allow rules are in place, set the default
policy to DROP on all chains. Any packet that doesn't match an allow rule is
silently dropped. This is set after the allow rules (not before) to avoid
locking the script out of the network mid-execution.

### Step 11: Stateful Connection Tracking

```bash
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

Allows return traffic for already-established connections. Without this, even
allowed connections would fail because the response packets wouldn't be
permitted.

### Step 12: ipset Match Rule

```bash
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
```

The actual allow rule: any outbound packet whose destination IP is in the
`allowed-domains` ipset is accepted. This single rule replaces what would
otherwise be dozens of individual iptables rules.

### Step 13: REJECT Catch-All

```bash
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited
```

Explicitly **REJECT** (not DROP) all remaining outbound traffic. The difference:
- **REJECT** sends an ICMP "admin prohibited" response → the client gets an
  immediate error (connection refused)
- **DROP** silently discards → the client waits for a timeout (30+ seconds)

REJECT is used here because immediate feedback is better for developer
experience — you instantly know a connection was blocked rather than waiting.

### Step 14: Verification

```bash
curl --connect-timeout 5 https://example.com      # Should fail (blocked)
curl --connect-timeout 5 https://api.github.com/zen  # Should succeed (allowed)
```

Two smoke tests verify the firewall is working correctly:
1. `example.com` should be **blocked** (it's not in the allowlist)
2. `api.github.com` should be **reachable** (GitHub IPs were added)

If either test produces an unexpected result, the script exits with an error
code, and `postStartCommand` fails — preventing the user from getting a terminal
with a misconfigured firewall.

---

## Further Reading

- [Native Sandbox vs Dev Containers](../../docs/36-sandbox-vs-devcontainers.md) — Decision guide comparing Claude Code's `/sandbox` (OS-level isolation) with dev containers (Docker-based isolation), including the Docker root problem and when to use each approach
- [Browser Automation in Containers and Beyond](../../docs/37-browser-automation.md) — Comprehensive survey of browser automation MCP tools, why Playwright MCP is the only option with production-ready container support, and alternatives for host-only workflows
