# Awesome Claude Code

```
  ┃
  ┃  ░▒▓██████████████████████████████████████████████▓▒░
  ┃
  ┃    ┌─┐ ┬ ┬ ┌─┐ ┌─┐ ┌─┐ ┌┬┐ ┌─┐
  ┃    ├─┤ │││ ├┤  └─┐ │ │ │││ ├┤                     ◈ v2.0
  ┃    ┘ └ └┴┘ └─┘ └─┘ └─┘ ┘ └ └─┘
  ┃
  ┃  ────────────────────────────────────────────────────
  ┃
  ┃     ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
  ┃    ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
  ┃    ██║     ██║     ███████║██║   ██║██║  ██║█████╗
  ┃    ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝
  ┃    ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
  ┃     ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝
  ┃
  ┃     ██████╗ ██████╗ ██████╗ ███████╗
  ┃    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ┃    ██║     ██║   ██║██║  ██║█████╗
  ┃    ██║     ██║   ██║██║  ██║██╔══╝
  ┃    ╚██████╗╚██████╔╝██████╔╝███████╗
  ┃     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
  ┃
  ┃  ────────────────────────────────────────────────────
  ┃
  ┃    ◇── tips ── tricks ── tools ── workflows ──◇
  ┃
  ┃  ░▒▓██████████████████████████████████████████████▓▒░
  ┃
```

A comprehensive guide to mastering Claude Code - from first launch to advanced automation.

---

## Table of Contents

1. [Getting Started](docs/01-getting-started.md)
2. [The Claude Code Interface](docs/02-interface.md)
3. [CLI Commands & Flags](docs/03-cli-commands.md)
4. [In-Session Commands](docs/04-in-session-commands.md)
5. [Keyboard Shortcuts](docs/05-keyboard-shortcuts.md)
6. [CLAUDE.md & Information Architecture](docs/06-claudemd-architecture.md)
7. [Effective Prompting](docs/07-effective-prompting.md)
8. [Context Management](docs/08-context-management.md)
9. [Working with Large Files](docs/09-large-files.md)
10. [Subagents](docs/10-subagents.md)
11. [Skills](docs/11-skills.md)
12. [Running Agents in Parallel](docs/12-parallel-agents.md)
13. [Claude Code Hooks](docs/13-hooks.md)
14. [The Ralf Loop - Preventing Premature Stops](docs/14-ralf-loop.md)
15. [Multi-Modal: Screenshots & Images](docs/15-multimodal.md)
16. [Custom Slash Commands](docs/16-custom-commands.md)
17. [MCP Servers](docs/17-mcp-servers.md)
18. [MCP vs Python Libraries](docs/18-mcp-vs-python.md)
19. [Claude Agent SDK (Python)](docs/19-agent-sdk.md)
20. [GitHub Actions Integration](docs/20-github-actions.md)
21. [Best Practices & Tips](docs/21-best-practices.md)
22. [LSP Plugins for Code Intelligence](docs/22-lsp-plugins.md)
23. [SSH Multiplexing for Remote Development](docs/23-ssh-multiplexing.md)
24. [Permission Settings & Hardening](docs/24-permissions.md)
25. [Working on Multiple Features in Parallel](docs/25-parallel-features.md)
26. [Dev Containers with Claude Code](docs/26-dev-containers.md)
27. [Extended Thinking (Thinking Mode)](docs/27-extended-thinking.md)
28. [Troubleshooting](docs/28-troubleshooting.md)
29. [Statusline Customization](docs/29-statusline.md)
30. [Sandboxing](docs/30-sandboxing.md)
31. [Output Styles](docs/31-output-styles.md)
32. [Plugins](docs/32-plugins.md)
33. [Background Tasks](docs/33-background-tasks.md)
34. [Session Management](docs/34-session-management.md)
35. [OAuth Token Storage](docs/35-oauth-token-storage.md)
36. [Native Sandbox vs Dev Containers](docs/36-sandbox-vs-devcontainers.md)
37. [Browser Automation](docs/37-browser-automation.md)

---

## Quick Start

```bash
# Install Claude Code (macOS/Linux)
curl -fsSL https://claude.ai/install.sh | bash

# Start Claude Code in any project
cd your-project
claude
```

## Official Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Getting Started Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

## Ecosystem & Community

### Multi-Agent Orchestration

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — 32 specialized agents and 7 execution modes for Claude Code, with smart model routing and automatic parallelization
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — Agent harness plugin for OpenCode with multi-model orchestration, specialized agents (Sisyphus, Hephaestus, Oracle), and LSP/AST tools
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams) — Official docs for native multi-agent coordination (launched with Opus 4.6)
- [Claude Code Custom Agents](https://code.claude.com/docs/en/custom-agents) — Official guide for creating specialized agent definitions
- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents) — Official docs for spawning sub-agents from the task tool

### AI Coding Agents

- [OpenCode](https://github.com/sst/opencode) — Open-source, provider-agnostic terminal AI coding agent supporting Claude, OpenAI, Google, and local models
- [OpenClaw](https://openclaw.ai/) ([GitHub](https://github.com/openclaw/openclaw)) — Open-source personal AI assistant with 50+ integrations (WhatsApp, Telegram, Discord, Slack, Gmail, GitHub) and persistent memory

### Developer Tools

- [grep.app](https://grep.app/) — Code search engine across a million GitHub repositories — find implementations, examples, and patterns across open source
- [git-delta](https://github.com/dandavison/delta) — Syntax-highlighting pager for git diffs (pre-installed in the [devcontainer example](examples/06-pixi-devcontainer))

### Articles & Guides

- [The Ever-Changing AI Coding Agent Ecosystem](https://jeongil.dev/en/blog/trends/claude-code-agent-teams/) — Deep dive on the multi-agent landscape: Claude Code Agent Teams, community frameworks, and the ecosystem's evolution
- [Building Agent Teams in OpenCode](https://dev.to/uenyioha/porting-claude-codes-agent-teams-to-opencode-4hol) — Architecture walkthrough of porting multi-agent coordination to OpenCode with event-driven messaging and multi-provider support
- [Claude Opus 4.6 Announcement](https://www.anthropic.com/news/claude-opus-4-6) — Release announcement including Agent Teams introduction
