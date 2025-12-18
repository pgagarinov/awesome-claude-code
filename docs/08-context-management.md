# Part 8: Context Management

## Checking Context Usage

Use `/context` to see how much of your context window is consumed:

```
> /context

Context Usage
⛁ ⛀ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛀   claude-opus-4-5-20251101 · 182k/200k tokens (91%)
⛀ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   ⛁ System prompt: 3.1k tokens (1.6%)
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   ⛁ System tools: 15.2k tokens (7.6%)
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   ⛁ MCP tools: 769 tokens (0.4%)
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   ⛁ Messages: 117.6k tokens (58.8%)
⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁ ⛁   ⛶ Free space: 18k (9.1%)
⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛶ ⛝ ⛝ ⛝   ⛝ Autocompact buffer: 45.0k tokens (22.5%)
⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝
⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝ ⛝

MCP tools · /mcp
└ mcp__applescript__applescript_execute (applescript): 769 tokens

SlashCommand Tool · 0 commands
└ Total: 877 tokens
```

The colored grid visualizes context usage:
- **System prompt/tools** - Base overhead (~9%)
- **MCP tools** - Configured MCP servers
- **Messages** - Your conversation history
- **Free space** - Available for new content
- **Autocompact buffer** - Reserved for summarization when context fills up

**Tips:**
- Use `/compact` when free space gets low to summarise the conversation
- Use `/clear` when starting something new to free up tokens
- Disable unused MCP servers with `/mcp` to free context space

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
