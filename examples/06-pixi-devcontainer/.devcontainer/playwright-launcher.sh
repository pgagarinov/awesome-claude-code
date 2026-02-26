#!/bin/bash
# Launches Playwright MCP in the correct browser mode.
#
# Mode resolution (first match wins):
#   1. BROWSER_MODE env var      — for CI or explicit override
#   2. .devcontainer/.browser-mode dotfile — persistent toggle state
#   3. Default: "container"      — safest, works out of the box
#
# Modes:
#   container — headless Chromium inside the devcontainer
#   host      — Chrome on the host via CDP relay

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILE="$SCRIPT_DIR/.browser-mode"

# --- Three-tier mode resolution ---

if [ -n "${BROWSER_MODE:-}" ]; then
    mode="$BROWSER_MODE"
elif [ -f "$DOTFILE" ]; then
    mode="$(cat "$DOTFILE")"
else
    mode="container"
fi

# --- Launch ---

case "$mode" in
    host)
        exec bash "$SCRIPT_DIR/cdp-relay.sh"
        ;;
    container|*)
        exec npx @playwright/mcp --headless --no-sandbox --isolated --browser chromium
        ;;
esac
