# Browser automation in containers and beyond

**Only Playwright MCP offers first-class Docker support for containerized development; Claude Code's built-in Chrome integration fundamentally cannot work in devcontainers, and Chrome DevTools MCP requires manual workarounds.** This gap matters because devcontainers are increasingly the standard for reproducible development environments, yet browser automation—critical for AI-assisted web development—remains a pain point inside them. The broader ecosystem offers over a dozen alternative MCP servers and tools, with Playwright MCP and Browser-Use emerging as the most actively maintained options for both Claude Code and OpenCode.

## At a glance

| Tool | Repo | Stars | Commits/mo | Browsers | Protocol(s) | Container? | Key limitations |
|---|---|---|---|---|---|---|---|
| **Browser-Use** | [browser-use/browser-use](https://github.com/browser-use/browser-use) | ~79K | ~330 | Chrome/Chromium | CDP (`cdp-use` library) | Yes | CAPTCHA limited; Chrome memory at scale. See [38-browser-use.md](38-browser-use.md) for deep dive |
| **Playwright MCP** | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | ~27.7K | ~40 | Chromium, Firefox, WebKit, Edge | Playwright protocol; CDP (`--cdp-endpoint`); Native Messaging (extension) | Yes (official image) | ~114K tokens/task in MCP mode (CLI: ~27K); Shadow DOM gaps |
| **Chrome DevTools MCP** | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | ~26.7K | ~100 | Chrome only | CDP (Puppeteer); WebSocket; HTTP | Manual setup | Chrome-only; verbose CDP responses |
| **BrowserTools MCP** | [AgentDeskAI/browser-tools-mcp](https://github.com/AgentDeskAI/browser-tools-mcp) | ~7.1K | 0 (Mar 2025) | Chrome | WebSocket + CDP (`chrome.debugger`) + Puppeteer | Host only | 3-component setup; monitoring-focused; **inactive** |
| **BrowserMCP** | [BrowserMCP/mcp](https://github.com/BrowserMCP/mcp) | ~5.9K | 0 (Apr 2025) | Chrome | WebSocket (custom extension protocol) | Host only | Extension closed-source; **inactive since Apr 2025** |
| **Dev-Browser** | [SawyerHood/dev-browser](https://github.com/SawyerHood/dev-browser) | ~3.7K | 0 (Jan 2026) | Chromium | Playwright + CDP + WebSocket | Host only | Claude Code skill only (not MCP) |
| **Browserbase MCP** | [browserbase/mcp-server-browserbase](https://github.com/browserbase/mcp-server-browserbase) | ~3.2K | 0 | Chromium-based (cloud) | CDP (Stagehand); Browserbase API | Yes (cloud) | Paid subscription; 0 recent commits |
| **Claude Code Chrome** | Built-in | N/A | N/A | Chrome | Chrome Native Messaging | No (arch. blocker) | Host-only; can't cross containers |

> **TL;DR for devcontainer users:** Use Playwright MCP with `--headless --browser chromium --no-sandbox --isolated`. It's the only option with production-ready container support out of the box.

---

## How we got here: a timeline of browser automation

> 🚀 new launch · 🔀 migration · 📦 archived · 💰 funding

### The foundation (2017–2020)

- 🚀 **Aug 2017** — **Google releases Puppeteer.** Chrome 59 shipped headless mode, but raw CDP was too low-level. Puppeteer wrapped CDP in a high-level Node.js API and became the browser automation standard. ([InfoQ](https://www.infoq.com/news/2017/08/google-puppeteer-headless-chrome/))
- 🚀 **Jan 2020** · *Puppeteer team → Microsoft* — **Microsoft announces Playwright.** Ex-Puppeteer engineers hired by Microsoft built a multi-browser alternative. Playwright shipped with Chromium, Firefox, and WebKit (the engine behind Safari) support from day one, solving Puppeteer's biggest limitation (Chrome-only). Internally, Playwright uses CDP for Chromium, a custom protocol for Firefox, and WebKit's debugging protocol. ([InfoQ](https://www.infoq.com/news/2020/01/playwright-browser-automation/))

### The AI agent era (2024)

- 💰 **Early 2024** — **Browserbase founded.** Paul Klein IV saw that AI agents would need cloud-hosted browsers at scale. Raised $6.5M seed led by Kleiner Perkins. ([VentureBeat](https://venturebeat.com/ai/exclusive-browserbase-launches-headless-browser-platform-that-lets-llms-automate-web-tasks))
- 🚀 **Oct 2024** · *builds on Playwright* — **Stagehand SDK announced.** Browserbase's AI browser automation framework providing `act()`/`extract()`/`observe()` methods on top of Playwright. ([Browserbase changelog](https://www.browserbase.com/changelog/announcing-stagehand))
- 🚀 **Nov 2024** — **Browser-Use created.** Magnus Muller and Gregor Zunic (ETH Zurich, later YC W25) built a Python framework letting LLMs control browsers. Went viral — 50K+ stars in 3 months, raised $17M in Mar 2025. ([Show HN](https://news.ycombinator.com/item?id=42052432), [TechCrunch](https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/))
- 🚀 **Nov 2024** · *new protocol* — **Anthropic ships MCP + Puppeteer MCP.** The Model Context Protocol standardized AI-tool integration. Puppeteer MCP was a day-one reference implementation — the first standardized way for LLMs to control browsers. ([Anthropic](https://www.anthropic.com/news/model-context-protocol))

### The MCP explosion (2025)

- 🚀 **Feb 2025** — **BrowserTools MCP v1.0.** AgentDesk built a Chrome extension + Node middleware + MCP server for Cursor developers who needed to see console logs and network requests. ([GitHub release](https://github.com/AgentDeskAI/browser-tools-mcp/releases))
- 🚀 **Mar 2025** — **Microsoft ships Playwright MCP.** Key innovation: structured accessibility snapshots instead of screenshots, no vision model needed. GitHub Copilot ships with it built in. Became the ecosystem's dominant browser MCP server. ([GitHub](https://github.com/microsoft/playwright-mcp), [Simon Willison](https://simonwillison.net/2025/Mar/25/playwright-mcp/))
- 🚀 **Apr 2025** — **BrowserMCP launched.** Took a different approach: a Chrome extension letting AI control your existing browser with sessions intact, solving the "headless browsers get blocked" problem. ([Show HN](https://news.ycombinator.com/item?id=43613194))
- 📦 **May 2025** · *Puppeteer MCP → Playwright MCP* — **Anthropic archives Puppeteer MCP.** Playwright MCP superseded it. The torch passed from Anthropic's reference implementation to Microsoft's production-grade server. ([GitHub archive](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/puppeteer))
- 🔀 **Aug 2025** · *Playwright → CDP* — **Browser-Use drops Playwright for raw CDP.** Found that Playwright's auto-waiting and actionability checks (designed for testing) added latency for AI automation. Built their own `cdp-use` Python library for direct CDP access. ([Browser-Use blog](https://browser-use.com/posts/playwright-to-cdp))
- 🚀 **Aug 2025** — **Anthropic launches Claude in Chrome preview.** First-party browser control, bypassing MCP entirely. Initially 1,000 Max plan users. ([Anthropic](https://claude.com/blog/claude-for-chrome), [TechCrunch](https://techcrunch.com/2025/08/26/anthropic-launches-a-claude-ai-agent-that-lives-in-chrome/))
- 🚀 **Sep 2025** — **Google ships Chrome DevTools MCP.** Google's response: a debugging-focused MCP server exposing Chrome's full DevTools toolkit (performance tracing, network monitoring, DOM inspection). Optimized for the code-run-inspect-fix loop. ([Google blog](https://developer.chrome.com/blog/chrome-devtools-mcp))
- 🔀 **Oct 2025** · *Playwright → CDP* — **Stagehand v3 drops Playwright for CDP.** Second major AI framework to abandon Playwright abstraction. 44% faster via direct CDP. ([Browserbase blog](https://www.browserbase.com/blog/stagehand-v3), [rationale](https://www.browserbase.com/blog/stagehand-playwright-evolution-browser-automation))
- 🚀 **Dec 2025** · *chose Skill over MCP* — **Dev-Browser released as a Claude Code Skill.** Sawyer Hood chose the Skill paradigm over MCP for persistent browser state across interactions. ([GitHub release](https://github.com/SawyerHood/dev-browser/releases))

### Key narrative: the CDP boomerang

Puppeteer wrapped CDP in a high-level API (2017). Playwright added another abstraction (2020). MCP added yet another (2024–25). Then in 2025, both Browser-Use and Stagehand stripped away the Playwright layer and went back to raw CDP — the abstractions designed for testing proved a poor fit for AI automation. The stack got taller, then snapped back.

### The "real browser" schism

A fundamental architectural split runs through the ecosystem: tools that **launch new browsers** (Playwright MCP, Chrome DevTools MCP, Browser-Use) vs. tools that **connect to your existing Chrome** with your sessions (BrowserMCP, BrowserTools MCP, Claude in Chrome, Dev-Browser). Clean-room automation vs. authenticated-session reuse.

---

## Protocol landscape: CDP, Playwright, BiDi, and custom

Four protocol families underpin every tool in this document:

**CDP (Chrome DevTools Protocol)** — Low-level WebSocket protocol native to Chrome/Chromium. Provides direct DOM, network, performance, and debugging access. Used by most tools either directly or via Puppeteer. **Chrome/Chromium-only by design** — this is CDP's fundamental limitation. Firefox and Safari/WebKit have their own internal debugging protocols, and CDP doesn't speak them. If you only need Chrome, CDP is the most powerful and direct option. Both Browser-Use and Stagehand migrated from Playwright to direct CDP in 2025 — eliminating Playwright's Node.js relay layer that caused state drift and latency in AI agent workloads.

**Playwright protocol** — Higher-level abstraction supporting Chromium, Firefox, and WebKit. Internally maps to CDP (Chromium), a custom protocol (Firefox), and WebKit's debugging protocol. Uses accessibility tree snapshots for page representation — more portable across browsers but can miss Shadow DOM elements. Playwright has an experimental **WebDriver BiDi** implementation (`packages/playwright-core/src/server/bidi/`) with files including `bidiOverCdp.ts`, `bidiBrowser.ts`, `bidiPage.ts`, `bidiFirefox.ts`, `bidiChromium.ts` — signaling a future where BiDi replaces the current per-browser protocol layer.

**WebDriver BiDi** — W3C standard-in-progress for bidirectional browser automation over WebSocket. Exists because CDP only works with Chrome — if you want the same event-driven capabilities (real-time console logs, network interception, DOM mutation events) across Firefox and Safari too, you need a cross-browser protocol. The older WebDriver Classic (used by Selenium for years) works across all browsers but is request-response only — your test sends a command and waits for a reply, with no way for the browser to push events back. BiDi combines Classic's cross-browser reach with CDP's bidirectional event streaming into a single W3C standard. Current adoption: Selenium 5 fully adopted; Puppeteer uses BiDi by default for Firefox; Cypress uses it for Firefox; Playwright has experimental implementation. Not yet feature-complete but represents the likely protocol convergence point.

**Custom/hybrid** — BrowserTools MCP uses Chrome extension → WebSocket → Node middleware (not CDP directly; Puppeteer only for Lighthouse audits). BrowserMCP uses extension → WebSocket → MCP server with a custom extension protocol. Claude Code Chrome uses Chrome Native Messaging (file-based, loopback-only).

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

### CLI+Skills mode: 4x token reduction

Playwright MCP offers two interaction modes with very different token economics:

**MCP mode** (default) returns complete accessibility trees, console output, and element metadata in tool responses. A typical browser automation task consumes ~114K tokens. Tool schema loading adds ~8% context overhead.

**CLI+Skills mode** is a separate package ([`@playwright/cli`](https://github.com/microsoft/playwright-cli)) designed for coding agents. Install globally and set up the skill:

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills
```

This creates a `.claude/skills/playwright-cli/SKILL.md` file that Claude Code discovers automatically. Commands are concise shell invocations: `playwright-cli goto [url]`, `snapshot`, `click e21`, `fill`, `screenshot`, `close`. State persists to `.playwright-cli/` as timestamped YAML snapshots with compact element IDs (`e21`, `e2609`) instead of full accessibility trees. Screenshots persist as PNGs on disk. Claude Code discovers capabilities from the `SKILL.md` file rather than loading a tool schema.

Result: ~27K tokens for the same task — roughly **4x reduction**. The Playwright team recommends CLI+Skills for coding agents managing large codebases where context window budget matters, and MCP mode for autonomous agent loops needing persistent browser context and richer tool responses.

## Claude Code's Chrome integration hits a hard architectural wall

Claude Code's built-in browser support (`claude --chrome` and the Claude in Chrome extension) **cannot work in devcontainers**. This is a confirmed open bug (GitHub issue #25506, filed February 13, 2026). The root cause is architectural, not a simple configuration gap.

The integration relies on **Chrome Native Messaging**, a host-local mechanism where Chrome reads a JSON manifest from a specific filesystem path and launches a native host binary. That binary creates a **Unix domain socket** (e.g., `/tmp/claude-mcp-browser-bridge-<username>.sock`) that Claude Code's MCP subprocess connects to. Neither native messaging nor named pipes can cross Docker container boundaries. Investigation confirmed that `ss -tlnp | grep claude` shows **no listening TCP sockets**—there is nothing to port-forward.

VS Code's port forwarding, which works for web servers and other TCP-based services, is irrelevant here. The Chrome extension's discovery mechanism is file-based and loopback-only. Issue #25506 suggests three potential fixes—a WebSocket listener mode, a cloud relay, or better documentation—but **none have been implemented**. WSL support was added in Claude Code v2.1.0, but WSL is not Docker; the container boundary remains impassable.

The practical workaround is to **use Chrome DevTools MCP or Playwright MCP instead** when working inside a devcontainer. Claude Code's built-in `WebFetch` and `WebSearch` tools do work in containers since they're server-side (requests route through Anthropic's infrastructure), but these only read pages—they don't provide interactive browser automation.

## Chrome DevTools MCP works in containers with effort

Google's Chrome DevTools MCP (`chrome-devtools-mcp`) has **no Dockerfile or devcontainer.json** in its repository, but its architecture supports containerized use through configurable connection options. The server uses Puppeteer internally and communicates via CDP over HTTP or WebSocket, which means it can target any reachable Chrome instance. It exposes 28 tools across 6 categories (DOM, network, performance, accessibility, console, screenshots), supports CrUX performance tracing, and auto-connects with Chrome 144+ via `--autoConnect`. Chrome-only by design.

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

### Secondary tools

| Tool | Repo | Stars | Status | Browsers | Protocol(s) |
|---|---|---|---|---|---|
| **@executeautomation/playwright-mcp** | [executeautomation/mcp-playwright](https://github.com/executeautomation/mcp-playwright) | ~5.3K | Slowing (Dec 2025) | Chromium, Firefox, WebKit | Playwright protocol |
| **Puppeteer MCP** (archived) | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | ~79K (monorepo) | Archived May 2025 | Chrome/Chromium | CDP |
| **puppeteer-vision-mcp** | [djannot/puppeteer-vision-mcp](https://github.com/djannot/puppeteer-vision-mcp) | ~47 | Minimal | Chrome | CDP + Vision API |
| **puppeteer-real-browser-mcp** | [withLinda/puppeteer-real-browser-mcp-server](https://github.com/withLinda/puppeteer-real-browser-mcp-server) | ~16 | Inactive (Aug 2025) | Chrome | CDP (stealth) |

### Playwright-based tools dominate the official tier

**`@playwright/mcp` (Microsoft)** is the ecosystem standard. It uses accessibility tree snapshots rather than screenshots, supports Chromium, Firefox, and WebKit, and is explicitly documented for Claude Code, OpenCode, Cursor, VS Code, Codex CLI, GitHub Copilot, and over a dozen other clients. The project ships multiple releases per week. See the CLI+Skills mode section above for how coding agents can cut token usage by 4x.

**`@executeautomation/playwright-mcp-server`** is a community alternative adding device emulation (143 device profiles), test code generation, and API testing support. It offers an HTTP server mode useful for remote or headed-on-headless setups. Activity has been slowing since Dec 2025.

### Puppeteer MCP servers fill niche roles

The **original `@modelcontextprotocol/server-puppeteer`** from Anthropic's reference implementations was **archived in May 2025**, with the ecosystem shifting toward Playwright MCP. CDP-based. It still works (15,600+ weekly npm downloads) but receives no updates.

**`puppeteer-real-browser-mcp-server`** by withLinda targets **stealth and anti-detection** use cases using CDP in stealth mode, bypassing common bot detection mechanisms. **Inactive since Aug 2025.** **`puppeteer-mcp-server`** by sultannaufal offers a self-hosted server with **remote SSE/HTTP access and API key authentication**, making it suitable for team or production deployments. **`puppeteer-vision-mcp`** integrates vision models (GPT-4.1) via CDP + Vision API for AI-powered element detection on complex pages.

### Cloud and AI-powered options

**Browserbase MCP** (`@browserbasehq/mcp-server-browserbase`) runs browsers entirely in the cloud, eliminating local Chrome dependencies. It uses **Stagehand v3.0** for natural language browser control via `act()`, `extract()`, and `observe()` primitives—telling the browser "click the login button" rather than specifying CSS selectors. Stagehand v3 dropped Playwright for direct CDP, achieving 44% faster execution. The MCP server itself has 0 recent commits. The tradeoff: it requires a paid Browserbase subscription and an LLM API key (Gemini by default). A community fork, **`stagehand-mcp-local`**, unlocks local mode without cloud services.

**Browser-Use** is the largest open-source browser automation platform (~79K stars, ~330 commits/mo). Unlike the MCP tools above, it's an **autonomous agent framework** — it runs its own agent loop rather than exposing primitives for Claude to orchestrate. It offers a hosted cloud MCP, a free local MCP, and a Claude Code skill. See [38-browser-use.md](38-browser-use.md) for architecture deep-dive, CDP migration details, and a full comparison with MCP tools.

### Tools that use your existing browser

**Dev-Browser by SawyerHood** (~3.7K stars) is a **Claude Code skill** (not an MCP server) purpose-built for development workflows. It uses Playwright under the hood with CDP for reconnection to your existing Chrome via a companion extension, preserving logged-in sessions and cookies. It maintains persistent page state across script executions. It works with Claude Code natively and also supports Amp and Codex, but **not OpenCode** (which uses MCP, not skills). Burst of 98 commits Dec–Jan 2026, then quiet. Chromium only.

**BrowserMCP** (`@browsermcp/mcp` from browsermcp.io) adapts Playwright MCP to automate your existing browser instance rather than creating new ones. Uses a custom WebSocket protocol (not CDP) with a **closed-source Chrome extension**. It works with both Claude Code and OpenCode (documented in the OpenCode config examples) and preserves your real browser fingerprint for stealth. **Inactive since Apr 2025.**

**BrowserTools MCP** by AgentDeskAI combines a Chrome extension, Node server, and MCP server to capture screenshots, console logs, network activity, and run **Lighthouse audits** (accessibility, performance, SEO). The Chrome extension uses `chrome.debugger` CDP access, communicates via WebSocket to the Node middleware, and falls back to Puppeteer only for Lighthouse. It's focused on debugging rather than automation. 3-component setup required. **Inactive since Mar 2025.**

### OpenCode-specific options

OpenCode supports all MCP servers through its `opencode.json` configuration. **`@playwright/mcp` explicitly documents OpenCode** as a supported client. A purpose-built **`opencode-browser`** plugin by michaljach wraps BrowserMCP with auto-reconnection and exponential backoff retry logic designed for OpenCode's session management. All stdio-based MCP servers work with OpenCode's standard config pattern:

```json
{"mcp": {"<name>": {"type": "local", "command": ["npx", "<package>@latest"], "enabled": true}}}
```

## Running a browser pool for parallel testing

### The Selenium Grid era and what replaced it

> 🚀 new launch · 📦 archived

- 🚀 **2011** — **Selenium Grid 2 ships.** Hub + Node architecture for distributing tests across machines. Became the standard for parallel browser testing. ([Selenium docs](https://www.selenium.dev/documentation/grid/))
- 🚀 **2016** — **Aerokube Selenoid released.** Lightweight Go alternative to Selenium Grid — one Docker container per browser session, no Java Hub. ([GitHub](https://github.com/aerokube/selenoid))
- 🚀 **2021** — **Selenium Grid 4 released.** Rebuilt architecture with Docker-native dynamic container spawning, observability, and distributed mode. ([Selenium blog](https://www.selenium.dev/blog/2021/selenium-4-0/))
- 📦 **Dec 2024** — **Aerokube archives Selenoid.** Not suited for Kubernetes. Recommends Moon as replacement. ([GitHub archive](https://github.com/aerokube/selenoid))
- 🚀 **2025** — **Aerokube Moon 2 released.** Kubernetes-native successor to Selenoid. Supports Selenium, Playwright, Puppeteer, Cypress. ([aerokube.com/moon](https://aerokube.com/moon/latest/))

### At a glance: browser pool solutions

| Tool | Repo | Stars | Commits/mo | Parallel model | Browsers | Protocol |
|---|---|---|---|---|---|---|
| **Playwright Test** | [microsoft/playwright](https://github.com/microsoft/playwright) | ~83K | ~200 | Workers + sharding | Chromium, Firefox, WebKit | Playwright protocol |
| **browserless** | [browserless/browserless](https://github.com/browserless/browserless) | ~12.6K | ~43 | Queue + concurrency pool | Chrome/Chromium | CDP / Puppeteer / Playwright |
| **docker-selenium** | [SeleniumHQ/docker-selenium](https://github.com/SeleniumHQ/docker-selenium) | ~8.6K | ~31 | Hub + Node containers | Chrome, Firefox, Edge | WebDriver / BiDi |
| **Browserbase** | [browserbase/mcp-server-browserbase](https://github.com/browserbase/mcp-server-browserbase) | ~3.2K | 0 | Cloud-managed pool | Chromium | CDP (Stagehand) |
| **Moon 2** | [aerokube.com/moon](https://aerokube.com/moon/latest/) | N/A (commercial) | N/A | K8s pods (up to 5000+) | Chrome, Firefox, Edge, Safari | Selenium / Playwright / CDP |
| **concurrent-browser-mcp** | [sailaoda/concurrent-browser-mcp](https://github.com/sailaoda/concurrent-browser-mcp) | ~7 | ~1 | Dynamic MCP instances | Chromium | Playwright MCP |

### Playwright's built-in parallelism (recommended starting point)

**Workers** (single machine):
- `npx playwright test --workers 4` — each worker gets its own browser context
- Default: auto-detected based on CPU cores
- 40-min suite → ~12–15 min with 4 workers
- [Playwright parallelism docs](https://playwright.dev/docs/test-parallel)

**Sharding** (multiple machines):
- `npx playwright test --shard=1/4` — distributes across CI jobs
- Use `fullyParallel: true` for test-level (not file-level) splitting
- Merge reports: `npx playwright merge-reports --reporter html ./all-blob-reports`
- 15–20 min local → 5–7 min across 4 shards
- [Playwright sharding docs](https://playwright.dev/docs/test-sharding)

This is the default recommendation — no infrastructure to manage, built into Playwright, works in CI/CD natively.

### Scaling beyond one machine

**Aerokube Moon 2** (Selenoid's successor):
- Kubernetes/OpenShift native
- Supports Selenium, Playwright, Puppeteer, Cypress
- Free tier: 4 parallel browser pods
- Manages clusters up to 5,000+ parallel browsers
- [aerokube.com/moon](https://aerokube.com/moon/latest/)

**Selenium Grid 4** (still actively maintained):
- Docker-native with dynamic container spawning
- Hub-Node model, good observability
- `docker-selenium` images (~8.6K stars) with all browsers pre-installed
- Best if you have an existing Selenium test suite
- [docker-selenium on GitHub](https://github.com/SeleniumHQ/docker-selenium)

**Browserless.io** (Docker + cloud):
- Headless browser service with built-in queuing (~12.6K stars)
- Configurable concurrency (`CONCURRENT=20`, `QUEUED=30`)
- Supports Puppeteer, Playwright, REST API
- Good for programmatic/headless-heavy workloads
- [browserless docs](https://docs.browserless.io/)

### MCP-based parallel patterns

For AI agent workflows (not traditional test suites):

**concurrent-browser-mcp** (community):
- Manages multiple parallel Playwright MCP instances
- Dynamic creation, configurable max (default: 20), auto-cleanup
- `npm install -g concurrent-browser-mcp`
- [GitHub](https://github.com/sailaoda/concurrent-browser-mcp)

**Multiple Playwright MCP containers:**
- Each container runs one MCP instance with its own browser
- Docker Compose + load balancer for distribution
- Use `--isolated` flag for clean separation
- [playwright-mcp-docker](https://github.com/iuill/playwright-mcp-docker)

**Browserbase** (cloud):
- Managed parallel browsers with Stagehand v3 (CDP)
- Native MCP support
- Eliminates local Chrome dependencies
- Paid subscription
- [browserbase.com/mcp](https://www.browserbase.com/mcp)

### Which browser pool to choose

| Scenario | Recommendation |
|---|---|
| Playwright test suite, single machine | Playwright workers (`--workers N`) |
| Playwright test suite, CI/CD | Playwright sharding (`--shard=X/N`) |
| Kubernetes at scale (500+ browsers) | Aerokube Moon 2 |
| Existing Selenium test suite | Selenium Grid 4 |
| Headless API/scraping workload | Browserless.io |
| Parallel AI agents via MCP | concurrent-browser-mcp |
| Cloud-managed, no infra to run | Browserbase |

---

## Conclusion

The devcontainer story has a clear winner: **Playwright MCP is the only tool with production-ready container support**, complete with an official Docker image and well-documented configuration. Its new CLI+Skills mode cuts token usage by 4x for coding agents. Chrome DevTools MCP is workable with manual setup, while Claude Code's native Chrome integration remains architecturally incompatible with containers and awaits a fix. For developers committed to devcontainers, the practical path is Playwright MCP with `--headless --browser chromium --no-sandbox --isolated`.

The timeline reveals a striking pattern: the **CDP boomerang**. The industry spent 2017–2024 building ever-higher abstractions over Chrome's raw protocol, then in 2025 the AI automation use case drove Browser-Use and Stagehand to strip those layers back off. Testing abstractions (auto-waiting, actionability checks) turned out to be liabilities for agent workloads that need direct, low-latency browser control.

The broader ecosystem splits between tools that **launch fresh browsers** (Playwright MCP, Chrome DevTools MCP, Browser-Use) and tools that **connect to your existing browser** (Dev-Browser, BrowserMCP, BrowserTools). The first category works well in containers and CI; the second provides access to authenticated sessions but requires a host browser. Meanwhile, the **protocol landscape is converging**: WebDriver BiDi aims to unify CDP's Chrome-specific power with cross-browser reach, and Playwright's experimental BiDi implementation suggests this convergence is underway.

For OpenCode users, Playwright MCP's explicit documentation and the dedicated `opencode-browser` plugin make them the natural starting points. For Claude Code users choosing between modes, CLI+Skills suits large-codebase workflows where context budget matters, while MCP mode suits autonomous agent loops needing rich browser state in tool responses.
