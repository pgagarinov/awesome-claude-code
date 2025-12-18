# Claude Code Training Programme

A comprehensive guide to mastering Claude Code - from first launch to advanced automation.

## Quick Start

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Start Claude Code in any project
cd your-project
claude
```

## Training Materials

**[Start the Training Programme](claude-code-training-programme.md)** - The complete guide covering:

1. Getting Started - Installation and first launch
2. The Claude Code Interface - Understanding the terminal UI
3. CLI Commands & Flags - Command-line options
4. In-Session Commands - Slash commands like `/help`, `/status`
5. Keyboard Shortcuts - Essential key bindings
6. CLAUDE.md & Information Architecture - Project documentation
7. Effective Prompting - Getting the best results
8. Context Management - Working within token limits
9. Working with Large Files - Strategies for big codebases
10. Subagents - Delegating tasks to specialized agents
11. Multi-Modal - Screenshots and images
12. Custom Slash Commands - Creating your own commands
13. Skills - Reusable capability packages
14. MCP Servers - Model Context Protocol integrations
15. Claude Agent SDK - Python automation
16. GitHub Actions Integration - CI/CD workflows
17. Best Practices & Tips - Expert recommendations

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
├── claude-code-training-programme.md  # Main training document
├── src/cc_training/examples/          # SDK code examples
├── tests/                             # Test suite
└── pyproject.toml                     # Python project config
```

## Official Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Getting Started Guide](https://docs.anthropic.com/en/docs/claude-code/getting-started)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
