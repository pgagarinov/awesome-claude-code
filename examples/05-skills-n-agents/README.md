# Example 05 — Skills & Agents

A single project containing **8 skills** and **3 agents** that together
demonstrate every representative combination of Claude Code's skill/agent system.

**Domain**: A tiny BookStore Python project (`models/`, `api/`, `utils/`, `tests/`)
— simple enough to understand instantly, rich enough for skills to have something
meaningful to operate on.

## Quick Start

```bash
cd examples/05-skills-n-agents
claude                          # launch Claude Code in this project
```

Then try:
- Type `/` to see available skills (note: `publishing-domain` is hidden)
- Type `/generate-tests models/book.py` to see argument substitution
- Type `/security-review` to see a forked agent find real vulnerabilities
- Ask "Use the api-developer agent to build an author search API"

## Complete Combination Matrix

### Skills (8 total)

| # | Skill Name | Content Type | Who Invokes | Runs Where | Key Features |
|---|-----------|-------------|-------------|------------|-------------|
| S1 | `api-conventions` | Reference | Both (default) | Inline | Simplest skill; auto-loading |
| S2 | `publishing-domain` | Reference | Claude only | Inline | `user-invocable: false` |
| S3 | `generate-tests` | Action | User only | Inline | `disable-model-invocation`, `$ARGUMENTS`, `` !`cmd` `` |
| S4 | `safe-reader` | Reference | Both | Inline | `allowed-tools: Read, Grep, Glob` |
| S5 | `audit-codebase` | Action | Both | Forked → Explore | `context: fork`, built-in agent |
| S6 | `security-review` | Action | Both | Forked → Custom | `context: fork`, `agent: security-reviewer` |
| S7 | `explain-with-diagrams` | Action | User only | Inline | Supporting files (templates/) |
| S8 | `pr-summary` | Action | User only | Forked → Explore | `context: fork` + `` !`cmd` `` |

### Agents (3 total)

| # | Agent Name | Purpose | Key Features |
|---|-----------|---------|-------------|
| A1 | `security-reviewer` | Target for S6 | `model: sonnet`, read-only `tools` |
| A2 | `api-developer` | Builder with preloaded skills | `skills: [api-conventions, publishing-domain]` |
| A3 | `code-reviewer` | Reviewer with persistent memory | `memory: project` |

### Coverage Grid

```
                  WHO INVOKES THE SKILL?
                  ┌──────────────┬────────────┬─────────────┐
                  │  User Only   │    Both    │ Claude Only │
                  │  (disable-   │  (default) │ (user-invoc │
                  │   model-inv) │            │  : false)   │
  ┌───────────────┼──────────────┼────────────┼─────────────┤
  │ INLINE        │ S3 gen-tests │ S1 api-con │ S2 publish- │
  │ (main context)│ S7 explain   │ S4 safe-   │    domain   │
  │               │              │    reader  │             │
  ├───────────────┼──────────────┼────────────┼─────────────┤
  │ FORKED →      │ S8 pr-       │ S5 audit-  │             │
  │ Built-in Agent│    summary   │  codebase  │             │
  ├───────────────┼──────────────┼────────────┼─────────────┤
  │ FORKED →      │              │ S6 secur-  │             │
  │ Custom Agent  │              │  ity-review│             │
  └───────────────┴──────────────┴────────────┴─────────────┘
```

---

## Try-It Guide

### S1: api-conventions — Reference, Both Invoke

**What it demonstrates**: The simplest possible skill. No special frontmatter
beyond `name` and `description`. Claude auto-loads it when writing Python code
because the description matches.

**Try it**:
1. Ask "Create a function to search books by genre" → Claude follows the
   conventions automatically (dataclass, dict return, docstring format)
2. Type `/api-conventions` → see the rules directly

```
┌─ S1: api-conventions ─────────────────────────────────────────────────────┐
│  Type: Reference   │  Invokes: Both (default)  │  Runs: Inline            │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL.md                       RESULT           │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌───────────────┐ │
│  │ User types       │     │ (default frontmatter)│     │ Claude writes │ │
│  │ /api-conventions  │────▶│                      │────▶│ code that     │ │
│  │                  │     │ • Use @dataclass      │     │ follows all   │ │
│  │ OR               │     │ • Return dict         │     │ conventions   │ │
│  │                  │     │ • Docstrings with     │     │ automatically │ │
│  │ Claude auto-loads│────▶│   Args/Returns        │     │               │ │
│  │ (matches descr.) │     │ • snake_case verbs    │     │               │ │
│  └──────────────────┘     └──────────────────────┘     └───────────────┘ │
│                                                                           │
│  Simplest skill. Description drives auto-loading. No special frontmatter. │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### S2: publishing-domain — Reference, Claude-Only

**What it demonstrates**: `user-invocable: false` makes this skill invisible in
the `/` menu. Only Claude can load it, based on description matching.

**Try it**:
1. Type `/` → `publishing-domain` is NOT in the menu
2. Ask "Add ISBN validation to the Book model" → Claude uses the check digit
   algorithm from this skill (not just regex)
3. Ask "What do you know about BISAC codes?" → Claude discusses them

```
┌─ S2: publishing-domain ──────────────────────────────────────────────────┐
│  Type: Reference   │  Invokes: Claude only      │  Runs: Inline          │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL.md                       RESULT          │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌──────────────┐ │
│  │                  │     │ user-invocable: false │     │ Claude uses  │ │
│  │ ✗ User types     │     │                      │     │ check digit  │ │
│  │   /publishing-   │ ╳   │ • ISBN-13 check digit│     │ algorithm    │ │
│  │   domain         │     │   (modulo 10, weights│     │ (not just    │ │
│  │   → NOT IN MENU  │     │    1 and 3)          │     │  regex!)     │ │
│  │                  │     │ • BISAC subject codes │     │              │ │
│  │ ✓ Claude auto-   │────▶│ • Price in cents      │────▶│ Domain rules │ │
│  │   loads when     │     │ • LC classification   │     │ applied to   │ │
│  │   "ISBN" matches │     │                      │     │ generated    │ │
│  └──────────────────┘     └──────────────────────┘     │ code         │ │
│                                                         └──────────────┘ │
│  Invisible in / menu. Pure background knowledge only Claude can load.    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S3: generate-tests — Action, User-Only, Args + Dynamic Context

**What it demonstrates**: Three features together:
- `disable-model-invocation` — Claude can't trigger this itself
- `$ARGUMENTS` — user passes the target module path
- `` !`cmd` `` — injects live pytest config and existing test files

**Try it**:
1. Ask "generate tests for book.py" naturally → skill does NOT activate
2. Type `/generate-tests models/book.py` → skill activates with argument
   substitution and dynamic config injection

```
┌─ S3: generate-tests ─────────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Inline                  │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL.md                       RESULT          │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌──────────────┐ │
│  │ User types:      │     │ disable-model-invoc.  │     │ Claude       │ │
│  │ /generate-tests  │────▶│ argument-hint: <path> │────▶│ generates    │ │
│  │  models/book.py  │     │                      │     │ tests that   │ │
│  │       │          │     │ "Test $ARGUMENTS"     │     │ match project│ │
│  │       ▼          │     │  → "Test models/..."  │     │ patterns     │ │
│  │ $ARGUMENTS =     │     │                      │     │              │ │
│  │ "models/book.py" │     │ !`cat pyproject.toml` │     │              │ │
│  │                  │     │  → pytest config      │     │              │ │
│  │ ✗ Claude asks    │     │ !`ls tests/`          │     │              │ │
│  │   "generate      │ ╳   │  → existing tests     │     │              │ │
│  │   tests" → NOPE  │     │                      │     │              │ │
│  └──────────────────┘     └──────────────────────┘     └──────────────┘ │
│                                                                          │
│  disable-model-invocation hides from Claude. $ARGUMENTS + !`cmd`         │
│  enable parameterized skills with live system data injection.            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S4: safe-reader — Reference, Tool Restriction

**What it demonstrates**: `allowed-tools` restricts Claude to read-only
operations (Read, Grep, Glob) while the skill is active.

**Try it**:
1. Type `/safe-reader`
2. Ask "Explore this project and summarize its architecture"
3. Claude can read files and search but cannot edit, write, or run commands

```
┌─ S4: safe-reader ────────────────────────────────────────────────────────┐
│  Type: Reference   │  Invokes: Both (default)  │  Runs: Inline           │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL.md                       RESULT          │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌──────────────┐ │
│  │ User types       │     │ allowed-tools:        │     │ Claude       │ │
│  │ /safe-reader     │────▶│   Read, Grep, Glob    │────▶│ explores     │ │
│  │                  │     │                      │     │ codebase     │ │
│  │ OR               │     │ "Explore codebase,   │     │ read-only    │ │
│  │                  │     │  summarize structure, │     │              │ │
│  │ Claude auto-loads│────▶│  identify patterns"   │     │ ✓ Read files │ │
│  │ (matches descr.) │     │                      │     │ ✓ Grep/Glob  │ │
│  └──────────────────┘     └──────────────────────┘     │ ✗ Write/Edit │ │
│                                                         │ ✗ Bash       │ │
│                                                         └──────────────┘ │
│  allowed-tools restricts Claude to read-only operations while active.    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S5: audit-codebase — Forked → Built-in Explore Agent

**What it demonstrates**: `context: fork` runs the skill in an isolated
subagent (Explore). The main conversation stays clean — only the summary
comes back.

**Try it**:
1. Type `/audit-codebase` → subagent spinner appears
2. Type `/audit-codebase error handling` → focused audit via `$ARGUMENTS`
3. After completion, ask "What files did the audit read?" → Claude doesn't
   know (the Explore agent's context was isolated)

```
┌─ S5: audit-codebase ─────────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: Both   │  Runs: Forked → Explore (built-in)  │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL.md                 FORKED SUBAGENT       │
│  ┌──────────────────┐     ┌─────────────────┐     ┌───────────────────┐ │
│  │ User types       │     │ context: fork    │     │ EXPLORE AGENT     │ │
│  │ /audit-codebase  │────▶│ agent: Explore   │─task▶│                   │ │
│  │  error handling  │     │                 │     │ Reads 20+ files   │ │
│  │       │          │     │ Audit checklist: │     │ Searches patterns │ │
│  │       ▼          │     │ • Naming         │     │ Compiles report   │ │
│  │ $ARGUMENTS =     │     │ • Imports        │     │        │          │ │
│  │ "error handling" │     │ • Error handling │     │        ▼          │ │
│  └──────────────────┘     │ • Type hints     │     │ ┌─────────────┐   │ │
│                           │ • Test coverage  │     │ │  Summary    │   │ │
│  MAIN CONVERSATION        └─────────────────┘     │ │  only       │   │ │
│  ┌──────────────────┐                              │ └─────────────┘   │ │
│  │ Receives ONLY    │◀────────── summary ──────────│ (file contents    │ │
│  │ the summary.     │                              │  stay isolated)   │ │
│  │ Context clean.   │                              └───────────────────┘ │
│  └──────────────────┘                                                    │
│  context: fork isolates heavy work. Skill = TASK. Agent = ENVIRONMENT.   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S6 + A1: security-review → security-reviewer

**What it demonstrates**: A skill (S6) defines WHAT to do, a custom agent (A1)
defines WHO does it and HOW. Two files compose into one workflow.

**Try it**:
1. Type `/security-review` → the custom `security-reviewer` agent runs
2. Observe it finding the hardcoded token in `api/auth.py` (CRITICAL)
   and the timing-attack vulnerable comparison (MEDIUM)
3. Type `/security-review api/` → scoped review via `$ARGUMENTS`

```
┌─ S6 + A1: security-review → security-reviewer ──────────────────────────┐
│  Type: Action   │  Invokes: Both   │  Runs: Forked → Custom agent        │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER              SKILL.md (= TASK)       AGENT .md (= EXECUTOR)    │
│  ┌────────────────┐   ┌──────────────────┐    ┌───────────────────────┐ │
│  │ User types     │   │ context: fork     │    │ security-reviewer.md  │ │
│  │ /security-     │──▶│ agent: security-  │───▶│                       │ │
│  │  review api/   │   │        reviewer   │    │ model: sonnet         │ │
│  │                │   │                  │    │ tools: Read,Grep,Glob │ │
│  └────────────────┘   │ "Check for:      │    │                       │ │
│                       │  • Injection      │    │ "You are a senior     │ │
│                       │  • Hardcoded keys │    │  security engineer    │ │
│                       │  • Insecure auth" │    │  with OWASP expertise │ │
│                       └──────────────────┘    │  ..."                 │ │
│                                                └───────────────────────┘ │
│  MAIN CONVERSATION              FORKED SUBAGENT (security-reviewer)      │
│  ┌──────────────────┐           ┌─────────────────────────────────────┐  │
│  │ Receives security│◀──report──│ Finds hardcoded token (CRITICAL)   │  │
│  │ report summary   │           │ Finds timing-attack vuln (MEDIUM)  │  │
│  └──────────────────┘           └─────────────────────────────────────┘  │
│                                                                          │
│  TWO files compose: Skill = WHAT to do. Agent = WHO does it and HOW.     │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S7: explain-with-diagrams — Supporting Files

**What it demonstrates**: A skill can have a directory with supporting files.
`SKILL.md` is the entrypoint; it references `templates/explanation-template.md`
which is loaded on demand.

**Try it**:
1. Type `/explain-with-diagrams api/catalog.py`
2. Claude reads both the skill and the template, then explains the code using
   the four-section structure (Analogy, Diagram, Walkthrough, Gotcha)

```
┌─ S7: explain-with-diagrams ──────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Inline                  │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL DIRECTORY               RESULT           │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌──────────────┐ │
│  │ User types       │     │ explain-with-diagrams/│     │ Claude       │ │
│  │ /explain-with-   │────▶│                      │────▶│ explains     │ │
│  │  diagrams        │     │ ├─ SKILL.md (entry)   │     │ code using   │ │
│  │  api/catalog.py  │     │ │  "Follow template   │     │ the template │ │
│  │                  │     │ │   in templates/..."  │     │ structure:   │ │
│  │ ✗ Claude auto-   │     │ │         │           │     │              │ │
│  │   loads → NOPE   │ ╳   │ │         │ references│     │ 1. Analogy   │ │
│  │   (disable-model │     │ │         ▼           │     │ 2. Diagram   │ │
│  │    -invocation)  │     │ └─ templates/          │     │ 3. Walkthru  │ │
│  └──────────────────┘     │    └─ explanation-     │     │ 4. Gotcha    │ │
│                           │       template.md      │     │              │ │
│                           │       (loaded on       │     │              │ │
│                           │        demand)         │     │              │ │
│                           └──────────────────────┘     └──────────────┘ │
│                                                                          │
│  SKILL.md is the entrypoint. Supporting files loaded on demand.          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S8: pr-summary — Forked + Dynamic Git Context

**What it demonstrates**: Combines three features — `disable-model-invocation`
(user-only), `context: fork` (isolated Explore agent), and `` !`cmd` `` (live
git state injected before the agent sees the content).

**Try it**:
1. Make any change to a file (e.g., add a comment)
2. Type `/pr-summary` → the Explore agent analyzes the actual diff

```
┌─ S8: pr-summary ─────────────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Forked → Explore        │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                  SKILL.md                 FORKED SUBAGENT       │
│  ┌──────────────────┐     ┌─────────────────┐     ┌───────────────────┐ │
│  │ User types       │     │ disable-model-   │     │ EXPLORE AGENT     │ │
│  │ /pr-summary      │────▶│  invocation      │─task▶│                   │ │
│  │                  │     │ context: fork    │     │ Analyzes diffs    │ │
│  └──────────────────┘     │ agent: Explore   │     │ Categorizes       │ │
│                           │                 │     │  changes          │ │
│  PREPROCESSED:            │ Dynamic context: │     │ Identifies risks  │ │
│  !`cmd` runs BEFORE       │ !`git diff`      │     │        │          │ │
│  agent sees content        │  → actual diff   │     │        ▼          │ │
│                           │ !`git log -10`   │     │ ┌─────────────┐   │ │
│  MAIN CONVERSATION        │  → recent commits│     │ │  Summary    │   │ │
│  ┌──────────────────┐     │ !`git diff       │     │ │  report     │   │ │
│  │ Receives change  │◀sum─│   --name-only`   │     │ └─────────────┘   │ │
│  │ summary only     │     └─────────────────┘     └───────────────────┘ │
│                                                                          │
│  Combines: disable-model-invoc + context: fork + !`cmd` dynamic inject.  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### A2: api-developer — Agent Preloads Skills (Inverse Pattern)

**What it demonstrates**: The **inverse** of S5/S6. Instead of a skill
dispatching TO an agent, this agent preloads skills as its knowledge base.
The `skills:` field injects skill content into the agent's context at startup.

**Try it**:
1. Ask "Use the api-developer agent to build an author management API"
2. Observe that the agent follows BOTH api-conventions AND publishing-domain
   rules — because both skills were preloaded into its context

```
┌─ A2: api-developer — Agent Preloads Skills ──────────────────────────────┐
│  Type: Custom Agent   │  Has: skills: [api-conventions, publishing-domain]│
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                     AGENT CONTEXT (isolated)                    │
│  ┌──────────────────┐        ┌────────────────────────────────────────┐  │
│  │ User asks Claude │        │  System Prompt (agent .md body):       │  │
│  │ "Use the api-    │        │  "You are a senior Python developer"   │  │
│  │  developer to    │──del──▶│                                        │  │
│  │  build author    │        │  ┌─ PRELOADED SKILLS ───────────────┐  │  │
│  │  management API" │        │  │                                  │  │  │
│  │                  │        │  │  ┌──────────────┐ ┌────────────┐ │  │  │
│  │ Claude delegates │        │  │  │api-conventions│ │publishing- │ │  │  │
│  │ to the agent     │        │  │  │(full content) │ │domain      │ │  │  │
│  └──────────────────┘        │  │  │injected at   │ │(full cont.)│ │  │  │
│                              │  │  │startup       │ │injected at │ │  │  │
│  MAIN CONVERSATION           │  │  └──────────────┘ │startup     │ │  │  │
│  ┌──────────────────┐        │  │                    └────────────┘ │  │  │
│  │ Receives code    │◀─res───│  └──────────────────────────────────┘  │  │
│  │ following BOTH   │        │                                        │  │
│  │ conventions AND  │        │  Writes code with both knowledge sets  │  │
│  │ domain rules     │        └────────────────────────────────────────┘  │
│  └──────────────────┘                                                    │
│                                                                          │
│  THE INVERSE: Skill=TASK→Agent (S5,S6) vs Agent=PERSONA←Skills (A2).    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### A3: code-reviewer — Agent with Persistent Memory

**What it demonstrates**: `memory: project` gives the agent a persistent
memory file that survives across sessions. The agent builds knowledge over
time, making each review better than the last.

**Try it**:
1. Ask "Use the code-reviewer to review api/catalog.py" → it reviews and
   saves findings to memory
2. In a new session, ask "Use the code-reviewer to review api/inventory.py"
   → it reads its previous findings first and applies past learning

```
┌─ A3: code-reviewer — Agent with Persistent Memory ───────────────────────┐
│  Type: Custom Agent   │  Has: memory: project   │  Tools: Read-only       │
│──────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  SESSION 1                            SESSION 2                          │
│  ┌──────────────────────────┐         ┌──────────────────────────┐      │
│  │ code-reviewer agent      │         │ code-reviewer agent      │      │
│  │                          │         │                          │      │
│  │ Reviews api/catalog.py   │         │ Reviews api/inventory.py │      │
│  │                          │         │                          │      │
│  │ Discovers:               │         │ Reads MEMORY.md first:   │      │
│  │ • No input validation    │         │ "catalog.py had no input │      │
│  │ • Inconsistent errors    │         │  validation..."          │      │
│  │                          │         │         │                │      │
│  │ Writes to MEMORY.md: ────│────▶────│────▶    ▼                │      │
│  │ "catalog.py: missing     │  persists│  Applies past learning  │      │
│  │  input validation.       │  across  │  to new review →        │      │
│  │  Check other modules."   │  sessions│  catches same pattern   │      │
│  │                          │         │  in inventory.py!        │      │
│  └──────────────────────────┘         └──────────────────────────┘      │
│                                                                          │
│  memory: project persists across sessions. Agent builds knowledge.       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
examples/05-skills-n-agents/
├── README.md                              ← you are here
├── CLAUDE.md                              # Minimal router
├── pyproject.toml                         # Python project + pytest config
│
├── .claude/
│   ├── skills/
│   │   ├── api-conventions/SKILL.md       # S1: Reference, both invoke
│   │   ├── publishing-domain/SKILL.md     # S2: Reference, Claude-only
│   │   ├── generate-tests/SKILL.md        # S3: Action, user-only, args
│   │   ├── safe-reader/SKILL.md           # S4: Reference, tool restriction
│   │   ├── audit-codebase/SKILL.md        # S5: Forked → Explore
│   │   ├── security-review/SKILL.md       # S6: Forked → custom agent
│   │   ├── explain-with-diagrams/         # S7: With supporting files
│   │   │   ├── SKILL.md
│   │   │   └── templates/
│   │   │       └── explanation-template.md
│   │   └── pr-summary/SKILL.md            # S8: Forked + dynamic git
│   │
│   └── agents/
│       ├── security-reviewer.md           # A1: Custom agent (target for S6)
│       ├── api-developer.md               # A2: Agent preloads skills
│       └── code-reviewer.md               # A3: Agent with memory
│
├── models/
│   ├── book.py                            # @dataclass: title, author, price
│   └── author.py                          # @dataclass: name, bio
│
├── api/
│   ├── catalog.py                         # get_book, list_books, create_book
│   ├── inventory.py                       # track_stock, check_availability
│   └── auth.py                            # ⚠ Hardcoded token (deliberate)
│
├── utils/
│   └── validators.py                      # ISBN regex (no check digit)
│
└── tests/
    ├── test_catalog.py
    ├── test_inventory.py
    └── test_auth.py
```

## Key Concepts Demonstrated

### Skill → Agent (S5, S6, S8)

The skill defines the **task** (what to do). The agent provides the
**environment** (who does it, what tools, what model).

```
SKILL.md   ──task──▶   AGENT
(the what)             (the who/how)
```

### Agent ← Skills (A2)

The **inverse** pattern. The agent defines the **persona** (senior developer).
Skills provide **knowledge** (conventions, domain rules) preloaded at startup.

```
SKILL(s)   ──knowledge──▶   AGENT.md
(the know-how)               (the persona)
```

### Memory (A3)

The agent persists findings across sessions via `memory: project`. First review
discovers patterns; subsequent reviews build on that knowledge.

## References

- [Skills documentation](https://code.claude.com/docs/en/skills)
- [Sub-agents documentation](https://code.claude.com/docs/en/sub-agents)
- [Feature comparison](https://code.claude.com/docs/en/features-overview#compare-similar-features)
