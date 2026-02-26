#!/bin/bash
set -euo pipefail

# Toggle Playwright MCP between container (headless Chromium) and host browser (CDP).
#
# Usage:
#   toggle-browser.sh            Show current mode
#   toggle-browser.sh container  Switch to headless Chromium inside the container
#   toggle-browser.sh host       Switch to Chrome on the host via CDP

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
MCP_CONFIG="$WORKSPACE_DIR/.mcp.json"
CONTAINER_TEMPLATE="$SCRIPT_DIR/mcp-container.json"
HOST_TEMPLATE="$SCRIPT_DIR/mcp-host-browser.json"

# --- Detect current mode ---

detect_mode() {
    if [ ! -f "$MCP_CONFIG" ]; then
        echo "unknown"
        return
    fi

    if jq -e '.mcpServers.playwright.args | index("--cdp-endpoint")' "$MCP_CONFIG" >/dev/null 2>&1; then
        echo "host"
    elif jq -e '.mcpServers.playwright.args | index("--headless")' "$MCP_CONFIG" >/dev/null 2>&1; then
        echo "container"
    else
        echo "unknown"
    fi
}

current_mode=$(detect_mode)

# --- No argument: show current mode ---

if [ $# -eq 0 ]; then
    case "$current_mode" in
        container)
            echo "Current mode: container (headless Chromium inside the devcontainer)"
            ;;
        host)
            echo "Current mode: host (Chrome on host via CDP at host.docker.internal:9222)"
            ;;
        *)
            echo "Current mode: unknown (.mcp.json is missing or has unexpected config)"
            ;;
    esac
    exit 0
fi

# --- Argument: switch mode ---

requested_mode="$1"

case "$requested_mode" in
    container)
        if [ "$current_mode" = "container" ]; then
            echo "Already in container mode. No changes made."
            exit 0
        fi
        cp "$CONTAINER_TEMPLATE" "$MCP_CONFIG"
        echo "Switched to container mode (headless Chromium inside the devcontainer)."
        echo ""
        echo "Restart Claude Code to pick up the new MCP config."
        ;;

    host)
        if [ "$current_mode" = "host" ]; then
            echo "Already in host mode. No changes made."
            exit 0
        fi
        cp "$HOST_TEMPLATE" "$MCP_CONFIG"
        echo "Switched to host mode (Chrome on host via CDP)."
        echo ""

        # Non-blocking reachability check
        if curl -s --connect-timeout 3 "http://host.docker.internal:9222/json/version" >/dev/null 2>&1; then
            echo "Chrome is reachable at host.docker.internal:9222."
        else
            echo "Chrome is not reachable at host.docker.internal:9222."
            echo "Launch Chrome on your host with remote debugging enabled:"
            echo ""
            echo "  macOS:"
            echo '    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug'
            echo ""
            echo "  Linux:"
            echo "    google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug"
            echo ""
            echo "  Windows:"
            echo '    "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=%TEMP%\chrome-debug'
        fi

        echo ""
        echo "Restart Claude Code to pick up the new MCP config."
        ;;

    *)
        echo "Usage: toggle-browser.sh [container|host]"
        echo ""
        echo "  (no argument)  Show current mode"
        echo "  container      Use headless Chromium inside the devcontainer"
        echo "  host           Connect to Chrome on the host via CDP"
        exit 1
        ;;
esac
