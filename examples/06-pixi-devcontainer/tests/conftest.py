"""Pytest-playwright configuration: connect to the external Chrome via CDP.

Mirrors the CDP resolution logic in .devcontainer/cdp-relay.sh so that
pytest uses the same host browser configured in .mcp.json.
"""

import json
import urllib.request

import pytest

CDP_HOST = "host.docker.internal:9222"


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
    """Connect to the external host Chrome instead of launching a new browser."""
    ws_url = _resolve_cdp_endpoint()
    browser = playwright.chromium.connect_over_cdp(ws_url)
    yield browser
    browser.close()
