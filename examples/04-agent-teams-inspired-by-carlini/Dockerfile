FROM ghcr.io/prefix-dev/pixi:noble

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git curl build-essential jq python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install --break-system-packages pytest

# Install Node.js 20 and Claude CLI
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code

# Create non-root user (claude-code refuses --dangerously-skip-permissions as root)
RUN useradd -m -s /bin/bash agent
RUN git config --global --replace-all safe.directory '*'

WORKDIR /workspace
RUN chown agent:agent /workspace

COPY agent_loop.sh /usr/local/bin/agent_loop.sh
RUN chmod +x /usr/local/bin/agent_loop.sh

USER agent

RUN git config --global user.name "Claude Agent" \
    && git config --global user.email "claude-agent@local" \
    && git config --global init.defaultBranch main \
    && git config --global safe.directory '*'

ENTRYPOINT ["agent_loop.sh"]
