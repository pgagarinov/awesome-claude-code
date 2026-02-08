# Part 14: MCP Servers

## What is MCP?

MCP (Model Context Protocol) extends Claude Code with additional tools by connecting to external servers.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         MCP ARCHITECTURE                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│  │             │         │ Playwright  │         │             │               │
│  │ Claude Code │ ◄─────► │ MCP Server  │ ◄─────► │   Browser   │               │
│  │             │         │             │         │             │               │
│  └─────────────┘         └─────────────┘         └─────────────┘               │
│                                                                                 │
│  Example: "Navigate to staging and screenshot the dashboard"                    │
│                                                                                 │
│  1. Claude Code sends request to Playwright MCP                                 │
│  2. Playwright opens browser, navigates to URL                                  │
│  3. Playwright takes screenshot, returns to Claude                              │
│  4. Claude analyses the image and responds                                      │
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

For remote HTTP/SSE servers and OAuth setup, see the [official MCP documentation](https://code.claude.com/docs/en/mcp).

## Playwright MCP Server

The [Playwright MCP server](https://github.com/microsoft/playwright-mcp) lets Claude Code control a browser - navigate pages, click buttons, fill forms, take screenshots, and more.

### Setup

**Prerequisites:** A browser must be installed on your system. Playwright can use Chrome, Chromium, Firefox, or WebKit.

```bash
# Add the Playwright MCP server
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest

# Verify connection
claude mcp list
# Output: playwright: npx @playwright/mcp@latest - ✓ Connected
```

If the browser isn't found automatically, specify the path:

```bash
# Point to a specific browser executable
claude mcp add playwright --transport stdio -- \
  npx @playwright/mcp@latest --executable-path /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome

# Or install Playwright's bundled browsers
npx playwright install chromium
```

### Example 1: Navigate and Analyse a Page

```
> Open https://example.com and tell me what's on the page
```

Claude navigates to the URL and returns an accessibility snapshot showing all elements:

```yaml
- heading "Example Domain" [level=1]
- paragraph: This domain is for use in illustrative examples...
- link "More information..." [cursor=pointer]
```

### Example 2: Click Links and Navigate

```
> Click the "More information" link
```

Claude clicks the element and reports the new page state. It tracks navigation automatically.

### Example 3: Search and Fill Forms

```
> Go to duckduckgo.com, search for "Claude Code tutorial", and tell me the top results
```

Claude will:
1. Navigate to the search engine
2. Find the search input field
3. Type the query and submit
4. Return the search results

### Example 4: Take Screenshots

```
> Take a screenshot of the current page
```

Screenshots are saved to `.playwright-mcp/` directory and can be analysed by Claude.

### Example 5: Test a Login Flow

```
> Navigate to localhost:3000/login, enter "testuser" as username and "password123"
  as password, click the login button, and screenshot the result
```

### Example 6: Scrape Data from a Website

```
> Go to https://news.ycombinator.com and list the top 10 headlines with their URLs
```

Claude reads the page structure and extracts the requested data.

### Available Tools

| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to a URL |
| `browser_click` | Click an element on the page |
| `browser_type` | Type text into an input field |
| `browser_take_screenshot` | Capture a screenshot |
| `browser_snapshot` | Get accessibility tree of the page |
| `browser_select_option` | Select from dropdown menus |
| `browser_press_key` | Press keyboard keys (Enter, Tab, etc.) |
| `browser_tabs` | List, create, close, or select tabs |
| `browser_console_messages` | Get browser console output |
| `browser_navigate_back` | Go back to previous page |
| `browser_close` | Close the browser |

### Configuration Options

```bash
# Run in headless mode (no visible browser window)
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest --headless

# Use a specific browser
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest --browser firefox

# Run in Docker
docker run -i --rm --init mcr.microsoft.com/playwright/mcp
```

### Alternative: Python Libraries

You can achieve similar browser automation by asking Claude to write Python scripts using Playwright directly. See [MCP Servers vs Python Libraries](15-mcp-vs-python.md) for a detailed comparison of when to use each approach.

## Configuration File

MCP servers are stored in `~/.claude/settings.json` (user-level) or `.mcp.json` (project-level):

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

## Checking MCP Status

Use `/mcp` in a Claude Code session to see connected servers and available tools:

```
> /mcp

MCP Servers:
  playwright (connected)
  └── Tools: browser_navigate, browser_click, browser_take_screenshot, ...
```

## Finding More MCP Servers

Browse available MCP servers at:
- [Anthropic MCP Servers](https://github.com/anthropics/mcp-servers)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

## Remote MCP Servers

Claude Code supports three MCP transport types:

### Local Stdio (shown above)
```bash
claude mcp add playwright --transport stdio -- npx @playwright/mcp@latest
```

### Remote HTTP
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

### Remote SSE (deprecated)
```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse
```

### Authentication

Remote MCP servers use OAuth 2.0. Run `/mcp` in Claude Code to authenticate - tokens are stored securely and auto-refreshed.

## MCP Scopes

| Scope | Location | Shared | Use Case |
|-------|----------|--------|----------|
| Project | `.mcp.json` | Yes (git-committed) | Team-shared servers |
| Local | `.claude/settings.local.json` | No | Personal project servers |
| User | `~/.claude/settings.json` | No | Cross-project tools |

```bash
claude mcp add --scope project paypal https://mcp.paypal.com/mcp
claude mcp add --scope local mydb -- my-db-server
claude mcp add --scope user hubspot https://mcp.hubspot.com/anthropic
```

## Enabling and Disabling MCP Servers

Toggle MCP servers on or off during a session:

```
> /mcp enable playwright
> /mcp disable playwright
```
