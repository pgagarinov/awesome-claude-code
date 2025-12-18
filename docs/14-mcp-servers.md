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
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│  │             │         │             │         │             │               │
│  │ Claude Code │ ◄─────► │ MCP Server  │ ◄─────► │  External   │               │
│  │             │         │             │         │    API      │               │
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

## Configuring MCP Servers

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["-m", "mcp_server_postgres"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Using MCP Tools

Once configured, MCP tools appear alongside built-in tools:

```
> /mcp

╭─ MCP Servers ───────────────────────────────────────────────────────────────────╮
│                                                                                 │
│  database (connected)                                                           │
│  ├── query          - Execute SQL query                                         │
│  ├── schema         - Get database schema                                       │
│  └── tables         - List all tables                                           │
│                                                                                 │
│  github (connected)                                                             │
│  ├── list_prs       - List pull requests                                        │
│  ├── get_issue      - Get issue details                                         │
│  └── create_pr      - Create pull request                                       │
│                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

```
> Show me the database schema for the users table

  [Using MCP: database.schema]

  Table: users
  ├── id (integer, primary key)
  ├── email (varchar(255), unique)
  ├── password_hash (varchar(255))
  ├── created_at (timestamp)
  └── updated_at (timestamp)
```
