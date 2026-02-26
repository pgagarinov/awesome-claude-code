# Awesome Claude Code — Documentation

Training materials and reference guides for mastering Claude Code.

## Guides

| # | Topic | Description |
|---|---|---|
| 01 | [Getting Started](01-getting-started.md) | Installation, first launch, basic usage |
| 02 | [The Claude Code Interface](02-interface.md) | UI elements, layout, visual conventions |
| 03 | [CLI Commands & Flags](03-cli-commands.md) | Command-line options and flags |
| 04 | [In-Session Commands](04-in-session-commands.md) | Slash commands available during a session |
| 05 | [Keyboard Shortcuts](05-keyboard-shortcuts.md) | Key bindings and customization |
| 06 | [CLAUDE.md & Information Architecture](06-claudemd-architecture.md) | Project memory files and structure |
| 07 | [Effective Prompting](07-effective-prompting.md) | Prompt engineering for Claude Code |
| 08 | [Context Management](08-context-management.md) | Managing context windows and token usage |
| 09 | [Working with Large Files](09-large-files.md) | Strategies for large codebases |
| 10 | [Subagents](10-subagents.md) | Spawning and managing sub-agents |
| 11 | [Skills](11-skills.md) | Built-in and custom skills |
| 12 | [Running Agents in Parallel](12-parallel-agents.md) | Parallel agent execution |
| 13 | [Claude Code Hooks](13-hooks.md) | Event-driven shell command hooks |
| 14 | [The Ralf Loop](14-ralf-loop.md) | Preventing premature stops |
| 15 | [Multi-Modal: Screenshots & Images](15-multimodal.md) | Image and screenshot workflows |
| 16 | [Custom Slash Commands](16-custom-commands.md) | Creating your own commands |
| 17 | [MCP Servers](17-mcp-servers.md) | Model Context Protocol servers |
| 18 | [MCP vs Python Libraries](18-mcp-vs-python.md) | When to use MCP vs native libraries |
| 19 | [Claude Agent SDK (Python)](19-agent-sdk.md) | Building agents with the Python SDK |
| 20 | [GitHub Actions Integration](20-github-actions.md) | CI/CD with Claude Code |
| 21 | [Best Practices & Tips](21-best-practices.md) | Collected best practices |
| 22 | [LSP Plugins for Code Intelligence](22-lsp-plugins.md) | Language Server Protocol integration |
| 23 | [SSH Multiplexing](23-ssh-multiplexing.md) | Remote development optimization |
| 24 | [Permission Settings & Hardening](24-permissions.md) | Security configuration |
| 25 | [Parallel Features](25-parallel-features.md) | Working on multiple features at once |
| 26 | [Dev Containers](26-dev-containers.md) | Docker-based development environments |
| 27 | [Extended Thinking](27-extended-thinking.md) | Thinking mode configuration |
| 28 | [Troubleshooting](28-troubleshooting.md) | Common issues and fixes |
| 29 | [Statusline Customization](29-statusline.md) | Status bar configuration |
| 30 | [Sandboxing](30-sandboxing.md) | OS-level sandbox isolation |
| 31 | [Output Styles](31-output-styles.md) | Controlling output formatting |
| 32 | [Plugins](32-plugins.md) | Plugin system |
| 33 | [Background Tasks](33-background-tasks.md) | Running tasks in the background |
| 34 | [Session Management](34-session-management.md) | Managing and resuming sessions |
| 35 | [OAuth Token Storage](35-oauth-token-storage.md) | Token and credential storage |
| 36 | [Native Sandbox vs Dev Containers](36-sandbox-vs-devcontainers.md) | Comparison guide for choosing an isolation strategy |
| 37 | [Browser Automation](37-browser-automation.md) | Browser automation tools in containers and beyond |
| 38 | [Browser-Use Deep Dive](38-browser-use.md) | Browser-Use architecture, CDP migration, and comparison with MCP tools |

## Highlighted Articles

### [Native Sandbox vs Dev Containers](36-sandbox-vs-devcontainers.md)

A decision guide comparing Claude Code's two isolation approaches. Native sandboxing (`/sandbox`) uses OS-level primitives for lightweight, zero-setup protection during interactive work. Dev containers provide hard Docker boundaries for autonomous workflows and CI/CD. Covers the permission fatigue problem, filesystem and network isolation layers, the Docker root problem, and when to reach for microVMs.

### [Browser Automation in Containers and Beyond](37-browser-automation.md)

Comprehensive survey of browser automation options for Claude Code and OpenCode. Playwright MCP is the only tool with first-class Docker support; Claude Code's built-in Chrome integration is architecturally blocked in containers. Covers Playwright MCP, Chrome DevTools MCP, Browser-Use, Browserbase, Dev-Browser, BrowserMCP, BrowserTools, browser pools for parallel testing, and OpenCode-specific options.

### [Browser-Use Deep Dive](38-browser-use.md)

Browser-Use (~79K stars) is an autonomous agent framework, not a tool server — fundamentally different from MCP browser tools. This guide covers the Playwright-to-CDP migration, architecture comparison with Playwright MCP and Chrome DevTools MCP, and when to use each approach.
