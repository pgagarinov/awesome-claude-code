# Browser automation in containers and beyond

**Only Playwright MCP offers first-class Docker support for containerized development; Claude Code's built-in Chrome integration fundamentally cannot work in devcontainers, and Chrome DevTools MCP requires manual workarounds.** This gap matters because devcontainers are increasingly the standard for reproducible development environments, yet browser automation—critical for AI-assisted web development—remains a pain point inside them. The broader ecosystem offers over a dozen alternative MCP servers and tools, with Playwright MCP and Browser-Use emerging as the most actively maintained options for both Claude Code and OpenCode.

## At a glance

| Tool | Container-ready? | Approach | Best for |
|---|---|---|---|
| **Playwright MCP** | Yes — official Docker image | Launches headless Chromium | Devcontainers, CI, general automation |
| **Chrome DevTools MCP** | Manual setup required | Connects to any Chrome via DevTools Protocol | Targeting a specific Chrome instance |
| **Claude Code Chrome** | No — architecturally blocked | Chrome Native Messaging (host-only) | Host-only workflows; not viable in containers |
| **Browser-Use** | Yes — cloud or local | Cloud-hosted or local headless browser | Large community, dual cloud/local modes |
| **Browserbase MCP** | Yes — fully cloud | Cloud browsers with natural-language control | Stealth, proxies, no local Chrome needed |
| **Dev-Browser** | Host browser only | Controls your existing Chrome via extension | Authenticated sessions, preserving cookies |
| **BrowserMCP** | Host browser only | Adapts Playwright to your running browser | Reusing real browser fingerprint |
| **BrowserTools MCP** | Host browser only | Chrome extension + Node server | Debugging (screenshots, console logs, Lighthouse) |

> **TL;DR for devcontainer users:** Use Playwright MCP with `--headless --browser chromium --no-sandbox --isolated`. It's the only option with production-ready container support out of the box.

---

## Playwright MCP is the only tool with real Docker support

Microsoft's Playwright MCP (`@playwright/mcp`) stands apart with a **Dockerfile in the repo**, an **official Docker image** at `mcr.microsoft.com/playwright/mcp`, and explicit documentation for containerized use. The Docker image ships with headless Chromium pre-installed, and the server accepts the critical container flags: `--headless`, `--browser chromium`, `--no-sandbox`, and `--isolated`. There is no `devcontainer.json` in the repo, but the combination of official Docker support and community guides makes this the most container-ready option.

The recommended devcontainer configuration installs Chromium dependencies directly:

```dockerfile
USER root
RUN npx -y playwright@latest install-deps chromium
USER node
RUN npx -y playwright@latest install chromium
```

Then configure the MCP server with `--browser chromium --headless --isolated --no-sandbox`. Alternatively, you can pull the official image directly: `docker run -i --rm --init mcr.microsoft.com/playwright/mcp`.

**Container-specific issues are well-documented.** The most common problem—browser profile lock errors (#891, #636)—is solved by combining `--isolated` and `--no-sandbox`. An HTTP transport session management bug (#1140) affected Kubernetes deployments but stdio transport works reliably. Several community projects provide complete devcontainer setups, including `capi/devcontainer-desktop-lite-mcp-playwright` (with noVNC desktop), `iuill/playwright-mcp-docker` (Docker Compose), and a detailed gist by vibe2viable specifically for Claude Code devcontainers.

One important caveat: **Docker mode only supports headless Chromium**. No Firefox, WebKit, or headed browsing in containers.

## Claude Code's Chrome integration hits a hard architectural wall

Claude Code's built-in browser support (`claude --chrome` and the Claude in Chrome extension) **cannot work in devcontainers**. This is a confirmed open bug (GitHub issue #25506, filed February 13, 2026). The root cause is architectural, not a simple configuration gap.

The integration relies on **Chrome Native Messaging**, a host-local mechanism where Chrome reads a JSON manifest from a specific filesystem path and launches a native host binary. That binary creates a **Unix domain socket** (e.g., `/tmp/claude-mcp-browser-bridge-<username>.sock`) that Claude Code's MCP subprocess connects to. Neither native messaging nor named pipes can cross Docker container boundaries. Investigation confirmed that `ss -tlnp | grep claude` shows **no listening TCP sockets**—there is nothing to port-forward.

VS Code's port forwarding, which works for web servers and other TCP-based services, is irrelevant here. The Chrome extension's discovery mechanism is file-based and loopback-only. Issue #25506 suggests three potential fixes—a WebSocket listener mode, a cloud relay, or better documentation—but **none have been implemented**. WSL support was added in Claude Code v2.1.0, but WSL is not Docker; the container boundary remains impassable.

The practical workaround is to **use Chrome DevTools MCP or Playwright MCP instead** when working inside a devcontainer. Claude Code's built-in `WebFetch` and `WebSearch` tools do work in containers since they're server-side (requests route through Anthropic's infrastructure), but these only read pages—they don't provide interactive browser automation.

## Chrome DevTools MCP works in containers with effort

Google's Chrome DevTools MCP (`chrome-devtools-mcp`) has **no Dockerfile or devcontainer.json** in its repository, but its architecture supports containerized use through configurable connection options. The server uses Puppeteer internally and communicates via the Chrome DevTools Protocol over HTTP or WebSocket, which means it can target any reachable Chrome instance.

Three viable container patterns exist:

**Connect to host Chrome** is the most common approach. Launch Chrome on the host with `--remote-debugging-port=9222`, then configure the MCP server inside the container with `--browserUrl=http://<host-ip>:9222`. The catch: Chrome's **Host header validation** rejects connections where the header doesn't match localhost, and Docker's resolved IP (e.g., `192.168.65.254`) triggers this rejection. The community project `null-runner/chrome-mcp-docker` works around this by spoofing the Host header.

**Run headless Chrome inside the container** is fully self-contained. Install `google-chrome-stable`, then run with `--headless --no-sandbox --isolated`. Several third-party Docker setups exist: `avi686/chrome-devtools-mcp-docker` (Docker Compose with browserless/chrome) and `dbalabka/chrome-wsl` (network proxy bridging for WSL and Docker).

**Use `--autoConnect` with Chrome 144+** allows the MCP server to request a debugging session from a running Chrome instance without needing `--remote-debugging-port` at launch. This simplifies the host-Chrome pattern but still requires network reachability.

Relevant GitHub issues include #131 (WSL access, 21 upvotes, now closed with workarounds documented), #261 (headless fails as root without `--no-sandbox`), and #292 (misleading error messages in headless environments).

## Summary comparison for devcontainer support

| Capability | Playwright MCP | Chrome DevTools MCP | Claude Code Chrome |
|---|---|---|---|
| Dockerfile in repo | **Yes** | No | N/A |
| Official Docker image | **Yes** (`mcr.microsoft.com/playwright/mcp`) | No | N/A |
| devcontainer.json in repo | No | No | No |
| Headless container mode | **Yes, first-class** | Yes, with manual setup | **Not possible** |
| Connect to host browser | Yes (`--cdp-endpoint`) | Yes (`--browserUrl`, `--wsEndpoint`) | **No** (native messaging only) |
| Community container solutions | Multiple (gists, repos) | Multiple (Docker Compose projects) | None viable |
| Key container flags | `--headless --no-sandbox --isolated --browser chromium` | `--headless --no-sandbox --browserUrl` | N/A |
| Open container-related issues | #891, #636, #1140 (all closed/resolved) | #261, #292, #509 | **#25506 (open, unresolved)** |

---

## The broader landscape of browser automation MCP tools

Beyond the three tools above, the ecosystem of browser automation servers for Claude Code and OpenCode is surprisingly rich. Here are the most significant options, organized by approach.

### Playwright-based tools dominate the official tier

**`@playwright/mcp` (Microsoft)** is the ecosystem standard. It uses accessibility tree snapshots rather than screenshots, supports Chromium, Firefox, and WebKit, and is explicitly documented for Claude Code, OpenCode, Cursor, VS Code, Codex CLI, GitHub Copilot, and over a dozen other clients. A newer CLI+Skills mode (`npx @playwright/mcp --cli`) is recommended for coding agents as it's more token-efficient than the full MCP protocol. The project ships multiple releases per week.

**`@executeautomation/playwright-mcp-server`** is a community alternative adding device emulation (143 device profiles), test code generation, and API testing support. It offers an HTTP server mode useful for remote or headed-on-headless setups.

### Puppeteer MCP servers fill niche roles

The **original `@modelcontextprotocol/server-puppeteer`** from Anthropic's reference implementations is now archived, with the ecosystem shifting toward Playwright MCP. It still works (15,600+ weekly npm downloads) but receives no updates.

**`puppeteer-real-browser-mcp-server`** by withLinda targets **stealth and anti-detection** use cases, bypassing common bot detection mechanisms. **`puppeteer-mcp-server`** by sultannaufal offers a self-hosted server with **remote SSE/HTTP access and API key authentication**, making it suitable for team or production deployments. **`puppeteer-vision-mcp`** integrates vision models (GPT-4.1) for AI-powered element detection on complex pages.

### Cloud and AI-powered options

**Browserbase MCP** (`@browserbasehq/mcp-server-browserbase`) runs browsers entirely in the cloud, eliminating local Chrome dependencies. It uses **Stagehand v3.0** for natural language browser control via `act()`, `extract()`, and `observe()` primitives—telling the browser "click the login button" rather than specifying CSS selectors. It supports proxies, advanced stealth, and persistent contexts. The tradeoff: it requires a paid Browserbase subscription and an LLM API key (Gemini by default). A community fork, **`stagehand-mcp-local`**, unlocks local mode without cloud services.

**Browser-Use** is the largest open-source browser automation platform at **78,500+ GitHub stars**. It offers both a hosted cloud MCP (`https://api.browser-use.com/mcp`) and a free local MCP (`uvx --from browser-use[cli] browser-use --mcp`). It can also be installed as a Claude Code skill. Its CLI provides persistent browser sessions between commands. The `mcp-browser-use` wrapper by Saik0s adds HTTP daemon transport for reliable long-running operations and includes a deep research tool.

### Tools that use your existing browser

**Dev-Browser by SawyerHood** (~2,500 stars) is a **Claude Code skill** (not an MCP server) purpose-built for development workflows. It can control your existing Chrome browser via a companion extension, preserving logged-in sessions and cookies. It uses Playwright under the hood and maintains persistent page state across script executions. It works with Claude Code natively and also supports Amp and Codex, but **not OpenCode** (which uses MCP, not skills).

**BrowserMCP** (`@browsermcp/mcp` from browsermcp.io) adapts Playwright MCP to automate your existing browser instance rather than creating new ones. It works with both Claude Code and OpenCode (documented in the OpenCode config examples) and preserves your real browser fingerprint for stealth.

**BrowserTools MCP** by AgentDeskAI combines a Chrome extension, Node server, and MCP server to capture screenshots, console logs, network activity, and run **Lighthouse audits** (accessibility, performance, SEO). It's focused on debugging rather than automation.

### OpenCode-specific options

OpenCode supports all MCP servers through its `opencode.json` configuration. **`@playwright/mcp` explicitly documents OpenCode** as a supported client. A purpose-built **`opencode-browser`** plugin by michaljach wraps BrowserMCP with auto-reconnection and exponential backoff retry logic designed for OpenCode's session management. All stdio-based MCP servers work with OpenCode's standard config pattern:

```json
{"mcp": {"<name>": {"type": "local", "command": ["npx", "<package>@latest"], "enabled": true}}}
```

## Conclusion

The devcontainer story has a clear winner: **Playwright MCP is the only tool with production-ready container support**, complete with an official Docker image and well-documented configuration. Chrome DevTools MCP is workable with manual setup, while Claude Code's native Chrome integration remains architecturally incompatible with containers and awaits a fix. For developers committed to devcontainers, the practical path is Playwright MCP with `--headless --browser chromium --no-sandbox --isolated`.

The broader ecosystem reveals an interesting split between tools that **launch fresh browsers** (Playwright MCP, Puppeteer servers, Browserbase) and tools that **connect to your existing browser** (Dev-Browser, BrowserMCP, BrowserTools). The first category works well in containers and CI; the second provides access to authenticated sessions but requires a host browser. Browser-Use bridges both approaches with its massive community and dual cloud/local modes. For OpenCode users, Playwright MCP's explicit documentation and the dedicated `opencode-browser` plugin make them the natural starting points.
