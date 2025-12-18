# Part 8: Context Management

## Understanding Context

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         THE CONTEXT WINDOW                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Everything in your session consumes context:                                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │   Your Prompts                    ████░░░░░░░░░░░░░░░░  ~10%            │   │
│  │   Claude's Responses              ████████░░░░░░░░░░░░  ~25%            │   │
│  │   File Contents Read              ████████████████░░░░  ~50%            │   │
│  │   Tool Outputs                    ███░░░░░░░░░░░░░░░░░  ~10%            │   │
│  │   System Context                  ██░░░░░░░░░░░░░░░░░░  ~5%             │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  Context Window: 200,000 tokens (Opus)                                          │
│                                                                                 │
│  When context fills up:                                                         │
│  • Older messages may be summarised                                             │
│  • Performance may degrade                                                      │
│  • You should use /compact or start fresh                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Context Economy Strategies

### 1. Start Fresh for New Tasks

```bash
# New task? Fresh session
claude

# Only continue for related follow-ups
claude --continue
```

### 2. Use Compact Mode

```bash
# Start in compact mode
claude --compact

# Or mid-session
> /compact
```

### 3. Be Specific

```
# BAD: Vague, leads to broad exploration
> Help me understand this codebase

# GOOD: Focused, minimal context needed
> Explain how user authentication works in src/auth/
```

### 4. Use Subagents for Exploration

```
# Instead of exploring yourself (fills YOUR context),
# let a subagent explore (uses SEPARATE context)

> Search the codebase for all error handling patterns and summarise them
```

### 5. Structured Queries

```
# BAD: Multiple back-and-forths
> What files handle auth?
> Now show me the login function
> What about the logout?

# GOOD: Single comprehensive request
> Show me the login and logout functions in the auth module
```

## Context Cheatsheet

| Technique | Savings | When to Use |
|-----------|---------|-------------|
| Subagents for exploration | High | Research, understanding code |
| Targeted file reading | Medium | Working with specific functions |
| `/compact` | Medium | Long sessions |
| Fresh sessions | High | Switching tasks |
| Avoiding full file reads | High | Large files (500+ lines) |
