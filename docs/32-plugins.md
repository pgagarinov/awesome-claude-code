# Part 32: Plugins

## What Are Plugins?

Plugins extend Claude Code with custom commands, agents, hooks, MCP servers, and output styles from marketplaces. They are a modular way to share and install extensions.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         PLUGIN SYSTEM                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Plugin Marketplace                                                            │
│       │                                                                        │
│       ▼                                                                        │
│  /plugin install <name>                                                        │
│       │                                                                        │
│       ▼                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐              │
│  │  Plugin provides:                                            │              │
│  │  • Commands & Skills    (appear in /skills menu)             │              │
│  │  • Custom Agents        (available via Task tool)            │              │
│  │  • Hooks                (PreToolUse, PostToolUse, etc.)      │              │
│  │  • MCP Servers          (additional tools)                   │              │
│  │  • Output Styles        (formatting presets)                 │              │
│  └──────────────────────────────────────────────────────────────┘              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Managing Plugins

### Install a Plugin

```
> /plugins

# Or directly:
> /plugin install <plugin-name>
```

The `/plugins` command provides tabs for:
- **Discover** — Browse available plugins from marketplaces
- **Installed** — Manage installed plugins with scope-based grouping

### Enable/Disable Plugins

```
> /plugin enable <name>
> /plugin disable <name>
```

### Validate a Plugin

Check plugin structure and configuration:

```
> /plugin validate <path-to-plugin>
```

### Uninstall a Plugin

```
> /plugin uninstall <name>
```

## Plugin Marketplaces

Plugins are sourced from git-based marketplaces. Claude Code has a default marketplace, and teams can add custom ones.

### Adding Custom Marketplaces

Configure additional marketplaces in `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": [
    "github.com/my-org/claude-plugins"
  ]
}
```

### Marketplace Features

- **Search** — Type to filter plugins by name, description, or marketplace
- **Auto-update** — Toggle automatic updates per marketplace
- **Branch support** — Pin to specific branches using `owner/repo#branch`

## Plugin Pinning

Pin plugins to specific git commit SHAs for reproducibility:

```json
{
  "plugins": {
    "my-plugin": {
      "source": "github.com/org/plugin",
      "pin": "abc123def456"
    }
  }
}
```

Marketplace entries can specify exact versions via SHA pinning.

## Auto-Update Control

Control automatic updates per marketplace:

```
> /plugins
# Navigate to marketplace settings
# Toggle auto-update on/off
```

Or set `FORCE_AUTOUPDATE_PLUGINS=1` to force updates even when the main auto-updater is disabled.

## What Plugins Can Provide

### Commands and Skills

Plugin-provided skills appear in the `/skills` menu with the plugin name:

```
> /skills

Plugin Skills:
  /deploy [my-plugin]     Deploy to staging or production
  /lint [my-plugin]       Run comprehensive linting
```

### Agents

Custom agents from plugins are available via the Task tool.

### Hooks

Plugins can provide command and prompt-based hooks that run alongside your project hooks.

### MCP Servers

Plugin-provided MCP servers are managed in the `/plugins` installed tab alongside regular MCP servers.

### Output Styles

> **Note**: Output styles were deprecated in v2.0.30. Use `--system-prompt`, `--system-prompt-file`, or CLAUDE.md instructions instead.

Plugins can share output style presets. Install and activate via `/output-style`.

## Plugin Structure

A plugin is a git repository with a specific structure:

```
my-plugin/
├── plugin.json          # Plugin manifest
├── commands/            # Slash commands / skills
│   └── deploy.md
├── agents/              # Custom agents
│   └── reviewer.md
├── hooks/               # Hook scripts
│   └── pre-commit.py
└── mcp/                 # MCP server configs
    └── config.json
```

## Diagnostics

Use `/doctor` to diagnose plugin issues:

```
> /doctor
# Shows plugin health, marketplace connectivity, validation errors
```

## Official Documentation

- [Plugins Documentation](https://code.claude.com/docs/en/plugins)
- [Plugin Announcement](https://www.anthropic.com/news/claude-code-plugins)
