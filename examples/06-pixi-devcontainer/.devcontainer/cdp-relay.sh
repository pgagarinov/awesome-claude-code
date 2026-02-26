#!/bin/bash
# Resolves the CDP WebSocket URL from the host browser and launches Playwright MCP.
#
# Chrome's /json/version returns ws://localhost/devtools/browser/<id>, but from
# inside a container "localhost" is the container itself. This script rewrites
# the URL to use host.docker.internal:9222 so the WebSocket connects to the host.

set -euo pipefail

CDP_HOST="host.docker.internal:9222"

WS_URL=$(curl -sf -H "Host: localhost" "http://${CDP_HOST}/json/version" \
  | jq -r .webSocketDebuggerUrl \
  | sed "s|ws://localhost|ws://${CDP_HOST}|")

if [ -z "$WS_URL" ]; then
  echo "ERROR: Could not resolve WebSocket URL from http://${CDP_HOST}" >&2
  exit 1
fi

exec npx @playwright/mcp --cdp-endpoint "$WS_URL"
