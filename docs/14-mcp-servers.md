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

## Example: PostgreSQL MCP Server

### 1. Start a PostgreSQL Database

```bash
# Start postgres in Docker
docker run -d --name postgres_test \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=testdb \
  -p 5433:5432 \
  postgres:16
```

### 2. Add the MCP Server

```bash
claude mcp add postgres --transport stdio -- \
  npx -y @modelcontextprotocol/server-postgres \
  "postgresql://testuser:testpass@localhost:5433/testdb"
```

### 3. Verify Connection

```bash
claude mcp list

# Output:
# postgres: npx -y @modelcontextprotocol/server-postgres ... - ✓ Connected
```

### 4. Use in Claude Code

Once connected, you can query the database directly:

```
> What tables are in the database?

> Show me the schema for the users table

> Find all orders with status 'pending'

> How many users signed up this month?
```

Claude Code will use the MCP server to execute queries and return results.

## Configuration File

MCP servers are stored in `~/.claude.json` or project-local config:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:pass@localhost:5432/mydb"
      ]
    }
  }
}
```

## Other MCP Servers

```bash
# GitHub
claude mcp add github --transport stdio \
  --env GITHUB_TOKEN=your_token -- \
  npx -y @modelcontextprotocol/server-github

# Filesystem (read-only access to directories)
claude mcp add files --transport stdio -- \
  npx -y @modelcontextprotocol/server-filesystem /path/to/dir

# Slack
claude mcp add slack --transport stdio \
  --env SLACK_TOKEN=your_token -- \
  npx -y @anthropic-ai/mcp-server-slack
```

## Checking MCP Status

Use `/mcp` in a Claude Code session to see connected servers and available tools:

```
> /mcp

MCP Servers:
  postgres (connected)
  └── Tools: query, list_tables, describe_table
```
