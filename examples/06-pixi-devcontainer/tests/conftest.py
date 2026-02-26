"""Pytest-playwright configuration: browser mode resolved at runtime.

Mode resolution (first match wins):
  1. BROWSER_MODE env var      — for CI or explicit override
  2. .devcontainer/.browser-mode dotfile — persistent toggle state
  3. Default: "container"      — safest, works out of the box

Modes:
  container — launches headless Chromium inside the devcontainer
  host      — connects to Chrome on the host via CDP
"""

import json
import os
import urllib.request
from pathlib import Path

import pytest

CDP_HOST = "host.docker.internal:9222"
DOTFILE = Path(__file__).resolve().parent.parent / ".devcontainer" / ".browser-mode"


def _resolve_browser_mode() -> str:
    """Resolve the browser mode using three-tier priority."""
    env = os.environ.get("BROWSER_MODE", "").strip()
    if env:
        return env
    if DOTFILE.is_file():
        return DOTFILE.read_text().strip()
    return "container"


def _resolve_cdp_endpoint() -> str:
    """Resolve the CDP WebSocket URL from the host Chrome instance."""
    req = urllib.request.Request(
        f"http://{CDP_HOST}/json/version",
        headers={"Host": "localhost"},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())

    ws_url: str = data["webSocketDebuggerUrl"]
    # Inside the container "localhost" means the container itself;
    # rewrite to reach the host browser.
    return ws_url.replace("ws://localhost", f"ws://{CDP_HOST}")


@pytest.fixture(scope="session")
def browser(playwright):
    """Launch or connect to a browser based on the resolved mode."""
    mode = _resolve_browser_mode()

    if mode == "host":
        ws_url = _resolve_cdp_endpoint()
        browser = playwright.chromium.connect_over_cdp(ws_url)
    else:
        browser = playwright.chromium.launch(headless=True)

    yield browser
    browser.close()
