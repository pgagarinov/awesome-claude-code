# Ubuntu 22.04 LTS base with pre-configured: devcontainer 'vscode' user, sudo,
# git, curl, wget, zsh, gnupg2, less, procps, man-db, unzip
FROM mcr.microsoft.com/devcontainers/base:jammy

# Propagate host timezone into the container so logs, timestamps, and
# git commit dates use the local time instead of UTC
ARG TZ
ENV TZ="$TZ"

# Install system dependencies not in the base image.
# (base already has: git, curl, wget, sudo, zsh, gnupg2, less, procps, man-db, unzip)
RUN apt-get update && apt-get install -y --no-install-recommends \
  fzf \
  # fzf:       fuzzy finder for shell history search (Ctrl+R) and file navigation
  iptables \
  # iptables:  kernel-level firewall — used by init-firewall.sh to DROP/ACCEPT traffic
  ipset \
  # ipset:     efficient IP set matching — stores allowed CIDRs for iptables to match against
  iproute2 \
  # iproute2:  provides `ip route` command to detect the Docker host network gateway
  dnsutils \
  # dnsutils:  provides `dig` command to resolve domain names to IPs for the firewall allowlist
  aggregate \
  # aggregate: merges overlapping CIDR ranges (compacts GitHub's large IP list into fewer rules)
  jq \
  # jq:        JSON parser — extracts IP ranges from the GitHub API /meta endpoint
  nano \
  # nano:      terminal editor — set as $EDITOR so Claude Code uses it for file editing
  vim \
  # vim:       alternative terminal editor for users who prefer it
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pixi — a fast conda/PyPI package manager.
# Direct binary download (no package manager needed). Uses the musl build
# for maximum portability across container base images.
# `pixi info` is a smoke test to verify the binary works.
ARG PIXI_VERSION=v0.63.2
RUN curl -L -o /usr/local/bin/pixi -fsSL --compressed \
    "https://github.com/prefix-dev/pixi/releases/download/${PIXI_VERSION}/pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi info

# Install git-delta — a syntax-highlighting pager for git diffs.
# Uses the pre-built .deb package (handles dependencies automatically).
# `dpkg --print-architecture` detects amd64/arm64 for multi-arch support.
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# Install Node.js LTS from NodeSource, then Chromium system dependencies.
# The NodeSource setup script adds its repo and runs `apt-get update`, so
# the subsequent `apt-get install` uses a fresh package index.
# Chromium deps are listed explicitly (instead of using `playwright install-deps`)
# because that command runs its own `apt-get update` which triggers HTTP 400
# errors in Docker BuildKit's networking layer.
# Node is installed in the Dockerfile (not as a devcontainer feature) so that
# Playwright's browser binaries are baked into the image at build time —
# zero runtime downloads required.
ARG NODE_MAJOR=22
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
    # --- Chromium runtime deps (from Playwright's nativeDeps.ts) ---
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libglib2.0-0 libnspr4 libnss3 \
    libpango-1.0-0 libwayland-client0 libx11-6 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
    # --- Headless rendering: virtual framebuffer + fonts ---
    xvfb fonts-noto-color-emoji fonts-unifont libfontconfig1 libfreetype6 \
    xfonts-cyrillic xfonts-scalable fonts-liberation fonts-ipafont-gothic \
    fonts-wqy-zenhei fonts-tlwg-loma-otf fonts-freefont-ttf \
  && node --version && npm --version \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Persist bash/zsh history to a volume-mountable path outside $HOME.
# The /commandhistory directory is mounted as a named Docker volume in
# devcontainer.json, so history survives container rebuilds.
RUN mkdir /commandhistory && \
  touch /commandhistory/.bash_history && \
  chown -R vscode /commandhistory

# Convention flag for scripts to detect they're running inside a devcontainer
# (e.g., Claude Code, init scripts, or CI tooling can check $DEVCONTAINER)
ENV DEVCONTAINER=true

# Create workspace and Claude config directories with correct ownership.
# /workspace is where the host project is bind-mounted.
# /home/vscode/.claude stores Claude Code config/auth (backed by a named volume).
RUN mkdir -p /workspace /home/vscode/.claude && \
  chown -R vscode:vscode /workspace /home/vscode/.claude

WORKDIR /workspace

# Install global npm packages (requires root for /usr/lib/node_modules).
# - @anthropic-ai/claude-code: Claude Code CLI (replaces the curl install script,
#   and avoids the sudo cp workaround since npm puts the binary on $PATH directly)
# - @playwright/mcp: Playwright MCP server for headless browser automation
RUN npm install -g @anthropic-ai/claude-code @playwright/mcp

# Switch to non-root user for all subsequent commands
USER vscode

# Download the Chromium binary into the vscode user's cache.
# Uses the MCP package's bundled Playwright (not a standalone install) to ensure
# the browser revision matches what the MCP server expects at runtime.
# PLAYWRIGHT_BROWSERS_PATH sets where Playwright stores browser binaries —
# must be under the vscode user's home so it persists and is accessible.
ENV PLAYWRIGHT_BROWSERS_PATH=/home/vscode/.cache/ms-playwright
RUN /usr/lib/node_modules/@playwright/mcp/node_modules/.bin/playwright install chromium

# Set default shell to zsh (matches our Powerlevel10k theme setup below).
# Set nano as the default editor — Claude Code uses $EDITOR for file operations.
# $VISUAL is the "visual" editor (used by programs that want a full-screen editor).
ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano

# Install zsh-in-docker: configures Oh My Zsh + Powerlevel10k theme.
#   -p git:  enable the git plugin (aliases like gst, gco, etc.)
#   -p fzf:  enable the fzf plugin (Ctrl+R history search, Ctrl+T file finder)
#   -a '...':  append lines to .zshrc:
#     - pixi shell completions for zsh
#     - persist command history to the mounted /commandhistory volume
#   -x:  skip automatic theme configuration (we customize colors below)
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a 'eval "$(pixi completion -s zsh)"' \
  -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  -x

# Customize Powerlevel10k prompt colors for a neutral pastel green theme.
# Uses Python instead of sed to avoid shell newline-escaping issues.
# These vars must be set BEFORE `source $ZSH/oh-my-zsh.sh` in .zshrc,
# so we insert them just above that line.
#
# Color codes (256-color palette):
#   151=sage green, 158=mint, 108=moss green, 0=black, 231=white, 131=dusty rose
#   238=dark gray (for shortened directory segments)
RUN python3 -c "\
import pathlib; \
p = pathlib.Path.home() / '.zshrc'; \
lines = p.read_text().splitlines(); \
insert = [ \
  '# 256-color support (zsh-in-docker sets xterm which only has 8)', \
  'export TERM=xterm-256color', \
  '# Disable fzf key-bindings (file missing on Ubuntu Jammy fzf 0.29)', \
  'DISABLE_FZF_KEY_BINDINGS=true', \
  '# Neutral pastel green prompt (black text on light bg for max readability)', \
  '# 151=sage, 158=mint, 108=moss, 0=black, 231=white, 131=dusty rose', \
  'POWERLEVEL9K_USER_DEFAULT_BACKGROUND=108', \
  'POWERLEVEL9K_USER_DEFAULT_FOREGROUND=0', \
  'POWERLEVEL9K_DIR_BACKGROUND=151', \
  'POWERLEVEL9K_DIR_FOREGROUND=0', \
  'POWERLEVEL9K_DIR_SHORTENED_FOREGROUND=238', \
  'POWERLEVEL9K_DIR_ANCHOR_FOREGROUND=0', \
  'POWERLEVEL9K_VCS_CLEAN_BACKGROUND=158', \
  'POWERLEVEL9K_VCS_CLEAN_FOREGROUND=0', \
  'POWERLEVEL9K_VCS_MODIFIED_BACKGROUND=151', \
  'POWERLEVEL9K_VCS_MODIFIED_FOREGROUND=0', \
  'POWERLEVEL9K_VCS_UNTRACKED_BACKGROUND=158', \
  'POWERLEVEL9K_VCS_UNTRACKED_FOREGROUND=0', \
  'POWERLEVEL9K_STATUS_OK_BACKGROUND=108', \
  'POWERLEVEL9K_STATUS_OK_FOREGROUND=0', \
  'POWERLEVEL9K_STATUS_ERROR_BACKGROUND=131', \
  'POWERLEVEL9K_STATUS_ERROR_FOREGROUND=231', \
]; \
idx = next(i for i, l in enumerate(lines) if l.startswith('source \$ZSH/oh-my-zsh.sh')); \
lines[idx:idx] = insert; \
p.write_text('\n'.join(lines) + '\n'); \
"

# Firewall script setup:
# 1. COPY the script into the image (runs as current USER=vscode, but that's fine for COPY)
# 2. Switch to root to set permissions and sudoers
# 3. Grant passwordless sudo for ONLY the firewall script and chown command —
#    this follows least-privilege (vscode can't sudo arbitrary commands)
# 4. chmod 0440 on sudoers files — required by sudo for security
# 5. Switch back to vscode for the final image layer
COPY init-firewall.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/init-firewall.sh && \
  echo "vscode ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/vscode-firewall && \
  echo "vscode ALL=(root) NOPASSWD: /bin/chown" > /etc/sudoers.d/vscode-chown && \
  chmod 0440 /etc/sudoers.d/vscode-firewall /etc/sudoers.d/vscode-chown
USER vscode
