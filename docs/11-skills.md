# Part 11: Skills

## What Are Skills?

Skills are reusable markdown instructions that extend Claude Code's capabilities. They live in `.claude/skills/` directories and are loaded automatically. Since version 2.1.3, skills and slash commands are unified - a skill can be both an automated behaviour and a user-invocable command.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SKILLS SYSTEM                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Skills provide reusable instructions for Claude Code:                         │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  Project skill:     .claude/skills/pdf.md                               │   │
│  │  User skill:        ~/.claude/skills/review.md                          │   │
│  │  Plugin skill:      Installed via /plugins                              │   │
│  │                                                                         │   │
│  │  Skills can be:                                                         │   │
│  │  • Auto-loaded into Claude's context                                    │   │
│  │  • User-invocable via /skills menu or /skill-name                       │   │
│  │  • Provided by plugins                                                  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Skills Locations

| Location | Scope | Shared |
|----------|-------|--------|
| `.claude/skills/` | Project | Yes (git-committed) |
| `~/.claude/skills/` | User | No (personal) |
| Plugin-provided | Varies | Via plugin marketplace |
| `--add-dir` directories | Additional | `.claude/skills/` in added dirs |

Skills are hot-reloaded — create or modify a skill file and it becomes available immediately without restarting the session.

## Creating a Skill

### Basic Skill

Create `.claude/skills/pdf.md`:

````markdown
---
description: "Enhanced PDF reading and analysis"
---

When asked to read or analyse a PDF file, follow this approach:

## For Large PDFs (over 50 pages)

Do NOT read the entire PDF into context. Instead:

1. **Write a Python script** to extract what's needed:
   ```python
   import pymupdf  # or pdfplumber

   doc = pymupdf.open("file.pdf")

   # Extract table of contents
   toc = doc.get_toc()

   # Extract text from specific pages
   for page_num in range(min(5, len(doc))):
       page = doc[page_num]
       text = page.get_text()
   ```

2. **Run the script** and analyse the output

3. **Read specific pages** only if needed for detail
````

### User-Invocable Skill

By default, skills in `.claude/skills/` directories are visible in the `/skills` menu. Opt out with `user-invocable: false` in frontmatter.

Create `.claude/skills/review.md`:

````markdown
---
description: "Thorough code review with security focus"
argument-hint: "<file-or-directory>"
---

Review $ARGUMENTS for:
- Security vulnerabilities (OWASP Top 10)
- Error handling gaps
- Performance issues
- Code quality and readability

Provide specific, actionable feedback with line numbers.
````

Invoke with `/review src/auth.py` or select from the `/skills` menu.

### Skill with Arguments

Skills can access arguments via `$ARGUMENTS` (full string) or `$ARGUMENTS[0]`, `$ARGUMENTS[1]` (indexed):

````markdown
---
description: "Generate tests for a module"
argument-hint: "<module-path>"
---

Generate comprehensive pytest tests for $ARGUMENTS[0].

Requirements:
- Use pytest fixtures
- Include edge cases
- Follow AAA pattern (Arrange, Act, Assert)
````

## Frontmatter Reference

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What the skill does (shown in `/skills` menu) |
| `argument-hint` | string | Hint text for arguments (e.g., `<file>`) |
| `user-invocable` | boolean | Show in slash command menu (default: `true` for `/skills/` dir) |
| `allowed-tools` | list | Tools the skill can use (restricts or grants) |
| `agent` | string | Agent type to execute the skill |
| `context` | string | Set to `fork` to run in forked sub-agent context |
| `model` | string | Model to use (e.g., `sonnet`, `haiku`) |
| `hooks` | object | PreToolUse/PostToolUse/Stop hooks scoped to the skill |
| `memory` | string | Memory scope: `user`, `project`, or `local` |

### allowed-tools Examples

```yaml
---
# YAML-style list
allowed-tools:
  - Bash(npm test:*)
  - Read
  - Grep
---
```

```yaml
---
# Comma-separated
allowed-tools: Bash(npm test:*), Read, Grep
---
```

### Forked Context

Run a skill in an isolated sub-agent to protect the main conversation context:

```yaml
---
description: "Deep codebase exploration"
context: fork
agent: Explore
---
```

## Log Analysis Skill Example

Create `.claude/skills/logs.md`:

````markdown
---
description: "Analyse log files efficiently"
---

When asked to analyse log files, especially large ones:

## Never Read Full Logs

Log files can be gigabytes. Always use tools:

1. **Get overview first**:
   ```bash
   wc -l file.log           # Line count
   head -100 file.log       # First 100 lines
   tail -100 file.log       # Last 100 lines
   ```

2. **Search for patterns**:
   ```bash
   grep -c "ERROR" file.log     # Count errors
   grep -B2 -A2 "ERROR" file.log  # Errors with context
   ```

3. **For complex analysis**, write a Python script:
   ```python
   from collections import Counter

   errors = Counter()
   with open("file.log") as f:
       for line in f:
           if "ERROR" in line:
               # Extract error type and count
               errors[error_type] += 1
   ```
````

## Viewing Skills

```
> /skills

Available Skills:
  /pdf         Enhanced PDF reading and analysis
  /review      Thorough code review with security focus
  /logs        Analyse log files efficiently
```

Use `/context` to see which skills are loaded and their token cost.

## Skills vs Custom Slash Commands

Skills (`.claude/skills/`) and custom slash commands (`.claude/commands/`) are now unified. Both appear in the slash command menu and support frontmatter. The distinction is primarily organisational:

| Aspect | `.claude/skills/` | `.claude/commands/` |
|--------|-------------------|---------------------|
| Default visibility | Shown in `/skills` menu | Shown in `/` menu |
| Hot-reload | Yes | Yes |
| Frontmatter | Full support | Full support |
| Typical use | Reusable capabilities | Project-specific workflows |

## Plugin-Provided Skills

Plugins can provide skills that appear in the `/skills` menu with a plugin name badge:

```
> /skills

Plugin Skills:
  /deploy [my-plugin]    Deploy to staging or production
  /lint [my-plugin]      Run comprehensive linting
```

See [Part 32: Plugins](32-plugins.md) for plugin installation and management.

## Skills vs Agents (Subagents)

Skills and agents are complementary but distinct concepts. People often confuse them because they overlap — a skill *can* run inside an agent, and an agent *can* preload skills. The diagrams below clarify the difference.

### Where Things Run

The single most important distinction: **skills run inline** (in your conversation) by default, while **agents always run in their own isolated context** behind a wall.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  YOUR CONVERSATION                                                          │
│                                                                             │
│  You ←──→ Claude                                                            │
│                                                                             │
│  Skills load here by default ──────────────────────────────────────────┐    │
│  ┌───────────────────────────────────────────────────────────────────┐ │    │
│  │                                                                   │ │    │
│  │  /review src/auth.py        (you invoked it)                      │ │    │
│  │  api-conventions             (Claude auto-loaded it)              │ │    │
│  │                                                                   │ │    │
│  │  Shares your full conversation context                            │ │    │
│  │  No isolation — instructions merge into the current window        │ │    │
│  │                                                                   │ │    │
│  └───────────────────────────────────────────────────────────────────┘ │    │
│                                                                        │    │
│               │ delegate                         ▲ return summary      │    │
│               ▼                                  │                     │    │
├═══════════════╪══════════ CONTEXT WALL ══════════╪═════════════════════╪════┤
│               ▼                                  │                     │    │
│  ┌───────────────────────────────────────────────────────────────────┐ │    │
│  │  AGENT (subagent) — own isolated context                          │ │    │
│  │                                                                   │ │    │
│  │  ┌───────────┐ ┌──────────────┐ ┌─────────────┐ ┌─────────────┐ │ │    │
│  │  │  Model     │ │    Tools     │ │ Permissions  │ │  System     │ │ │    │
│  │  │  haiku     │ │  Read, Grep  │ │  dontAsk     │ │  prompt     │ │ │    │
│  │  └───────────┘ └──────────────┘ └─────────────┘ └─────────────┘ │ │    │
│  │                                                                   │ │    │
│  │  Cannot see your conversation history                             │ │    │
│  │  Cannot spawn other subagents                                     │ │    │
│  │  Returns only a summary when done                                 │ │    │
│  │                                                                   │ │    │
│  │  Can preload skills: ─────────────────────────────────────────────┘ │    │
│  │  skills: [api-conventions]   (full content injected at startup)     │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Anatomy Comparison

A side-by-side look at what each contains and how each behaves.

```
          SKILL (.claude/skills/)                AGENT (.claude/agents/)
          ═══════════════════════                ════════════════════════

          "What to do"                           "Who does it"
          Instructions / Knowledge               Execution Environment

          ┌────────────────────────┐             ┌────────────────────────┐
          │  SKILL.md              │             │  agent.md              │
          ├────────────────────────┤             ├────────────────────────┤
   front  │ description            │      front  │ name, description      │
   matter │ allowed-tools          │      matter │ model: haiku           │
          │ context: fork?         │             │ tools: Read, Grep      │
          │ agent: Explore?        │             │ permissionMode         │
          │ user-invocable         │             │ skills: [x, y]         │
          │ disable-model-invoc    │             │ hooks, maxTurns        │
          ├────────────────────────┤             ├────────────────────────┤
          │                        │             │                        │
   body   │ Step-by-step task      │      body   │ System prompt:         │
          │ instructions           │             │ "You are a senior      │
          │    — OR —              │             │  code reviewer..."     │
          │ Reference knowledge    │             │                        │
          │ (conventions, rules)   │             │                        │
          └────────────────────────┘             └────────────────────────┘

   Invoked by │ You (/name)                Invoked by │ Claude delegates
              │ Claude (auto)                          │ You ("use X agent")
              │ Both (default)                         │

   Runs in    │ YOUR context               Runs in    │ OWN isolated
              │  (default, inline)                     │  context (always)
              │ Forked context                         │
              │  (context: fork)                       │

   Analogy    │ Recipe / Playbook          Analogy    │ Specialist with
              │                                       │  their own office
```

### How Skills and Agents Connect

They compose bidirectionally. A skill can run *inside* an agent, and an agent can load skills as reference material.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                HOW SKILLS AND AGENTS CONNECT                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  (1) SKILL ──→ AGENT     "Run my instructions in that environment"          │
│                                                                             │
│    SKILL.md                              Agent (Explore)                    │
│    ┌───────────────────┐                 ┌────────────────────────────────┐ │
│    │ context: fork      │── task ──→     │ Receives skill content as the │ │
│    │ agent: Explore     │                │ task prompt to execute         │ │
│    │                    │                │                                │ │
│    │ "Research the      │                │ Agent provides: model, tools,  │ │
│    │  auth module..."   │                │ permissions, isolation          │ │
│    └───────────────────┘                 └────────────────────────────────┘ │
│                                                                             │
│  (2) AGENT ──→ SKILL     "Load that knowledge into my context"              │
│                                                                             │
│    agent.md                              Skill (api-conventions)            │
│    ┌────────────────────────────┐        ┌──────────────────────┐          │
│    │ skills:                    │←─────  │ Full skill content   │          │
│    │   - api-conventions        │        │ injected at startup  │          │
│    │   - error-handling         │        └──────────────────────┘          │
│    │                            │                                           │
│    │ "Implement API endpoints   │        Skill (error-handling)             │
│    │  following conventions"    │        ┌──────────────────────┐          │
│    │                            │←─────  │ Full skill content   │          │
│    └────────────────────────────┘        │ injected at startup  │          │
│                                          └──────────────────────┘          │
│                                                                             │
│  Summary:                                                                   │
│  ┌────────────────────────┬──────────────────┬────────────────────────────┐ │
│  │  Approach              │ System prompt     │ Task                      │ │
│  ├────────────────────────┼──────────────────┼────────────────────────────┤ │
│  │  Skill + context: fork │ From agent type  │ SKILL.md content          │ │
│  │  Agent + skills: [...] │ Agent's body     │ Claude's delegation msg   │ │
│  └────────────────────────┴──────────────────┴────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use What

```
  Do you have instructions or knowledge to give Claude?
  │
  ├─ YES ──→ Create a SKILL
  │          │
  │          ├─ Reference content? (conventions, patterns, rules)
  │          │  └─→ Default skill, runs inline
  │          │      user-invocable: false  (if users shouldn't /invoke it)
  │          │
  │          ├─ A task? (deploy, review, generate)
  │          │  ├─ Lightweight, needs conversation context
  │          │  │  └─→ Default skill (inline)
  │          │  └─ Heavy, protect main context
  │          │     └─→ context: fork  +  agent: Explore
  │          │
  │          └─ Only the user should trigger it? (deploy, send-message)
  │             └─→ disable-model-invocation: true
  │
  └─ NO, you need a specialized executor ──→ Create an AGENT
                │
                ├─ Need a specific model?        →  model: haiku
                ├─ Need restricted tools?        →  tools: Read, Grep
                ├─ Need custom permissions?      →  permissionMode: dontAsk
                ├─ Need persistent memory?       →  memory: user
                └─ Need reference knowledge?     →  skills: [api-conventions]
```

## Official Documentation

- [Skills Documentation](https://code.claude.com/docs/en/skills)
- [Custom Slash Commands](https://code.claude.com/docs/en/custom-slash-commands)
