# Part 22: LSP Plugins for Code Intelligence

## What are LSP Plugins?

Language Server Protocol (LSP) plugins give Claude Code real-time code intelligence: instant diagnostics, go-to-definition, find references, and hover documentation. Instead of relying solely on file reading and grep, Claude can use the same type system your IDE uses.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HOW LSP INTEGRATION WORKS                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌───────────────────┐    ┌──────────────────────┐     │
│  │ Claude Code  │◄──►│  LSP Plugin       │◄──►│  Language Server     │     │
│  │              │    │  (pyright-lsp)    │    │  (pyright-langserver)│     │
│  └──────────────┘    └───────────────────┘    └──────────────────────┘     │
│        │                                              │                     │
│        │         Types, diagnostics, definitions      │                     │
│        └──────────────────────────────────────────────┘                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Available LSP Plugins

Claude Code provides official plugins for major languages:

| Language   | Plugin Name          | Required Binary                |
|------------|----------------------|-------------------------------|
| Python     | `pyright-lsp`        | `pyright-langserver`          |
| TypeScript | `typescript-lsp`     | `typescript-language-server`  |
| Rust       | `rust-analyzer-lsp`  | `rust-analyzer`               |
| Go         | `gopls-lsp`          | `gopls`                       |
| C/C++      | `clangd-lsp`         | `clangd`                      |
| C#         | `csharp-lsp`         | `csharp-ls`                   |
| Java       | `jdtls-lsp`          | `jdtls`                       |
| Lua        | `lua-lsp`            | `lua-language-server`         |
| PHP        | `php-lsp`            | `intelephense`                |
| Swift      | `swift-lsp`          | `sourcekit-lsp`               |

## Installation

### Step 1: Install the Language Server Binary

The LSP plugin needs a language server to communicate with. Install it first.

**Python (Pyright)** - Use [pixi](https://pixi.sh/) (recommended):

```bash
# Add pyright to your project (recommended)
pixi add pyright

# The language server binary is then available as:
# .pixi/envs/default/bin/pyright-langserver
```

Using pixi keeps the dependency isolated to your project and version-controlled. Global installs via `pip install pyright` or `npm install -g pyright` are not recommended as they can conflict with project-specific versions.

**Other languages:**

```bash
# TypeScript
npm install -g typescript-language-server typescript

# Go
go install golang.org/x/tools/gopls@latest

# Rust (follow https://rust-analyzer.github.io/manual.html#installation)
```

### Step 2: Install the LSP Plugin

Using the interactive plugin manager:

```
/plugin
```

Navigate to the **Discover** tab and select the LSP plugin for your language.

Or install via command:

```
/plugin install pyright-lsp@claude-plugins-official
```

### Scope: Global vs Project

```bash
# Install for all projects (user scope)
/plugin install pyright-lsp@claude-plugins-official

# Install for current project only (project scope)
/plugin install pyright-lsp@claude-plugins-official --scope project
```

## Configuration

LSP servers can be configured at multiple levels:

| Scope | File | Shared with Team? |
|-------|------|-------------------|
| Project (team) | `.claude/settings.json` | Yes (commit to git) |
| Local (personal) | `.claude/settings.local.json` | No (gitignored) |
| Dedicated LSP | `.claude/.lsp.json` | Configurable |

### Basic Configuration

In `.claude/settings.json`:

```json
{
  "lspServers": {
    "python": {
      "command": "pixi",
      "args": ["run", "pyright-langserver", "--stdio"],
      "extensionToLanguage": {
        ".py": "python"
      }
    }
  }
}
```

This uses `pixi run` to invoke the project-local pyright-langserver. If you have pyright installed globally, you can use `"command": "pyright-langserver"` directly.

### Full Configuration Options

```json
{
  "lspServers": {
    "python": {
      "command": "pixi",
      "args": ["run", "pyright-langserver", "--stdio"],
      "extensionToLanguage": {
        ".py": "python"
      },
      "transport": "stdio",
      "env": {
        "PYTHONPATH": "/path/to/custom/pythonpath"
      },
      "initializationOptions": {
        "pythonPath": "/usr/bin/python3"
      },
      "settings": {
        "python.analysis.typeCheckingMode": "strict"
      },
      "workspaceFolder": "${CLAUDE_PROJECT_DIR}",
      "startupTimeout": 5000,
      "shutdownTimeout": 5000,
      "restartOnCrash": true,
      "maxRestarts": 3
    }
  }
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | LSP binary to execute (must be in PATH) |
| `args` | array | Command-line arguments for server |
| `extensionToLanguage` | object | Maps file extensions to language IDs |
| `transport` | string | Communication: `stdio` (default) or `socket` |
| `env` | object | Environment variables when starting server |
| `initializationOptions` | object | Options passed during server initialization |
| `settings` | object | Settings via `workspace/didChangeConfiguration` |
| `workspaceFolder` | string | Workspace folder path for server |
| `startupTimeout` | number | Max time to wait for startup (milliseconds) |
| `restartOnCrash` | boolean | Auto-restart if server crashes |
| `maxRestarts` | number | Maximum restart attempts before giving up |

## Important: BasedPyright Users

If your project uses [BasedPyright](https://github.com/DetachHead/basedpyright) for stricter type checking, you still need to install **plain pyright** for the LSP plugin:

```bash
# Your project may use basedpyright for CI
pip install basedpyright

# But the LSP plugin requires standard pyright
pip install pyright
```

The `pyright-lsp` plugin does not recognize `basedpyright` as a valid language server binary. The two tools share the same analysis engine, so type information will be consistent.

## Multi-Language Project Example

For projects with multiple languages:

```json
{
  "lspServers": {
    "python": {
      "command": "pixi",
      "args": ["run", "pyright-langserver", "--stdio"],
      "extensionToLanguage": {
        ".py": "python"
      },
      "settings": {
        "python.analysis.typeCheckingMode": "strict"
      }
    },
    "go": {
      "command": "gopls",
      "args": ["serve"],
      "extensionToLanguage": {
        ".go": "go"
      }
    },
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "extensionToLanguage": {
        ".ts": "typescript",
        ".tsx": "typescriptreact"
      }
    }
  }
}
```

## Debugging LSP Issues

### Check Plugin Status

```
/plugin
```

Go to the **Installed** tab to verify the LSP plugin is listed, then check the **Errors** tab for loading issues.

### Common Error: Binary Not Found

```
Error: Executable not found in $PATH
```

**Solution**: Install the language server binary:

```bash
pip install pyright
# Verify it's accessible
pyright-langserver --version
```

### Enable Debug Logging

```bash
claude --enable-lsp-logging
```

Logs are written to `~/.claude/debug/` directory.

### LSP Features Available

When properly configured, Claude Code gains:

- **Instant diagnostics**: Type errors highlighted immediately after edits
- **Go to definition**: Jump to where a symbol is defined
- **Find references**: Locate all usages of a function/class
- **Hover information**: Type signatures and documentation
- **Document symbols**: Quick navigation within files

## Summary

| Task | Command/File |
|------|--------------|
| Install plugin | `/plugin install pyright-lsp@claude-plugins-official` |
| Configure (team) | `.claude/settings.json` |
| Configure (personal) | `.claude/settings.local.json` |
| Debug issues | `/plugin` → Errors tab |
| Enable logging | `claude --enable-lsp-logging` |
