# Browser-Use: autonomous browser agents vs MCP tools

Browser-Use is the largest open-source browser automation platform (~79K GitHub stars, ~330 commits/mo). It's fundamentally different from MCP browser tools — it's an **autonomous agent framework**, not a tool server exposing primitives. Where Playwright MCP and Chrome DevTools MCP give your agent individual browser commands to orchestrate step by step, Browser-Use runs its own agent loop that decides what to click, type, and navigate autonomously.

## At a glance: Browser-Use vs MCP tools

| Tool | Repo | Stars | Commits/mo | What it is | Who orchestrates | Protocol |
|---|---|---|---|---|---|---|
| **Browser-Use** | [browser-use/browser-use](https://github.com/browser-use/browser-use) | ~79K | ~330 | Autonomous agent | Browser-Use's agent loop | Raw CDP (`cdp-use`) |
| **Playwright MCP** | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | ~27.7K | ~40 | Tool server | Your agent (Claude) | Playwright + CDP |
| **Chrome DevTools MCP** | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | ~26.7K | ~100 | Tool server | Your agent (Claude) | CDP (Puppeteer) |

| Capability | Browser-Use | Playwright MCP | Chrome DevTools MCP |
|---|---|---|---|
| Best for | Open-ended exploration | Deterministic automation | Debugging loops |
| Auth state | Authenticated profiles | Fresh browser | Fresh browser |
| Bot detection | Stealth infra (fingerprints, proxies) | None | None |
| Token cost | Internal to agent | ~27K (CLI) / ~114K (MCP) | ~18K overhead |
| Browsers | Chrome only | Chromium, Firefox, WebKit, Edge | Chrome only |
| Container support | Yes | Yes (official image) | Manual setup |

## Timeline: Browser-Use's evolution

> 🚀 new launch · 🔀 migration · 💰 funding

- 🚀 **Nov 2024** — **Browser-Use created.** Magnus Muller and Gregor Zunic (ETH Zurich, later YC W25) built a Python framework letting LLMs control browsers. Went viral — 50K+ stars in 3 months. ([Show HN](https://news.ycombinator.com/item?id=42052432), [TechCrunch](https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/))
- 💰 **Mar 2025** — **Browser-Use raises $17M seed.** Led by Felicis with participation from YC, Paul Graham, and others. ([TechCrunch](https://techcrunch.com/2025/03/23/browser-use-the-tool-making-it-easier-for-ai-agents-to-navigate-websites-raises-17m/), [Browser-Use blog](https://browser-use.com/posts/seed-round))
- 🔀 **Aug 2025** · *Playwright → CDP* — **Browser-Use drops Playwright for raw CDP.** Found that Playwright's auto-waiting and actionability checks (designed for testing) added latency for AI automation. Built `cdp-use`, a type-safe Python CDP client. ([Browser-Use blog](https://browser-use.com/posts/playwright-to-cdp), [cdp-use on GitHub](https://github.com/browser-use/cdp-use))
- 🚀 **Sep 2025** — **Stealth infrastructure launched.** Fingerprint spoofing, anti-bot bypass across 195+ proxy locations. Solving the biggest practical barrier to autonomous web agents. ([Browser-Use blog](https://browser-use.com/posts/browser-infra))
- 🚀 **Oct 2025** — **"Fastest Web Agent" LLM gateway.** 6x latency reduction through optimized model routing. ([Browser-Use blog](https://browser-use.com/posts/llm-gateway))
- 🚀 **Nov 2025** — **Browser-Use 1.0 released.** One year milestone with stable API, production-ready agent framework. ([Browser-Use blog](https://browser-use.com/posts/browser-use-1.0))

## Architecture after the CDP migration (Aug 2025)

Browser-Use's migration from Playwright to raw CDP mirrors a broader industry trend (Stagehand v3 made the same move in Oct 2025, achieving 44% faster execution).

**Before (Playwright relay):**
```
Browser-Use agent → Playwright (Node.js) → WebSocket → CDP → Chrome
                    326KB overhead per call
```

**After (`cdp-use` library):**
```
Browser-Use agent → cdp-use (Python) → CDP → Chrome
                    Direct, no relay
```

Key wins from the migration:
- **Event-driven watchdogs** — real-time page state monitoring via CDP events
- **Cross-origin iframe super-selectors** — reach into iframes that Playwright's same-origin model blocked
- **No Node.js dependency** — pure Python stack, simpler deployment
- **15–20% faster** execution for typical agent workflows
- Source: [cdp-use on GitHub](https://github.com/browser-use/cdp-use)

This mirrors the **CDP boomerang** pattern across the ecosystem: Puppeteer wrapped CDP (2017), Playwright added another layer (2020), MCP added yet another (2024–25), then AI automation stripped the layers back off in 2025.

## When to use Browser-Use

### Scenarios where Browser-Use wins over MCP tools

- **Long autonomous tasks** — "Research competitor pricing across 15 sites" — Browser-Use handles the full navigation loop internally, reducing token cost vs. step-by-step MCP tool calls.
- **Sites that block bots** — Stealth infrastructure with fingerprint spoofing and 195+ proxy locations. MCP tools have no anti-detection features.
- **Authenticated workflows** — Reuse logged-in browser profiles. MCP tools start fresh browsers by default.
- **Python-native agent stacks** — If your orchestrator is Python-based, Browser-Use integrates natively without Node.js dependencies.

### Scenarios where MCP tools win

- **Playwright MCP** — Deterministic automation flows, multi-browser support (Chromium, Firefox, WebKit), accessibility tree snapshots, first-class Docker support, 4x token efficiency in CLI mode. Best when Claude is your orchestrator and you want fine-grained control.
- **Chrome DevTools MCP** — Debugging loops (code → run → inspect → fix), network interception, JavaScript injection, performance profiling with CrUX traces. Best for development workflows.
- **General MCP advantage** — MCP tools are low-level building blocks that Claude controls step by step. This means your agent sees every action's result, can adapt its strategy mid-task, and you maintain full observability. Browser-Use's internal agent loop is a black box from Claude's perspective.

## Setup options

**Hosted cloud MCP** (easiest, requires account):
```json
{"mcpServers": {"browser-use": {"url": "https://api.browser-use.com/mcp"}}}
```

**Free local MCP** (no account needed):
```bash
uvx --from browser-use[cli] browser-use --mcp
```

**Claude Code skill installation:**
```bash
# Browser-Use provides a skill for Claude Code integration
browser-use install --skill
```

**CLI with persistent browser sessions:**
```bash
uvx --from browser-use[cli] browser-use
```

**mcp-browser-use wrapper** by Saik0s — adds HTTP daemon transport for reliable long-running operations and includes a deep research tool:
- [GitHub: Saik0s/mcp-browser-use](https://github.com/Saik0s/mcp-browser-use)

## The orchestration question

The fundamental difference between Browser-Use and MCP tools is **who drives the browser**:

**MCP tools = low-level building blocks your agent controls step by step.**
Claude calls `browser_navigate`, reads the result, decides what to click, calls `browser_click`, reads the result, and so on. Every step is visible, debuggable, and steerable. Your agent is the orchestrator.

**Browser-Use = high-level agent that handles multi-step browser workflows internally.**
You give it a goal ("find the cheapest flight from SFO to JFK on March 15"), and Browser-Use's own agent loop handles navigation, form filling, comparison, and result extraction. Your agent delegates the entire workflow.

If Claude is already your orchestrator, MCP tools give you more control and observability. If you want to delegate entire browser workflows without managing each click, Browser-Use handles more autonomously — but you lose visibility into intermediate steps.

See [37-browser-automation.md](37-browser-automation.md) for the full browser automation ecosystem, container setup guides, and protocol landscape.
