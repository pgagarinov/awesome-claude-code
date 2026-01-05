# Part 26: Extended Thinking (Thinking Mode)

Extended thinking reserves a portion of the output token budget for Claude to reason through complex problems step-by-step before responding. This internal reasoning process helps Claude work through challenging problems more thoroughly.

## When to Use Extended Thinking

Extended thinking is most valuable for:

- **Complex architectural decisions** - Evaluating tradeoffs between different approaches
- **Challenging bugs** - Reasoning through potential causes systematically
- **Multi-step implementation planning** - Breaking down complex tasks
- **Code review** - Thorough analysis of implications and edge cases

For simple tasks like file edits or straightforward questions, extended thinking adds unnecessary latency and cost.

## Model Support

| Model | Default Behaviour |
|-------|-------------------|
| Sonnet 4.5 | Thinking enabled by default |
| Opus 4.5 | Thinking enabled by default |
| Other models | Thinking disabled by default |

Use `/model` to view or switch your current model.

## Enabling Extended Thinking

### Per-Request: The `ultrathink` Keyword

Use `ultrathink` at the start of your prompt to enable thinking for a single request:

```
> ultrathink: design a caching layer for our API

> ultrathink: why is this race condition occurring in the worker pool?

> ultrathink: evaluate the security implications of this authentication flow
```

**Important**: `ultrathink` does two things:
1. Allocates the thinking token budget (up to 31,999 tokens)
2. Semantically signals Claude to reason more thoroughly

Other phrases like "think", "think hard", or "think deeply" are interpreted as regular prompt instructions and **do not** allocate thinking tokens. Only `ultrathink` triggers the dedicated thinking mode.

### Global Default

Enable thinking for all requests via `/config`:

```
/config
```

This saves `alwaysThinkingEnabled` to `~/.claude/settings.json`.

### Environment Variable

Set a custom thinking token budget that applies to all requests:

```bash
export MAX_THINKING_TOKENS=10000
```

When `MAX_THINKING_TOKENS` is set:
- It takes priority over both the default budget and `ultrathink`
- The specified budget applies to all requests
- `ultrathink` keyword has no additional effect

## Token Budgets

| Configuration | Thinking Tokens |
|--------------|-----------------|
| Thinking disabled | 0 |
| Thinking enabled (default) | Up to 31,999 |
| Custom (`MAX_THINKING_TOKENS`) | Your specified value |

See the [extended thinking documentation](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) for valid token ranges and detailed API information.

### Cost Implications

You are charged for all thinking tokens used. Claude 4 models display summarised thinking, but the full token count is billed.

## Viewing the Thinking Process

Press **Ctrl+O** to toggle verbose mode. When enabled, Claude's internal reasoning is displayed as grey italic text, allowing you to follow the step-by-step thought process.

## Priority Order

When multiple configurations exist, this is the priority:

1. `MAX_THINKING_TOKENS` environment variable (highest priority)
2. `ultrathink` keyword in prompt
3. `alwaysThinkingEnabled` in settings
4. Model default behaviour

## Practical Examples

### Architecture Decision

```
> ultrathink: We need to add real-time updates to our dashboard.
  Evaluate WebSockets vs Server-Sent Events vs polling for our
  use case. Consider our existing Express backend and React frontend.
```

### Debugging

```
> ultrathink: Users report intermittent 500 errors on the checkout
  endpoint. The error logs show "connection reset" but only under
  load. What could cause this?
```

### Security Review

```
> ultrathink: Review the authentication middleware in src/auth/
  for security vulnerabilities. Consider OWASP top 10.
```

### Without Thinking (Simple Tasks)

For straightforward tasks, skip `ultrathink` to save tokens and reduce latency:

```
> Add a created_at timestamp to the User model

> Fix the typo in the README

> What does the --verbose flag do?
```

## Reference

- [Claude Code Documentation: Extended Thinking](https://docs.anthropic.com/en/docs/claude-code/common-workflows#use-extended-thinking-thinking-mode)
- [Claude API: Extended Thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
