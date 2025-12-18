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
