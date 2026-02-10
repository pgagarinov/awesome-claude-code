#!/usr/bin/env bash
set -euo pipefail

AGENT_ID="${AGENT_ID:?AGENT_ID must be set}"
UPSTREAM="/upstream"
WORK="/workspace/repo"
LOG_DIR="/upstream/agent_logs"
MAX_ITERATIONS="${MAX_ITERATIONS:-0}" # 0 = unlimited

mkdir -p "$LOG_DIR"

iteration=0

log() {
    echo "[agent-${AGENT_ID}] $(date '+%Y-%m-%d %H:%M:%S') $*"
}

# Stagger agent starts to reduce initial task-claiming races.
# Agent-1 starts immediately, agent-2 waits 5s, agent-3 waits 10s, etc.
STAGGER_DELAY=$(( (AGENT_ID - 1) * 5 ))
if [[ "$STAGGER_DELAY" -gt 0 ]]; then
    log "Staggering start by ${STAGGER_DELAY}s to reduce claim races"
    sleep "$STAGGER_DELAY"
fi

while true; do
    iteration=$((iteration + 1))
    if [[ "$MAX_ITERATIONS" -gt 0 && "$iteration" -gt "$MAX_ITERATIONS" ]]; then
        log "Reached max iterations ($MAX_ITERATIONS), exiting"
        break
    fi

    log "=== Iteration $iteration ==="

    # Fresh clone each iteration
    rm -rf "$WORK"
    git clone "$UPSTREAM" "$WORK"
    cd "$WORK"

    # Ensure .gitignore exists to prevent binary/generated files
    if ! grep -q '__pycache__' .gitignore 2>/dev/null; then
        printf '\n__pycache__/\n*.py[cod]\n*.pyo\n.pytest_cache/\n.pixi/\n.venv/\nnode_modules/\n' >> .gitignore
        git add .gitignore
        git commit -m "agent-${AGENT_ID}: add .gitignore" || true
        git push origin main || true
    fi

    if [[ ! -f AGENT_PROMPT.md ]]; then
        log "No AGENT_PROMPT.md in repo, waiting..."
        sleep 10
        continue
    fi

    # Run Claude — it handles all git operations (commit, pull, push)
    log "Invoking Claude..."
    LOGFILE="${LOG_DIR}/agent_${AGENT_ID}_iter${iteration}_$(date +%s).log"

    PROMPT="$(cat AGENT_PROMPT.md)

---
You are agent-${AGENT_ID}. Follow the task coordination protocol described above."

    claude --dangerously-skip-permissions \
        -p "$PROMPT" \
        --model "${CLAUDE_MODEL:-claude-opus-4-6}" \
        --output-format stream-json --verbose \
        2>&1 | tee "$LOGFILE" || {
        log "Claude exited with error, continuing..."
    }

    log "Iteration $iteration complete"
    sleep 2
done
