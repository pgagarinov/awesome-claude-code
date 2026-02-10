#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER_PREFIX="cc-agent"
UPSTREAM="${SCRIPT_DIR}/upstream.git"

echo "=== Agent Containers ==="
docker ps --filter "name=${CONTAINER_PREFIX}-" --format "table {{.Names}}\t{{.Status}}\t{{.ID}}"
echo ""

# Show recent commits
if [[ -d "$UPSTREAM" ]]; then
    echo "=== Recent Commits ==="
    git --git-dir="$UPSTREAM" log --oneline -10 2>/dev/null || echo "(no commits yet)"
    echo ""
fi

# Show logs from each running container
containers=$(docker ps --filter "name=${CONTAINER_PREFIX}-" --format "{{.Names}}" 2>/dev/null || true)
for c in $containers; do
    echo "=== Logs: $c (last 20 lines) ==="
    docker logs --tail 20 "$c" 2>&1
    echo ""
done

# Show agent log files
if [[ -d "$UPSTREAM/agent_logs" ]]; then
    echo "=== Agent Log Files ==="
    ls -lt "$UPSTREAM/agent_logs/" 2>/dev/null | head -10
fi
