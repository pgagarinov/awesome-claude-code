#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER_PREFIX="cc-agent"
INTERVAL=30
MAX_UPDATES=0
UPSTREAM="${SCRIPT_DIR}/upstream.git"

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Periodically summarizes agent activity using Claude Haiku.

Options:
  --interval N       Seconds between updates (default: 30)
  --upstream PATH    Path to bare upstream repo (default: ./upstream.git)
  --max-updates N    Exit after N update cycles (default: 0 = unlimited)
  -h, --help         Show this help
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --interval) INTERVAL="$2"; shift 2 ;;
        --upstream) UPSTREAM="$2"; shift 2 ;;
        --max-updates) MAX_UPDATES="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

UPSTREAM="$(cd "$UPSTREAM" && pwd)"

if [[ ! -d "$UPSTREAM" ]]; then
    echo "Error: upstream repo not found at $UPSTREAM"
    exit 1
fi

# Track byte offsets per log file and last-seen commit
declare -A LOG_OFFSETS=()
LAST_COMMIT=""

update_count=0
while true; do
    # --- Gather delta info ---
    DELTA=""

    # Container status (always include full status — it's small)
    DELTA+="## Container Status
"
    DELTA+="$(docker ps -a --filter "name=${CONTAINER_PREFIX}-" \
        --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "(docker not available)")"
    DELTA+="
"

    # New commits since last check
    CURRENT_COMMIT=$(git --git-dir="$UPSTREAM" rev-parse HEAD 2>/dev/null || echo "")
    if [[ -n "$CURRENT_COMMIT" ]]; then
        if [[ -z "$LAST_COMMIT" ]]; then
            # First run — show last 15
            NEW_COMMITS=$(git --git-dir="$UPSTREAM" log --oneline -15 2>/dev/null || echo "(no commits)")
        elif [[ "$CURRENT_COMMIT" != "$LAST_COMMIT" ]]; then
            NEW_COMMITS=$(git --git-dir="$UPSTREAM" log --oneline "${LAST_COMMIT}..HEAD" 2>/dev/null || echo "(error reading commits)")
        else
            NEW_COMMITS=""
        fi
        LAST_COMMIT="$CURRENT_COMMIT"

        if [[ -n "$NEW_COMMITS" ]]; then
            DELTA+="
## New Commits
$NEW_COMMITS
"
        fi
    fi

    # Agent log deltas — only new bytes since last read
    HAS_LOG_DELTA=false
    if [[ -d "$UPSTREAM/agent_logs" ]]; then
        LOG_FILES=$(ls -t "$UPSTREAM/agent_logs"/*.log 2>/dev/null || true)
        if [[ -n "$LOG_FILES" ]]; then
            # Get the most recent log file per agent
            declare -A SEEN_AGENTS=()
            for f in $LOG_FILES; do
                BASENAME=$(basename "$f")
                AGENT_NUM=$(echo "$BASENAME" | sed -n 's/^agent_\([0-9]*\)_.*/\1/p')
                if [[ -n "$AGENT_NUM" && -z "${SEEN_AGENTS[$AGENT_NUM]:-}" ]]; then
                    SEEN_AGENTS[$AGENT_NUM]=1

                    FILE_SIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)
                    PREV_OFFSET="${LOG_OFFSETS[$f]:-0}"

                    if [[ "$FILE_SIZE" -gt "$PREV_OFFSET" ]]; then
                        NEW_BYTES=$((FILE_SIZE - PREV_OFFSET))
                        NEW_CONTENT=$(tail -c "$NEW_BYTES" "$f" 2>/dev/null || echo "(unreadable)")
                        DELTA+="
## Agent $AGENT_NUM — New Log Output ($(basename "$f"))
$NEW_CONTENT
"
                        HAS_LOG_DELTA=true
                    fi
                    LOG_OFFSETS[$f]="$FILE_SIZE"
                fi
            done
            unset SEEN_AGENTS
        fi
    fi

    # Skip Haiku call if nothing changed
    if [[ -z "${NEW_COMMITS:-}" && "$HAS_LOG_DELTA" == false ]]; then
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Monitor Update — $TIMESTAMP (no new activity)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "  Next update in ${INTERVAL}s (Ctrl+C to stop)"
        echo ""
        update_count=$((update_count + 1))
        if [[ "$MAX_UPDATES" -gt 0 && "$update_count" -ge "$MAX_UPDATES" ]]; then
            break
        fi
        sleep "$INTERVAL"
        continue
    fi

    # --- Summarize delta with Haiku ---
    PROMPT="You are a concise build/CI monitor. Below is NEW activity (since the last update) from a multi-agent coding system. Each agent is a Claude Code instance running in a Docker container, working on the same repo.

Produce a SHORT structured summary with these sections:
- **Agent Status**: one line per agent — running/exited, which iteration, any errors
- **Recent Activity**: what each agent did since last update (1-2 lines each)
- **New Commits**: notable new commits (skip routine ones)
- **Issues**: any errors, conflicts, or problems observed (or 'None')

Be concise. Skip sections if empty. Do not repeat raw data.

--- NEW ACTIVITY SINCE LAST UPDATE ---
$DELTA"

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Monitor Update — $TIMESTAMP"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    claude --model claude-haiku-4-5-20251001 \
        --output-format text \
        -p "$PROMPT" 2>/dev/null || echo "(Haiku summarization failed)"

    echo ""
    echo "  Next update in ${INTERVAL}s (Ctrl+C to stop)"
    echo ""

    update_count=$((update_count + 1))
    if [[ "$MAX_UPDATES" -gt 0 && "$update_count" -ge "$MAX_UPDATES" ]]; then
        break
    fi

    sleep "$INTERVAL"
done
