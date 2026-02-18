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

## Reference: devcontainer.json Line by Line

The devcontainer spec supports JSONC (JSON with Comments). The file is fully
commented in-source; this section provides a higher-level walkthrough.

### Container Identity and Build

| Key | Value | Why |
|-----|-------|-----|
| `name` | `"Claude Code Sandbox"` | Display name in VS Code's Remote Explorer and window title |
| `build.dockerfile` | `"Dockerfile"` | Points to our custom Dockerfile in the same directory |
| `build.args.TZ` | `"${localEnv:TZ:America/Los_Angeles}"` | Propagates host timezone so container timestamps match local time. `${localEnv:TZ}` reads the host's `$TZ`; falls back to `America/Los_Angeles` |
| `build.args.PIXI_VERSION` | `"v0.63.2"` | Pins pixi version for reproducible builds |
| `build.args.GIT_DELTA_VERSION` | `"0.18.2"` | Pins git-delta version |
| `build.args.ZSH_IN_DOCKER_VERSION` | `"1.2.0"` | Pins zsh-in-docker installer version |

### Features

| Key | Why |
|-----|-----|
| `ghcr.io/devcontainers/features/github-cli:1` | Installs GitHub CLI (`gh`) for PR workflows, issue management, and API calls inside the container |

### Runtime Capabilities

| Key | Value | Why |
|-----|-------|-----|
| `runArgs` | `["--cap-add=NET_ADMIN", "--cap-add=NET_RAW"]` | Required for `iptables`. `NET_ADMIN` allows modifying network config (firewall rules, ipset, routing). `NET_RAW` allows raw sockets (needed by iptables for packet matching). Both are scoped to the container's network namespace — they don't affect the host |

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
| `postCreateCommand` | `sudo chown vscode .pixi && pixi install` | Once, after first creation | The `.pixi` volume is root-owned initially; `chown` fixes permissions, then `pixi install` sets up the environment |
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

### System Packages

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
  fzf iptables ipset iproute2 dnsutils aggregate jq nano vim
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

`--no-install-recommends` keeps the image lean by skipping suggested packages.
The `apt-get clean && rm -rf /var/lib/apt/lists/*` cleanup reduces the layer size.

### Pixi

```dockerfile
ARG PIXI_VERSION=v0.63.2
RUN curl -L -o /usr/local/bin/pixi -fsSL --compressed \
    "https://...pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi info
```

Direct binary download — no package manager needed. The `musl` build is used for
portability across container base images (musl binaries don't depend on specific
glibc versions). `pixi info` is a smoke test that verifies the binary runs.

### git-delta

```dockerfile
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://...git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_...deb" && rm "git-delta_...deb"
```

Installs the pre-built `.deb` package (handles dependencies automatically).
`dpkg --print-architecture` returns `amd64` or `arm64` for multi-arch support,
so the same Dockerfile works on Intel and Apple Silicon hosts.

### Bash History Persistence

```dockerfile
RUN mkdir /commandhistory && \
  touch /commandhistory/.bash_history && \
  chown -R vscode /commandhistory
```

Creates a directory at a **volume-mountable path outside `$HOME`**. The
`devcontainer.json` mounts a named volume here, so shell history survives
container rebuilds. It's outside `$HOME` so it doesn't interfere with other home
directory mounts.

### Environment Flag

```dockerfile
ENV DEVCONTAINER=true
```

Convention flag for scripts to detect they're running inside a devcontainer.
Claude Code, init scripts, and CI tooling can check `$DEVCONTAINER` to adjust
behavior.

### Workspace and Config Directories

```dockerfile
RUN mkdir -p /workspace /home/vscode/.claude && \
  chown -R vscode:vscode /workspace /home/vscode/.claude
```

- `/workspace` — bind mount target for the host project
- `/home/vscode/.claude` — Claude Code config and auth (backed by a named volume)

Both are created with `vscode` ownership so the non-root user can write to them
immediately.

### Claude Code Install

```dockerfile
USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash \
  && sudo cp /home/vscode/.local/bin/claude /usr/local/bin/claude \
  && sudo chmod +x /usr/local/bin/claude
```

The install script places `claude` at `~/.local/bin/claude`. However, the
`~/.claude` volume mount (from `devcontainer.json`) shadows that path on
subsequent container starts. The `sudo cp` copies the binary to `/usr/local/bin/`
— a system path that isn't affected by any volume mount.

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
RUN sh -c "$(wget -O- .../zsh-in-docker.sh)" -- \
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

```dockerfile
RUN python3 -c "..."
```

Injects `POWERLEVEL9K_*` color variables into `.zshrc` **before** the
`source $ZSH/oh-my-zsh.sh` line. This uses Python instead of sed because:

1. Shell `sed` has notorious issues with newline escaping across platforms
2. Python's `pathlib` handles file I/O cleanly
3. Each variable gets its own line, making the result easy to read

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

**Allowed domains:**

| Domain | Purpose |
|--------|---------|
| `registry.npmjs.org` | npm package downloads |
| `api.anthropic.com` | Claude API |
| `sentry.io` | Error reporting |
| `statsig.anthropic.com` / `statsig.com` | Feature flags and analytics |
| `marketplace.visualstudio.com` | VS Code extension marketplace |
| `vscode.blob.core.windows.net` | VS Code extension downloads |
| `update.code.visualstudio.com` | VS Code update checks |
| `conda.anaconda.org` | Conda package channel |
| `pypi.org` / `files.pythonhosted.org` | PyPI package index and downloads |
| `prefix.dev` / `repo.prefix.dev` / `conda-mapping.prefix.dev` | Pixi package manager backends |
| `claude.ai` | Claude Code authentication |

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

### Step 9: Default DROP Policy

```bash
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
```

**The security boundary.** After all allow rules are in place, set the default
policy to DROP on all chains. Any packet that doesn't match an allow rule is
silently dropped. This is set after the allow rules (not before) to avoid
locking the script out of the network mid-execution.

### Step 10: Stateful Connection Tracking

```bash
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
```

Allows return traffic for already-established connections. Without this, even
allowed connections would fail because the response packets wouldn't be
permitted.

### Step 11: ipset Match Rule

```bash
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
```

The actual allow rule: any outbound packet whose destination IP is in the
`allowed-domains` ipset is accepted. This single rule replaces what would
otherwise be dozens of individual iptables rules.

### Step 12: REJECT Catch-All

```bash
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited
```

Explicitly **REJECT** (not DROP) all remaining outbound traffic. The difference:
- **REJECT** sends an ICMP "admin prohibited" response → the client gets an
  immediate error (connection refused)
- **DROP** silently discards → the client waits for a timeout (30+ seconds)

REJECT is used here because immediate feedback is better for developer
experience — you instantly know a connection was blocked rather than waiting.

### Step 13: Verification

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
