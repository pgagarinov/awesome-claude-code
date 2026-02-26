#!/bin/bash
set -euo pipefail

# Toggle Playwright MCP between container (headless Chromium) and host browser (CDP).
#
# Usage:
#   toggle-browser.sh            Show current mode and source
#   toggle-browser.sh container  Switch to headless Chromium inside the container
#   toggle-browser.sh host       Switch to Chrome on the host via CDP

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILE="$SCRIPT_DIR/.browser-mode"

# --- Three-tier mode resolution (same logic as playwright-launcher.sh) ---

resolve_mode_with_source() {
    if [ -n "${BROWSER_MODE:-}" ]; then
        echo "$BROWSER_MODE (from BROWSER_MODE env var)"
    elif [ -f "$DOTFILE" ]; then
        echo "$(cat "$DOTFILE") (from .devcontainer/.browser-mode dotfile)"
    else
        echo "container (default — no env var or dotfile set)"
    fi
}

# --- No argument: show current mode ---

if [ $# -eq 0 ]; then
    mode_info=$(resolve_mode_with_source)
    echo "Current mode: $mode_info"
    echo ""
    echo "Usage: toggle-browser.sh [container|host]"
    exit 0
fi

# --- Argument: switch mode ---

requested_mode="$1"

case "$requested_mode" in
    container)
        echo "container" > "$DOTFILE"
        echo "Switched to container mode (headless Chromium inside the devcontainer)."
        echo ""
        echo "Restart Claude Code to pick up the mode change."
        ;;

    host)
        echo "host" > "$DOTFILE"
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
        echo "Restart Claude Code to pick up the mode change."
        ;;

    *)
        echo "Usage: toggle-browser.sh [container|host]"
        echo ""
        echo "  (no argument)  Show current mode and source"
        echo "  container      Use headless Chromium inside the devcontainer"
        echo "  host           Connect to Chrome on the host via CDP"
        exit 1
        ;;
esac
