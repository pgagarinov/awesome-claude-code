#!/usr/bin/env bash
set -euo pipefail

CONTAINER_PREFIX="cc-agent"

echo "Stopping all agent containers..."
containers=$(docker ps -q --filter "name=${CONTAINER_PREFIX}-" 2>/dev/null || true)

if [[ -z "$containers" ]]; then
    echo "No running agent containers found."
    exit 0
fi

docker stop $containers
docker rm $containers 2>/dev/null || true

echo "All agent containers stopped."
