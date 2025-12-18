# Claude Code Training Programme

```
   ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗     ██████╗ ██████╗ ██████╗ ███████╗
  ██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝
  ██║     ██║     ███████║██║   ██║██║  ██║█████╗      ██║     ██║   ██║██║  ██║█████╗
  ██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝      ██║     ██║   ██║██║  ██║██╔══╝
  ╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗    ╚██████╗╚██████╔╝██████╔╝███████╗
   ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝
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
11. [Multi-Modal: Screenshots & Images](docs/11-multimodal.md)
12. [Custom Slash Commands](docs/12-custom-commands.md)
13. [Skills](docs/13-skills.md)
14. [MCP Servers](docs/14-mcp-servers.md)
15. [Claude Agent SDK (Python)](docs/15-agent-sdk.md)
16. [GitHub Actions Integration](docs/16-github-actions.md)
17. [Best Practices & Tips](docs/17-best-practices.md)

---

## Quick Start

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Start Claude Code in any project
cd your-project
claude
```

## SDK Examples

Runnable Python examples demonstrating the Claude Agent SDK:

| Example | Description |
|---------|-------------|
| [01_basic_query.py](src/cc_training/examples/01_basic_query.py) | Simple query to Claude Code |
| [02_with_options.py](src/cc_training/examples/02_with_options.py) | Configuring options and parameters |
| [03_file_analysis.py](src/cc_training/examples/03_file_analysis.py) | Analyzing files in a project |
| [04_batch_processing.py](src/cc_training/examples/04_batch_processing.py) | Processing multiple items |
| [05_message_handling.py](src/cc_training/examples/05_message_handling.py) | Working with message streams |
| [06_code_reviewer.py](src/cc_training/examples/06_code_reviewer.py) | Building a code review tool |

### Running Examples

```bash
# Install dependencies
pixi install

# Run an example
pixi run python src/cc_training/examples/01_basic_query.py

# Run tests
pixi run pytest
```

## Project Structure

```
cc-training/
├── README.md                          # This file
├── docs/                              # Training documentation (17 parts)
├── src/cc_training/examples/          # SDK code examples
├── tests/                             # Test suite
└── pyproject.toml                     # Python project config
```

## Official Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Getting Started Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
