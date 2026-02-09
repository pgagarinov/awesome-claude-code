# Part 19: Claude Agent SDK

## Overview

The Claude Agent SDK allows you to control Claude Code programmatically - perfect for automation, CI/CD integration, and building custom tools. Available in both **TypeScript** and **Python**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SDK vs CLI                                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Aspect              │ CLI                    │ SDK                             │
│  ────────────────────┼────────────────────────┼──────────────────────────────── │
│  Interface           │ Interactive terminal   │ Code (async)                    │
│  Languages           │ Any (shell)            │ TypeScript, Python              │
│  Authentication      │ Browser OAuth          │ Uses existing CLI auth          │
│  Best for            │ Interactive work       │ Automation, scripts             │
│  Customisation       │ Slash commands         │ Full programmatic control       │
│                                                                                 │
│  KEY POINT: The SDK uses your existing Claude Code authentication.              │
│  If `claude` works in your terminal, the SDK works too.                         │
│  No API keys needed.                                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

See the [Claude Agent SDK documentation](https://platform.claude.com/docs/en/agent-sdk) for the complete API reference.

## Installation

### TypeScript SDK

```bash
npm install @anthropic-ai/claude-agent-sdk
```

### Python SDK

```bash
# Using pip
pip install claude-agent-sdk

# Using pixi (recommended)
pixi add --pypi claude-agent-sdk
```

**Note**: Requires zod ^4.0.0 as a peer dependency for TypeScript.

## SDK Components

| Component | Use Case |
|-----------|----------|
| `query()` | One-shot queries, batch processing, CI/CD |
| `ClaudeSDKClient` | Interactive sessions, conversations with follow-ups |
| `ClaudeAgentOptions` | Configuration (cwd, model, permissions, etc.) |

## Basic Usage

The SDK uses **async/await** - all queries are asynchronous.

### Simple Query

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    # Simple one-shot query
    async for message in query(prompt="What is 2 + 2?"):
        if hasattr(message, 'content'):
            print(message.content)

asyncio.run(main())
```

### Query with Options

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def explain_code():
    options = ClaudeAgentOptions(
        cwd="/path/to/project",           # Working directory
        model="claude-sonnet-4-5-20250929", # Model to use
        # permission_mode="bypassPermissions",  # For automation (use with caution)
    )

    async for message in query(
        prompt="Explain the main function in src/main.py",
        options=options,
    ):
        if hasattr(message, 'content'):
            print(message.content)

asyncio.run(explain_code())
```

### Handling Message Types

The SDK returns various message types. Use type-specific imports to handle them:

```python
import asyncio
from pathlib import Path
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock,
    ThinkingBlock,
    AssistantMessage,
    ResultMessage,
)

async def handle_messages():
    options = ClaudeAgentOptions(cwd=str(Path.cwd()))

    async for message in query(
        prompt="Read the first 5 lines of pyproject.toml",
        options=options
    ):
        if isinstance(message, AssistantMessage):
            # AssistantMessage may contain multiple content blocks
            if hasattr(message, 'content'):
                for block in (message.content if isinstance(message.content, list) else [message.content]):
                    if isinstance(block, TextBlock):
                        print(f"  Text: {block.text[:100]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  Tool: {block.name}")
                    elif isinstance(block, ThinkingBlock):
                        print(f"  Thinking: {block.thinking[:50]}...")

        elif isinstance(message, ResultMessage):
            print(f"Result: {message.content[:200] if hasattr(message, 'content') else message}")

asyncio.run(handle_messages())
```

### Parallel Batch Processing

Process multiple queries concurrently with `asyncio.gather`:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def collect_response(prompt: str, options: ClaudeAgentOptions | None = None) -> str:
    """Helper to collect full response from a query."""
    parts = []
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            parts.append(str(message.content))
    return "".join(parts)

async def main():
    questions = [
        "What is a Python decorator? (1 sentence)",
        "What is a Python generator? (1 sentence)",
        "What is a Python context manager? (1 sentence)",
    ]

    # Run all queries in parallel
    responses = await asyncio.gather(*[collect_response(q) for q in questions])

    for question, response in zip(questions, responses):
        print(f"Q: {question}\nA: {response}\n")

asyncio.run(main())
```

## Practical Examples

### Batch Code Review

```python
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def review_file(py_file: Path, directory: str) -> tuple[str, str]:
    """Review a single Python file."""
    options = ClaudeAgentOptions(cwd=directory)

    response_parts = []
    async for message in query(
        prompt=f"""Review {py_file} for:
        - Code quality issues
        - Potential bugs
        - Security vulnerabilities

        Be concise. List issues with line numbers.""",
        options=options
    ):
        if hasattr(message, 'content'):
            response_parts.append(str(message.content))

    return str(py_file), "".join(response_parts)


async def review_python_files(directory: str) -> dict[str, str]:
    """Review all Python files in a directory."""
    py_files = list(Path(directory).glob("**/*.py"))

    # Process files sequentially (or use asyncio.gather for parallel)
    results = {}
    for py_file in py_files:
        print(f"Reviewing {py_file}...")
        file_path, review = await review_file(py_file, directory)
        results[file_path] = review

    return results


async def main():
    reviews = await review_python_files("./src")

    for file, review in reviews.items():
        print(f"\n{'='*60}")
        print(f"FILE: {file}")
        print('='*60)
        print(review)

if __name__ == "__main__":
    asyncio.run(main())
```

### Automated Documentation Generator

```python
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def generate_module_docs(module_path: str) -> str:
    """Generate documentation for a Python module."""
    options = ClaudeAgentOptions(cwd=".")

    response_parts = []
    async for message in query(
        prompt=f"""Analyse {module_path} and generate documentation in Markdown:

        1. Module overview (2-3 sentences)
        2. List of classes with brief descriptions
        3. List of functions with signatures and descriptions
        4. Usage examples

        Output only the Markdown, no explanations.""",
        options=options
    ):
        if hasattr(message, 'content'):
            response_parts.append(str(message.content))

    return "".join(response_parts)


async def document_project(src_dir: str, output_dir: str):
    """Generate documentation for all modules in a project."""
    Path(output_dir).mkdir(exist_ok=True)

    for py_file in Path(src_dir).glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue

        print(f"Documenting {py_file}...")

        docs = await generate_module_docs(str(py_file))

        # Create output path
        relative = py_file.relative_to(src_dir)
        output_path = Path(output_dir) / relative.with_suffix(".md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(docs)
        print(f"  → {output_path}")


if __name__ == "__main__":
    asyncio.run(document_project("./src", "./docs/api"))
```

### Test Generator

```python
import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

async def generate_tests(source_file: str) -> str:
    """Generate pytest tests for a source file."""
    options = ClaudeAgentOptions(cwd=".")

    response_parts = []
    async for message in query(
        prompt=f"""Generate comprehensive pytest tests for {source_file}.

        Requirements:
        - Use pytest fixtures where appropriate
        - Include edge cases
        - Mock external dependencies
        - Follow AAA pattern (Arrange, Act, Assert)
        - Add docstrings explaining each test

        Output only the Python code, no explanations.""",
        options=options
    ):
        if hasattr(message, 'content'):
            response_parts.append(str(message.content))

    return "".join(response_parts)


async def generate_missing_tests(src_dir: str, test_dir: str):
    """Generate tests for source files that don't have them."""

    for src_file in Path(src_dir).glob("**/*.py"):
        if src_file.name.startswith("_"):
            continue

        # Determine expected test file path
        relative = src_file.relative_to(src_dir)
        test_file = Path(test_dir) / f"test_{relative}"

        if test_file.exists():
            print(f"Tests exist for {src_file}, skipping")
            continue

        print(f"Generating tests for {src_file}...")

        tests = await generate_tests(str(src_file))

        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(tests)
        print(f"  → {test_file}")


if __name__ == "__main__":
    asyncio.run(generate_missing_tests("./src", "./tests"))
```

### Custom Code Analysis Tool

```python
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions

@dataclass
class SecurityIssue:
    file: str
    line: int
    severity: str
    description: str
    recommendation: str


async def security_scan(directory: str) -> list[SecurityIssue]:
    """Scan a directory for security issues."""
    options = ClaudeAgentOptions(cwd=directory)

    response_parts = []
    async for message in query(
        prompt=f"""Perform a security audit of the Python code in {directory}.

        Look for:
        - SQL injection vulnerabilities
        - Command injection
        - Hardcoded secrets
        - Insecure deserialization
        - Path traversal
        - XSS vulnerabilities

        Output as JSON array with this structure:
        [{{
            "file": "path/to/file.py",
            "line": 42,
            "severity": "high|medium|low",
            "description": "What the issue is",
            "recommendation": "How to fix it"
        }}]

        Output ONLY the JSON, no other text.""",
        options=options
    ):
        if hasattr(message, 'content'):
            response_parts.append(str(message.content))

    # Parse the JSON response
    response_text = "".join(response_parts)
    issues_data = json.loads(response_text)

    return [SecurityIssue(**issue) for issue in issues_data]


def print_security_report(issues: list[SecurityIssue]):
    """Print a formatted security report."""

    print("\n" + "="*70)
    print("SECURITY SCAN REPORT")
    print("="*70)

    # Group by severity
    high = [i for i in issues if i.severity == "high"]
    medium = [i for i in issues if i.severity == "medium"]
    low = [i for i in issues if i.severity == "low"]

    for severity, items in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
        if items:
            print(f"\n{severity} SEVERITY ({len(items)} issues)")
            print("-"*40)
            for issue in items:
                print(f"\n  File: {issue.file}:{issue.line}")
                print(f"  Issue: {issue.description}")
                print(f"  Fix: {issue.recommendation}")

    print("\n" + "="*70)
    print(f"Total: {len(high)} high, {len(medium)} medium, {len(low)} low")
    print("="*70)


async def main():
    issues = await security_scan("./src")
    print_security_report(issues)


if __name__ == "__main__":
    asyncio.run(main())
```

### Integration with Pre-commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook using Claude Agent SDK."""

import asyncio
import subprocess
import sys
from claude_agent_sdk import query, ClaudeAgentOptions

def get_staged_files() -> list[str]:
    """Get list of staged Python files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True
    )
    return [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]


async def review_changes() -> tuple[bool, str]:
    """Review staged changes for issues."""

    files = get_staged_files()
    if not files:
        return True, "No Python files to review"

    options = ClaudeAgentOptions(cwd=".")

    response_parts = []
    async for message in query(
        prompt=f"""Review the staged changes (git diff --cached) for critical issues only:

        Files changed: {', '.join(files)}

        Check for:
        1. Obvious bugs (null references, infinite loops, etc.)
        2. Security vulnerabilities
        3. Syntax errors

        If there are critical issues, output them clearly.
        If no critical issues, just say "LGTM".

        Be concise.""",
        options=options
    ):
        if hasattr(message, 'content'):
            response_parts.append(str(message.content))

    response = "".join(response_parts).strip()

    if "LGTM" in response:
        return True, response
    else:
        return False, response


if __name__ == "__main__":
    passed, message = asyncio.run(review_changes())
    print(message)
    sys.exit(0 if passed else 1)
```

## TypeScript SDK Usage

```typescript
import { query, type ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

const options: ClaudeAgentOptions = {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-5-20250929",
  maxBudgetUsd: 5.0,
};

// Simple query
for await (const message of query({ prompt: "Explain this codebase", options })) {
  if (message.type === "text") {
    console.log(message.content);
  }
}
```

### Tool Confirmation (canUseTool)

Control tool execution with a callback:

```typescript
const result = await query({
  prompt: "Fix the bug in auth.py",
  options: {
    canUseTool: async (toolName, toolInput) => {
      if (toolName === "Bash" && toolInput.command.includes("rm")) {
        return false; // Deny destructive commands
      }
      return true;
    },
  },
});
```

### Custom Callback Tools

Register custom tools that Claude can invoke:

```typescript
const result = await query({
  prompt: "Deploy the app",
  options: {
    tools: [
      {
        name: "deploy",
        description: "Deploy to staging",
        inputSchema: { type: "object", properties: { env: { type: "string" } } },
        callback: async (input) => {
          // Custom deployment logic
          return { success: true };
        },
      },
    ],
  },
});
```

### Request Cancellation

Cancel a running query:

```typescript
const controller = new AbortController();

// Cancel after 30 seconds
setTimeout(() => controller.abort(), 30000);

for await (const message of query({
  prompt: "Analyse the entire codebase",
  options: { signal: controller.signal },
})) {
  console.log(message);
}
```

## SDK Configuration Options

### Python

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# All available options
options = ClaudeAgentOptions(
    cwd="/path/to/project",              # Working directory
    model="claude-sonnet-4-5-20250929",    # Model to use
    system_prompt="You are a code expert", # Custom system prompt
    permission_mode="default",           # "default", "acceptEdits", "bypassPermissions"
    max_turns=10,                        # Limit conversation turns
    continue_conversation=False,         # Resume previous session
    max_budget_usd=5.0,                  # Maximum spend in USD
)
```

### TypeScript

```typescript
import type { ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

const options: ClaudeAgentOptions = {
  cwd: "/path/to/project",
  model: "claude-sonnet-4-5-20250929",
  systemPrompt: "You are a code expert",
  permissionMode: "default",
  maxTurns: 10,
  maxBudgetUsd: 5.0,
  canUseTool: async (tool, input) => true,
};
```

### Key Options

| Option | Description |
|--------|-------------|
| `cwd` | Working directory |
| `model` | Model to use |
| `system_prompt` / `systemPrompt` | Custom system prompt |
| `permission_mode` / `permissionMode` | Permission level |
| `max_turns` / `maxTurns` | Limit conversation turns |
| `max_budget_usd` / `maxBudgetUsd` | Maximum spending budget (USD) |
| `canUseTool` | Callback for tool confirmation (TS only) |

### Cost Tracking

The SDK returns `total_cost_usd` in results for budget monitoring.
