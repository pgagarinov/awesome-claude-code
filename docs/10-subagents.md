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

## Built-in Subagent Types

| Type | Use Case | Tools Available | Model |
|------|----------|-----------------|-------|
| `Explore` | Fast codebase search and exploration | Read, Glob, Grep | Haiku (fast, cheap) |
| `Plan` | Architecture planning and design | All read tools | Configurable |
| `general-purpose` | Complex multi-step tasks | All tools | Inherits parent |

### Explore Agent

The Explore agent is optimised for fast codebase searches. Powered by Haiku, it searches your codebase efficiently while preserving your main context:

```
> Search the entire codebase for deprecated API usage
  # Claude spawns an Explore subagent (uses Haiku)

> How does the authentication middleware work?
  # Explore agent reads relevant files and reports back
```

### Plan Agent

The Plan agent is designed for architecture and design tasks. It can explore the codebase and produce implementation plans:

```
> Plan the migration from REST to GraphQL
  # Claude spawns a Plan subagent to research and design

> Design a caching strategy for our API
  # Plan agent analyses current code and proposes architecture
```

### Model Selection

Claude can dynamically choose which model a subagent uses, or you can specify it in custom agent configuration:

```yaml
---
name: quick-search
description: Fast file searches
model: haiku
---
```

Available model options: `sonnet`, `opus`, `haiku`, or `inherit` (use parent's model).

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
| `disallowedTools` | No | Tools to explicitly block |
| `hooks` | No | PreToolUse/PostToolUse/Stop hooks scoped to the agent |
| `memory` | No | Memory scope: `user`, `project`, or `local` |

### Restricting Subagent Spawning

Control which subagents can be spawned using `Task(agent_type)` syntax in the `tools` frontmatter:

```yaml
---
name: orchestrator
tools: Read, Grep, Task(Explore), Task(Plan)
# Can only spawn Explore and Plan subagents, not general-purpose
---
```

### Resumable Subagents

Each subagent execution gets a unique `agentId`. Claude can resume a subagent with its previous context:

```
> Resume agent abc123 and analyse the authorisation logic
```

This is useful when a subagent's work needs follow-up without re-reading all the files.

## Background Agents

Background agents run independently while you continue working in the main session:

```
> & Research all the API endpoints and document them
  # Runs in background, notifies when complete
```

Press `Ctrl+B` to background a currently running agent. See [Part 33: Background Tasks](33-background-tasks.md) for details.

## Agent Teams (Experimental)

Agent Teams enable multi-agent collaboration where multiple agents work together on a task. This is an experimental feature requiring:

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

Teams allow coordinated work across multiple agents with shared context and task delegation. See the [official Agent Teams documentation](https://code.claude.com/docs/en/agent-teams) for details.

## Disabling Specific Agents

Block certain agent types using `Task(AgentName)` in `disallowedTools` settings or the `--disallowedTools` CLI flag:

```json
{
  "permissions": {
    "deny": ["Task(general-purpose)"]
  }
}
```

## Official Documentation

- [Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Custom Agents](https://code.claude.com/docs/en/custom-agents)
