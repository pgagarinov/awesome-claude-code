FROM mcr.microsoft.com/devcontainers/base:jammy

ARG TZ
ENV TZ="$TZ"

# Install system dependencies not in base image
# (base already has: git, curl, wget, sudo, zsh, gnupg2, less, procps, man-db, unzip)
RUN apt-get update && apt-get install -y --no-install-recommends \
  fzf \
  iptables \
  ipset \
  iproute2 \
  dnsutils \
  aggregate \
  jq \
  nano \
  vim \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pixi
ARG PIXI_VERSION=v0.63.2
RUN curl -L -o /usr/local/bin/pixi -fsSL --compressed \
    "https://github.com/prefix-dev/pixi/releases/download/${PIXI_VERSION}/pixi-$(uname -m)-unknown-linux-musl" \
    && chmod +x /usr/local/bin/pixi \
    && pixi info

# Install git-delta
ARG GIT_DELTA_VERSION=0.18.2
RUN ARCH=$(dpkg --print-architecture) && \
  wget "https://github.com/dandavison/delta/releases/download/${GIT_DELTA_VERSION}/git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  dpkg -i "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb" && \
  rm "git-delta_${GIT_DELTA_VERSION}_${ARCH}.deb"

# Persist bash history
RUN mkdir /commandhistory && \
  touch /commandhistory/.bash_history && \
  chown -R vscode /commandhistory

ENV DEVCONTAINER=true

# Create workspace and config directories
RUN mkdir -p /workspace /home/vscode/.claude && \
  chown -R vscode:vscode /workspace /home/vscode/.claude

WORKDIR /workspace

USER vscode

# Install Claude Code, then copy binary to a system path so the ~/.claude volume mount won't shadow it
RUN curl -fsSL https://claude.ai/install.sh | bash \
  && sudo cp /home/vscode/.local/bin/claude /usr/local/bin/claude \
  && sudo chmod +x /usr/local/bin/claude

ENV SHELL=/bin/zsh
ENV EDITOR=nano
ENV VISUAL=nano

# zsh with powerline10k theme
ARG ZSH_IN_DOCKER_VERSION=1.2.0
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v${ZSH_IN_DOCKER_VERSION}/zsh-in-docker.sh)" -- \
  -p git \
  -p fzf \
  -a 'eval "$(pixi completion -s zsh)"' \
  -a "export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
  -x

# Prompt colors + fzf fix — must be set BEFORE oh-my-zsh sources p10k/plugins
# Uses Python to avoid sed newline-escaping bugs (each var gets its own line)
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

# Firewall script setup
COPY init-firewall.sh /usr/local/bin/
USER root
RUN chmod +x /usr/local/bin/init-firewall.sh && \
  echo "vscode ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh" > /etc/sudoers.d/vscode-firewall && \
  echo "vscode ALL=(root) NOPASSWD: /bin/chown" > /etc/sudoers.d/vscode-chown && \
  chmod 0440 /etc/sudoers.d/vscode-firewall /etc/sudoers.d/vscode-chown
USER vscode
