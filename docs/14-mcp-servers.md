# Part 14: MCP Servers

## What is MCP?

MCP (Model Context Protocol) extends Claude Code with additional tools by connecting to external servers.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MCP ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│  │             │         │             │         │             │               │
│  │ Claude Code │ ◄─────► │ MCP Server  │ ◄─────► │  Database   │               │
│  │             │         │             │         │             │               │
│  └─────────────┘         └─────────────┘         └─────────────┘               │
│                                                                                 │
│  MCP servers provide Claude Code with:                                          │
│  • Database access (query, understand schema)                                   │
│  • External API integration                                                     │
│  • Custom tools specific to your workflow                                       │
│  • Access to internal systems                                                   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Managing MCP Servers

Use the `claude mcp` command to manage servers:

```bash
# List configured servers and their status
claude mcp list

# Add an MCP server
claude mcp add <name> --transport stdio -- <command>

# Remove an MCP server
claude mcp remove <name>

# Get details about a server
claude mcp get <name>
```

## Example: Playwright MCP Server

The [Playwright MCP server](https://github.com/microsoft/playwright-mcp) lets Claude Code control a browser - navigate pages, click buttons, fill forms, take screenshots, and more.

### 1. Add the MCP Server

```bash
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest
```

### 2. Verify Connection

```bash
claude mcp list

# Output:
# playwright: npx @playwright/mcp@latest - ✓ Connected
```

### 3. Use in Claude Code

Once connected, you can control the browser directly:

```
> Open https://example.com and take a screenshot

> Go to https://news.ycombinator.com and list the top 5 headlines

> Navigate to our staging site, fill in the login form with test credentials,
  click submit, and tell me if the dashboard loads correctly

> Open localhost:3000, click the "Sign Up" button, and screenshot what you see
```

### Available Playwright Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_click` | Click an element |
| `browser_type` | Type text into an input |
| `browser_screenshot` | Capture a screenshot |
| `browser_snapshot` | Get accessibility tree of the page |
| `browser_select_option` | Select from dropdowns |
| `browser_press_key` | Press keyboard keys |
| `browser_tab_list` | List open tabs |
| `browser_tab_new` | Open new tab |
| `browser_console_messages` | Get console output |

### Configuration Options

```bash
# Run in headless mode (no visible browser)
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest --headless

# Use a specific browser
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest --browser firefox

# Run in Docker
docker run -i --rm --init mcr.microsoft.com/playwright/mcp
```

## Configuration File

MCP servers are stored in `~/.claude.json` or project-local config:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Other MCP Servers

```bash
# PostgreSQL database
claude mcp add postgres --transport stdio -- \
  npx -y @modelcontextprotocol/server-postgres \
  "postgresql://user:pass@localhost:5432/mydb"

# GitHub
claude mcp add github --transport stdio \
  --env GITHUB_TOKEN=your_token -- \
  npx -y @modelcontextprotocol/server-github

# Filesystem (read-only access to directories)
claude mcp add files --transport stdio -- \
  npx -y @modelcontextprotocol/server-filesystem /path/to/dir
```

## Checking MCP Status

Use `/mcp` in a Claude Code session to see connected servers and available tools:

```
> /mcp

MCP Servers:
  playwright (connected)
  └── Tools: browser_navigate, browser_click, browser_screenshot, ...
```
