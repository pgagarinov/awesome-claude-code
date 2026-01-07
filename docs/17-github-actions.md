# Part 17: GitHub Actions Integration

## Automated PR Reviews

For quick setup, run `/install-github-app` in Claude Code. See the [official GitHub Actions docs](https://code.claude.com/docs/en/github-actions) for AWS Bedrock and Vertex AI integration.

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: review
```

## Issue Triage

```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: triage
          issue_number: ${{ github.event.issue.number }}
```

## Security Review on PRs

```yaml
# .github/workflows/security-review.yml
name: Security Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: |
            Perform a security review of the changes in this PR.
            Focus on:
            - Authentication/authorization issues
            - Input validation
            - SQL injection
            - XSS vulnerabilities
            - Sensitive data exposure

            Report findings as comments on specific lines.
```

## Action Parameters

| Parameter | Description |
|-----------|-------------|
| `prompt` | Instructions for Claude (text or slash command) |
| `claude_args` | CLI arguments: `--max-turns 5 --model claude-sonnet-4-5-20250929` |
| `anthropic_api_key` | API key (required for direct API) |
| `trigger_phrase` | Custom trigger (default: `@claude`) |
| `use_bedrock` | Use AWS Bedrock |
| `use_vertex` | Use Google Vertex AI |

### Example with Options

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "/review"
    claude_args: "--max-turns 5 --model claude-sonnet-4-5-20250929"
```
