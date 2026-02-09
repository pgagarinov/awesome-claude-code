# Progressive Disclosure for Claude Code

**Problem:** Claude Code loads `CLAUDE.md` into every conversation. If you put all your
rules and docs there, you waste context tokens on information irrelevant to the current task.

**Solution:** A layered architecture that progressively discloses information:

```
Layer 1: CLAUDE.md              ← Always loaded (router + essential rules)
Layer 2: .claude/rules/*.md     ← Auto-loaded when editing files matching paths: globs
         └── @docs/file.md      ← Hard-included with the rule (NOT on-demand)
Layer 3: docs/*.md              ← Manually read by Claude via routing table fallback
Layer 4: products/X/CLAUDE.md   ← Subtree router, loaded when working in that subtree
```

## Loading Mechanisms

There are exactly **four ways** docs get into Claude's context:

| Mechanism | When it loads | Example |
|-----------|---------------|---------|
| **Always loaded** | Every conversation | `CLAUDE.md`, `.claude/rules/` without `paths:` |
| **Path-triggered rule** | When Claude touches a matching file | `.claude/rules/api.md` with `paths: api/**` |
| **Subtree router** | When Claude works in that directory | `api/CLAUDE.md` |
| **Manual read** | Claude follows routing table to read a doc | Routing table says "API" -> `docs/api-design.md` |

The `@docs/file.md` syntax is a **hard include** — it gets pulled in whenever its
parent file loads. If `api.md` rule has `@docs/api-design.md`, then touching any file
in `api/` loads both the rule AND the API design doc together. This is not on-demand;
it's bundled with the rule.

**Anti-pattern:** `.claude/rules/` files without `paths:` frontmatter are always loaded,
just like `CLAUDE.md`. They provide no token savings — move their content to `CLAUDE.md`
or add `paths:` scoping.

## This Demo

```
progressive-disclosure/
├── CLAUDE.md                  # Layer 1: Router (always loaded)
├── .claude/rules/
│   ├── api.md                 # Layer 2: paths: api/** → suffix rule + @docs/api-design.md
│   └── models.md              # Layer 2: paths: models/** → suffix rule (no @includes)
├── docs/
│   ├── api-design.md          # Hard-included by api.md rule
│   ├── coding-standards.md    # Hard-included by CLAUDE.md (always loaded)
│   └── testing.md             # Only loads if Claude reads it via routing table
├── api/
│   ├── CLAUDE.md              # Layer 4: Subtree router (loaded when working in api/)
│   └── health_endpoint.py     # Existing file (follows _endpoint suffix)
├── models/
│   └── order_model.py         # Existing file (follows _model suffix)
└── utils/
    └── helpers.py             # No matching rule — no suffix enforced
```

The two rules each enforce a **filename suffix** for their directory:
- `api/` → files must end with `_endpoint.py` (Layer 2), plus `async def` and
  `version` parameter from subtree CLAUDE.md (Layer 4)
- `models/` → files must end with `_model.py`
- `utils/` → no rule, no suffix

## Try It Yourself

Start Claude Code in this folder:

```bash
cd progressive-disclosure
claude
```

### Test 1: Path-scoped rule fires (api/)

```
Create a Python file for user management in the api/ folder
```

**Expected:** Claude creates `api/user_endpoint.py` (with the `_endpoint` suffix)
because editing in `api/` triggers `.claude/rules/api.md`.

### Test 2: Different rule fires (models/)

```
Create a Python file for user data in the models/ folder
```

**Expected:** Claude creates `models/user_model.py` (with the `_model` suffix)
because `models/` triggers `.claude/rules/models.md`.

### Test 3: No rule fires (utils/)

```
Create a Python file for date formatting in the utils/ folder
```

**Expected:** Claude creates something like `utils/date_utils.py` or
`utils/date_formatting.py` — no suffix rule applies because no `.claude/rules/`
file has `paths: utils/**`.

### Test 4: Routing table fallback

Without touching any files, ask:

```
What are the API design standards?
```

**Expected:** Claude reads `docs/api-design.md` by following the routing table in
`CLAUDE.md`. The rule didn't fire (no file in `api/` was edited), but the routing
table guided Claude to the right doc.

### Test 5: Subtree CLAUDE.md (api/)

In a **new session** (so previous rules aren't cached), ask:

```
Create a Python file for product listing in the api/ folder
```

**Expected:** Claude creates `api/product_endpoint.py` with:
- The `_endpoint` suffix (from `.claude/rules/api.md` — Layer 2)
- `async def` function signature (from `api/CLAUDE.md` — Layer 4)
- A `version` parameter defaulting to `"v1"` (from `api/CLAUDE.md` — Layer 4)

This shows Layer 2 (path-scoped rule) and Layer 4 (subtree router) stacking together.
Neither rule loaded for `models/` or `utils/` work.

### Test 6: Hard import from CLAUDE.md (always in context)

In a **new session**, without touching any files, ask:

```
Create a Python file for string validation in the utils/ folder
```

**Expected:** Claude creates a file in `utils/` (no suffix rule applies), but the
code follows the coding standards from `docs/coding-standards.md`:
- Functions that can fail return a tuple `(result, error_message)`
- The module includes `import logging` and `logger = logging.getLogger(__name__)`

This works because `CLAUDE.md` hard-imports `@docs/coding-standards.md`, so it's
loaded in **every** conversation — even when no path-scoped rule fires. Compare
with Test 3 where `utils/` has no rules: the suffix is free-form, but the coding
standards still apply because they come from the always-loaded Layer 1 hard import.

### Test 7: Verify what's loaded

At any point, ask:

```
What project rules do you currently have loaded?
```

After Test 1, Claude should mention the `_endpoint` suffix rule and API design
standards. After Test 3, it should NOT mention any suffix rules (unless Tests 1-2
already loaded them in the same session). The coding standards from
`docs/coding-standards.md` should **always** be mentioned (hard-imported via `@`).

## Concepts Demonstrated

| Concept | Where to see it |
|---------|-----------------|
| **CLAUDE.md as router** | Small file with routing table, not full docs |
| **Path-scoped rules** | `paths:` frontmatter triggers on file access |
| **Hard includes (`@`) in rules** | `api.md` pulls in `docs/api-design.md` when it loads |
| **Hard includes (`@`) in CLAUDE.md** | Test 6 — `coding-standards.md` always loaded via `@` in CLAUDE.md |
| **Routing table fallback** | Test 4 — Claude finds docs without path trigger |
| **Token savings** | Test 3 — no rules load for unmatched paths |
| **Subtree CLAUDE.md** | `api/CLAUDE.md` adds `async def` + `version` param |
| **Layered stacking** | Test 5 — Layer 1 + 2 + 4 all contribute to the result |
| **Anti-pattern awareness** | Rules without `paths:` = always loaded = no savings |

## Concepts NOT Shown (For Simplicity)

These exist in the full architecture but are omitted here:

- **AI summaries (`docs/_ai/`)** — optional thin summaries marked non-authoritative,
  containing only navigation + invariants, never full specs.
- **Layered rules** — base rules (e.g., `python-base.md` for all `*.py`) plus
  product-specific rules that stack on top. Avoids duplicating shared rules.
- **Size constraints** — CLAUDE.md should stay under 25K chars (~210 lines) optimal,
  38K chars hard limit. Docs under 72K chars (~600 lines).
- **Governance** — CI checks that verify all referenced doc paths exist, routing
  table completeness, and doc freshness.
- **`/memory` command** — inspect what Claude currently has loaded in context.

## Key Principles

1. **CLAUDE.md is a router, not a repository** — point to docs, don't copy them
2. **`paths:` is what makes rules lazy** — without it, rules load always (no savings)
3. **`@` is a hard include, not on-demand** — it bundles with its parent file
4. **Single source of truth** — each concept in one canonical doc, cross-referenced
5. **Routing table = fallback** — when path rules don't fire, Claude follows the map
6. **Rules without `paths:` are an anti-pattern** — same cost as putting it in CLAUDE.md
