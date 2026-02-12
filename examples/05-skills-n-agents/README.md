# Example 05 — Skills & Agents

A single project containing **8 skills** and **3 agents** that together
demonstrate every representative combination of Claude Code's skill/agent system.

**Domain**: A tiny BookStore Python project (`models/`, `api/`, `utils/`, `tests/`)
— simple enough to understand instantly, rich enough for skills to have something
meaningful to operate on.

## Feature Comparison

Each skill demonstrates a different combination of frontmatter options. Scan across
a row to see which features a skill uses; scan down a column to find which skills
demonstrate a given feature.

| Skill | Description | Type | User Invokes | Claude Invokes | Context | Agent | `$ARGUMENTS` | `` !`cmd` `` | `allowed-tools` | Supporting Files |
|-------|-------------|------|:---:|:---:|---------|-------|:---:|:---:|:---:|:---:|
| **S1** api-conventions | Simplest skill — Claude auto-loads conventions → writes compliant code | Ref | \* | \* | Inline | — | | | | |
| **S2** publishing-domain | `user-invocable: false` hides from `/` menu → only Claude loads ISBN/BISAC rules | Ref | | \* | Inline | — | | | | |
| **S3** generate-tests | User passes `$ARGUMENTS` path → `!`cmd`` injects pytest config → generates tests | Action | \* | | Inline | — | \* | \* | | |
| **S4** safe-reader | `allowed-tools` locks Claude to Read, Grep, Glob → safe code exploration | Ref | \* | \* | Inline | — | | | \* | |
| **S5** audit-codebase | `context: fork` → Explore agent reads 20+ files → returns summary only | Action | \* | \* | Fork | Explore | \* | | | |
| **S6** security-review | `context: fork` → dispatches to custom agent A1 → returns vulnerability report | Action | \* | \* | Fork | Custom (A1) | \* | | | |
| **S7** explain-with-diagrams | SKILL.md → reads `templates/explanation-template.md` → structured explanation | Action | \* | | Inline | — | \* | | | \* |
| **S8** pr-summary | `!`git diff`` injects live state → forks to Explore → returns change summary | Action | \* | | Fork | Explore | | \* | | |

**Legend**: \* = yes / enabled. Blank = no / default.
**User Invokes** = appears in `/` menu. **Claude Invokes** = Claude can auto-load based on description matching.
`disable-model-invocation` removes Claude's ability; `user-invocable: false` removes the user's.

| Agent | Description | `model` | `tools` | `skills` | `memory` | Triggered by Skill |
|-------|-------------|---------|---------|----------|----------|:---:|
| **A1** security-reviewer | S6 dispatches here → read-only OWASP scan → returns vulnerability report | sonnet | Read, Grep, Glob | — | — | S6 |
| **A2** api-developer | Preloads S1 + S2 as knowledge → writes code following conventions + domain rules | sonnet | *(all)* | S1, S2 | — | |
| **A3** code-reviewer | Reads persistent memory → reviews code → writes findings back for next session | *(default)* | Read, Grep, Glob, Write, Edit | — | project | |

## Quick Start

```bash
cd examples/05-skills-n-agents
claude                          # launch Claude Code in this project
```

Then try:
- Type `/` to see available skills (note: `s2-publishing-domain` is hidden)
- Type `/s3-generate-tests models/book.py` to see argument substitution
- Type `/s6-security-review` to see a forked agent find real vulnerabilities
- Ask "Use the a2-api-developer agent to build an author search API"

## Complete Combination Matrix

### Skills (8 total)

| # | Skill Name | Content Type | Who Invokes | Runs Where | Key Features |
|---|-----------|-------------|-------------|------------|-------------|
| S1 | `s1-api-conventions` | Reference | Both (default) | Inline | Simplest skill; auto-loading |
| S2 | `s2-publishing-domain` | Reference | Claude only | Inline | `user-invocable: false` |
| S3 | `s3-generate-tests` | Action | User only | Inline | `disable-model-invocation`, `$ARGUMENTS`, `` !`cmd` `` |
| S4 | `s4-safe-reader` | Reference | Both | Inline | `allowed-tools: Read, Grep, Glob` |
| S5 | `s5-audit-codebase` | Action | Both | Forked → Explore | `context: fork`, built-in agent |
| S6 | `s6-security-review` | Action | Both | Forked → Custom | `context: fork`, `agent: a1-security-reviewer` |
| S7 | `s7-explain-with-diagrams` | Action | User only | Inline | Supporting files (templates/) |
| S8 | `s8-pr-summary` | Action | User only | Forked → Explore | `context: fork` + `` !`cmd` `` |

### Agents (3 total)

| # | Agent Name | Purpose | Key Features |
|---|-----------|---------|-------------|
| A1 | `a1-security-reviewer` | Target for S6 | `model: sonnet`, read-only `tools` |
| A2 | `a2-api-developer` | Builder with preloaded skills | `skills: [s1-api-conventions, s2-publishing-domain]` |
| A3 | `a3-code-reviewer` | Reviewer with persistent memory | `memory: project` |

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

### S1: s1-api-conventions — Reference, Both Invoke

**What it demonstrates**: The simplest possible skill. No special frontmatter
beyond `name` and `description`. Claude auto-loads it when writing Python code
because the description matches.

**Try it**:
1. Ask "Create a function to search books by genre" → Claude follows the
   conventions automatically (dataclass, dict return, docstring format)
2. Type `/s1-api-conventions` → see the rules directly

```
┌─ S1: s1-api-conventions ──────────────────────────────────────────────────┐
│  Type: Reference   │  Invokes: Both (default)  │  Runs: Inline            │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL.md                       RESULT           │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌───────────────┐ │
│  │ User types       │     │ (default frontmatter)│     │ Claude writes │ │
│  │ /s1-api-         │────▶│                      │────▶│ code that     │ │
│  │  conventions     │     │ • Use @dataclass      │     │ follows all   │ │
│  │                  │     │ • Return dict         │     │ conventions   │ │
│  │ OR               │     │ • Docstrings with     │     │ automatically │ │
│  │                  │     │   Args/Returns        │     │               │ │
│  │ Claude auto-loads│────▶│ • snake_case verbs    │     │               │ │
│  │ (matches descr.) │     │                      │     │               │ │
│  └──────────────────┘     └──────────────────────┘     └───────────────┘ │
│                                                                           │
│  Simplest skill. Description drives auto-loading. No special frontmatter. │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### S2: s2-publishing-domain — Reference, Claude-Only

**What it demonstrates**: `user-invocable: false` makes this skill invisible in
the `/` menu. Only Claude can load it, based on description matching.

**Try it**:
1. Type `/` → `s2-publishing-domain` is NOT in the menu
2. Ask "Add ISBN validation to the Book model" → Claude uses the check digit
   algorithm from this skill (not just regex)
3. Ask "What do you know about BISAC codes?" → Claude discusses them

```
┌─ S2: s2-publishing-domain ────────────────────────────────────────────────┐
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

### S3: s3-generate-tests — Action, User-Only, Args + Dynamic Context

**What it demonstrates**: Three features together:
- `disable-model-invocation` — Claude can't trigger this itself
- `$ARGUMENTS` — user passes the target module path
- `` !`cmd` `` — injects live pytest config and existing test files

**Try it**:
1. Ask "generate tests for book.py" naturally → skill does NOT activate
2. Type `/s3-generate-tests models/book.py` → skill activates with argument
   substitution and dynamic config injection

```
┌─ S3: s3-generate-tests ───────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Inline                   │
│──────────────────────────────────────────────────────────────────────────-│
│                                                                           │
│  TRIGGER                  SKILL.md                       RESULT           │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌───────────────┐ │
│  │ User types:      │     │ disable-model-invoc.  │     │ Claude        │ │
│  │ /s3-generate-    │────▶│ argument-hint: <path> │────▶│ generates     │ │
│  │  tests           │     │                      │     │ tests that    │ │
│  │  models/book.py  │     │ "Test $ARGUMENTS"     │     │ match project │ │
│  │       │          │     │  → "Test models/..."  │     │ patterns      │ │
│  │       ▼          │     │                      │     │               │ │
│  │ $ARGUMENTS =     │     │ !`cat pyproject.toml` │     │               │ │
│  │ "models/book.py" │     │  → pytest config      │     │               │ │
│  │                  │     │ !`ls tests/`          │     │               │ │
│  │ ✗ Claude asks    │     │  → existing tests     │     │               │ │
│  │   "generate      │ ╳   │                      │     │               │ │
│  │   tests" → NOPE  │     │                      │     │               │ │
│  └──────────────────┘     └──────────────────────┘     └───────────────┘ │
│                                                                          │
│  disable-model-invocation hides from Claude. $ARGUMENTS + !`cmd`         │
│  enable parameterized skills with live system data injection.            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S4: s4-safe-reader — Reference, Tool Restriction

**What it demonstrates**: `allowed-tools` restricts Claude to read-only
operations (Read, Grep, Glob) while the skill is active.

**Try it**:
1. Type `/s4-safe-reader`
2. Ask "Explore this project and summarize its architecture"
3. Claude can read files and search but cannot edit, write, or run commands

```
┌─ S4: s4-safe-reader ──────────────────────────────────────────────────────┐
│  Type: Reference   │  Invokes: Both (default)  │  Runs: Inline            │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL.md                       RESULT           │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌───────────────┐ │
│  │ User types       │     │ allowed-tools:        │     │ Claude        │ │
│  │ /s4-safe-reader  │────▶│   Read, Grep, Glob    │────▶│ explores      │ │
│  │                  │     │                      │     │ codebase      │ │
│  │ OR               │     │ "Explore codebase,   │     │ read-only     │ │
│  │                  │     │  summarize structure, │     │               │ │
│  │ Claude auto-loads│────▶│  identify patterns"   │     │ ✓ Read files  │ │
│  │ (matches descr.) │     │                      │     │ ✓ Grep/Glob   │ │
│  └──────────────────┘     └──────────────────────┘     │ ✗ Write/Edit  │ │
│                                                         │ ✗ Bash        │ │
│                                                         └───────────────┘ │
│  allowed-tools restricts Claude to read-only operations while active.    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

### S5: s5-audit-codebase — Forked → Built-in Explore Agent

**What it demonstrates**: `context: fork` runs the skill in an isolated
subagent (Explore). The main conversation stays clean — only the summary
comes back.

**Try it**:
1. Type `/s5-audit-codebase` → subagent spinner appears
2. Type `/s5-audit-codebase error handling` → focused audit via `$ARGUMENTS`
3. After completion, ask "What files did the audit read?" → Claude doesn't
   know (the Explore agent's context was isolated)

```
┌─ S5: s5-audit-codebase ───────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: Both   │  Runs: Forked → Explore (built-in)   │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL.md                 FORKED SUBAGENT        │
│  ┌──────────────────┐     ┌─────────────────┐     ┌────────────────────┐ │
│  │ User types       │     │ context: fork    │     │ EXPLORE AGENT      │ │
│  │ /s5-audit-       │────▶│ agent: Explore   │─task▶│                    │ │
│  │  codebase        │     │                 │     │ Reads 20+ files    │ │
│  │  error handling  │     │ Audit checklist: │     │ Searches patterns  │ │
│  │       │          │     │ • Naming         │     │ Compiles report    │ │
│  │       ▼          │     │ • Imports        │     │        │           │ │
│  │ $ARGUMENTS =     │     │ • Error handling │     │        ▼           │ │
│  │ "error handling" │     │ • Type hints     │     │ ┌──────────────┐   │ │
│  └──────────────────┘     │ • Test coverage  │     │ │  Summary     │   │ │
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

### S6 + A1: s6-security-review → a1-security-reviewer

**What it demonstrates**: A skill (S6) defines WHAT to do, a custom agent (A1)
defines WHO does it and HOW. Two files compose into one workflow.

**Try it**:
1. Type `/s6-security-review` → the custom `a1-security-reviewer` agent runs
2. Observe it finding the hardcoded token in `api/auth.py` (CRITICAL)
   and the timing-attack vulnerable comparison (MEDIUM)
3. Type `/s6-security-review api/` → scoped review via `$ARGUMENTS`

```
┌─ S6 + A1: s6-security-review → a1-security-reviewer ─────────────────────┐
│  Type: Action   │  Invokes: Both   │  Runs: Forked → Custom agent         │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER              SKILL.md (= TASK)       AGENT .md (= EXECUTOR)     │
│  ┌────────────────┐   ┌──────────────────┐    ┌────────────────────────┐ │
│  │ User types     │   │ context: fork     │    │ a1-security-reviewer   │ │
│  │ /s6-security-  │──▶│ agent: a1-secur-  │───▶│                        │ │
│  │  review api/   │   │   ity-reviewer    │    │ model: sonnet          │ │
│  │                │   │                  │    │ tools: Read,Grep,Glob  │ │
│  └────────────────┘   │ "Check for:      │    │                        │ │
│                       │  • Injection      │    │ "You are a senior      │ │
│                       │  • Hardcoded keys │    │  security engineer     │ │
│                       │  • Insecure auth" │    │  with OWASP expertise  │ │
│                       └──────────────────┘    │  ..."                  │ │
│                                                └────────────────────────┘ │
│  MAIN CONVERSATION            FORKED SUBAGENT (a1-security-reviewer)      │
│  ┌──────────────────┐         ┌──────────────────────────────────────┐    │
│  │ Receives security│◀─report─│ Finds hardcoded token (CRITICAL)    │    │
│  │ report summary   │         │ Finds timing-attack vuln (MEDIUM)   │    │
│  └──────────────────┘         └──────────────────────────────────────┘    │
│                                                                           │
│  TWO files compose: Skill = WHAT to do. Agent = WHO does it and HOW.      │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### S7: s7-explain-with-diagrams — Supporting Files

**What it demonstrates**: A skill can have a directory with supporting files.
`SKILL.md` is the entrypoint; it references `templates/explanation-template.md`
which is loaded on demand.

**Try it**:
1. Type `/s7-explain-with-diagrams api/catalog.py`
2. Claude reads both the skill and the template, then explains the code using
   the four-section structure (Analogy, Diagram, Walkthrough, Gotcha)

```
┌─ S7: s7-explain-with-diagrams ────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Inline                   │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL DIRECTORY               RESULT            │
│  ┌──────────────────┐     ┌──────────────────────┐     ┌───────────────┐ │
│  │ User types       │     │ s7-explain-with-     │     │ Claude        │ │
│  │ /s7-explain-     │────▶│  diagrams/           │────▶│ explains      │ │
│  │  with-diagrams   │     │                      │     │ code using    │ │
│  │  api/catalog.py  │     │ ├─ SKILL.md (entry)   │     │ the template  │ │
│  │                  │     │ │  "Follow template   │     │ structure:    │ │
│  │ ✗ Claude auto-   │     │ │   in templates/..."  │     │               │ │
│  │   loads → NOPE   │ ╳   │ │         │           │     │ 1. Analogy    │ │
│  │   (disable-model │     │ │         │ references│     │ 2. Diagram    │ │
│  │    -invocation)  │     │ │         ▼           │     │ 3. Walkthru   │ │
│  └──────────────────┘     │ └─ templates/          │     │ 4. Gotcha     │ │
│                           │    └─ explanation-     │     │               │ │
│                           │       template.md      │     │               │ │
│                           │       (loaded on       │     │               │ │
│                           │        demand)         │     │               │ │
│                           └──────────────────────┘     └───────────────┘ │
│                                                                           │
│  SKILL.md is the entrypoint. Supporting files loaded on demand.           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

### S8: s8-pr-summary — Forked + Dynamic Git Context

**What it demonstrates**: Combines three features — `disable-model-invocation`
(user-only), `context: fork` (isolated Explore agent), and `` !`cmd` `` (live
git state injected before the agent sees the content).

**Try it**:
1. Make any change to a file (e.g., add a comment)
2. Type `/s8-pr-summary` → the Explore agent analyzes the actual diff

```
┌─ S8: s8-pr-summary ───────────────────────────────────────────────────────┐
│  Type: Action   │  Invokes: User only   │  Runs: Forked → Explore         │
│───────────────────────────────────────────────────────────────────────────│
│                                                                           │
│  TRIGGER                  SKILL.md                 FORKED SUBAGENT        │
│  ┌──────────────────┐     ┌─────────────────┐     ┌────────────────────┐ │
│  │ User types       │     │ disable-model-   │     │ EXPLORE AGENT      │ │
│  │ /s8-pr-summary   │────▶│  invocation      │─task▶│                    │ │
│  │                  │     │ context: fork    │     │ Analyzes diffs     │ │
│  └──────────────────┘     │ agent: Explore   │     │ Categorizes        │ │
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

### A2: a2-api-developer — Agent Preloads Skills (Inverse Pattern)

**What it demonstrates**: The **inverse** of S5/S6. Instead of a skill
dispatching TO an agent, this agent preloads skills as its knowledge base.
The `skills:` field injects skill content into the agent's context at startup.

**Try it**:
1. Ask "Use the a2-api-developer agent to build an author management API"
2. Observe that the agent follows BOTH s1-api-conventions AND s2-publishing-domain
   rules — because both skills were preloaded into its context

```
┌─ A2: a2-api-developer — Agent Preloads Skills ────────────────────────────┐
│  Type: Custom Agent   │  skills: [s1-api-conventions, s2-publishing-domain]│
│───────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  TRIGGER                     AGENT CONTEXT (isolated)                    │
│  ┌──────────────────┐        ┌────────────────────────────────────────┐  │
│  │ User asks Claude │        │  System Prompt (agent .md body):       │  │
│  │ "Use the a2-api- │        │  "You are a senior Python developer"   │  │
│  │  developer to    │──del──▶│                                        │  │
│  │  build author    │        │  ┌─ PRELOADED SKILLS ───────────────┐  │  │
│  │  management API" │        │  │                                  │  │  │
│  │                  │        │  │  ┌──────────────┐ ┌────────────┐ │  │  │
│  │ Claude delegates │        │  │  │s1-api-convent.│ │s2-publish. │ │  │  │
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

### A3: a3-code-reviewer — Agent with Persistent Memory

**What it demonstrates**: `memory: project` gives the agent a persistent
memory file that survives across sessions. The agent builds knowledge over
time, making each review better than the last.

**Try it**:
1. Ask "Use the a3-code-reviewer to review api/catalog.py" → it reviews and
   saves findings to memory
2. In a new session, ask "Use the a3-code-reviewer to review api/inventory.py"
   → it reads its previous findings first and applies past learning

```
┌─ A3: a3-code-reviewer — Agent with Persistent Memory ────────────────────┐
│  Type: Custom Agent   │  Has: memory: project   │  Tools: Read-only       │
│───────────────────────────────────────────────────────────────────────────│
│                                                                          │
│  SESSION 1                            SESSION 2                          │
│  ┌──────────────────────────┐         ┌──────────────────────────┐      │
│  │ a3-code-reviewer      │         │ code-reviewer agent      │      │
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
│   │   ├── s1-api-conventions/SKILL.md    # S1: Reference, both invoke
│   │   ├── s2-publishing-domain/SKILL.md  # S2: Reference, Claude-only
│   │   ├── s3-generate-tests/SKILL.md     # S3: Action, user-only, args
│   │   ├── s4-safe-reader/SKILL.md        # S4: Reference, tool restriction
│   │   ├── s5-audit-codebase/SKILL.md     # S5: Forked → Explore
│   │   ├── s6-security-review/SKILL.md    # S6: Forked → custom agent
│   │   ├── s7-explain-with-diagrams/      # S7: With supporting files
│   │   │   ├── SKILL.md
│   │   │   └── templates/
│   │   │       └── explanation-template.md
│   │   └── s8-pr-summary/SKILL.md         # S8: Forked + dynamic git
│   │
│   └── agents/
│       ├── a1-security-reviewer.md        # A1: Custom agent (target for S6)
│       ├── a2-api-developer.md            # A2: Agent preloads skills
│       └── a3-code-reviewer.md            # A3: Agent with memory
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
