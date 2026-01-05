# Part 10: Subagents

## What Are Subagents?

Subagents are separate Claude instances that handle specific tasks with their **own isolated context**.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         HOW SUBAGENTS WORK                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      MAIN SESSION (Your Context)                        │   │
│  │                                                                         │   │
│  │  You: "Find all security vulnerabilities in the codebase"               │   │
│  │                              │                                          │   │
│  │                              ▼                                          │   │
│  │                    [Spawns Subagent]                                    │   │
│  └──────────────────────────────┼──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    SUBAGENT (Separate Context)                          │   │
│  │                                                                         │   │
│  │  • Reads 20+ files                                                      │   │
│  │  • Searches patterns                                                    │   │
│  │  • Analyses code                                                        │   │
│  │  • Builds understanding                                                 │   │
│  │                                                                         │   │
│  │  All this work stays HERE (doesn't fill your main context)              │   │
│  └──────────────────────────────┼──────────────────────────────────────────┘   │
│                                 │                                               │
│                                 ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      MAIN SESSION (Your Context)                        │   │
│  │                                                                         │   │
│  │  Summary returned: "Found 3 SQL injection risks in api/users.py,        │   │
│  │  api/orders.py, and api/products.py. Also found hardcoded secrets..."   │   │
│  │                                                                         │   │
│  │  Your context only grew by ~200 tokens (the summary)                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Subagent Types

| Type | Use Case | Tools Available |
|------|----------|-----------------|
| `Explore` | Codebase exploration | Read, Glob, Grep |
| `Plan` | Architecture planning | All tools |
| `general-purpose` | Complex multi-step tasks | All tools |

For custom subagent configuration, see the [official Subagents documentation](https://code.claude.com/docs/en/sub-agents).

## When to Use Subagents

**Good for Subagents:**
- Codebase exploration ("How does X work?")
- Pattern searching ("Find all uses of Y")
- Research tasks ("What libraries handle Z?")
- Parallel independent tasks
- Tasks requiring reading many files

**Keep in Main Session:**
- Actual code editing
- Interactive decision-making
- Tasks requiring conversation context
- Sequential dependent operations

## Triggering Subagents

Subagents are triggered automatically for appropriate tasks:

```
> Search the entire codebase for deprecated API usage
  # Claude will spawn an Explore subagent

> Explore how the caching layer works across all services
  # Good candidate for subagent

> Analyse these three areas in parallel:
  1. Authentication security
  2. API rate limiting
  3. Data validation
  # May spawn multiple parallel subagents
```

## Creating Custom Subagents

Use `/agents` to interactively create and manage subagents:

```
> /agents
```

This opens a menu to:
- View all available subagents
- Create new subagents (project or user level)
- Edit existing subagents and tool access
- Delete custom subagents

### Subagent File Format

Create `.claude/agents/my-agent.md` (project) or `~/.claude/agents/my-agent.md` (user):

```yaml
---
name: code-reviewer
description: Expert code reviewer. Use proactively after significant changes.
tools: Read, Grep, Glob, Bash
model: sonnet
---

You are a senior code reviewer. Review code for:
- Readability and naming
- Error handling and edge cases
- Security vulnerabilities
- Performance issues

Provide specific, actionable feedback with line numbers.
```

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (lowercase, hyphens) |
| `description` | Yes | When to invoke this agent (use "proactively" for auto-invocation) |
| `tools` | No | Comma-separated tool list (inherits all if omitted) |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `plan`, etc. |

### Resumable Subagents

Each subagent execution gets a unique `agentId`. Resume with previous context:

```
> Resume agent abc123 and analyse the authorisation logic
```
