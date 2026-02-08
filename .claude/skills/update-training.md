---
description: "Compare training materials against Claude Code changelog to find outdated content and gaps"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - WebFetch
argument-hint: "[version-range]"
---

# Update Training Materials Audit

Compare the training materials in this repository against the official Claude Code changelog to identify outdated content and uncovered features.

## Steps

1. **Fetch the changelog**: Fetch the latest changelog from `https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` using WebFetch.

2. **Parse changelog entries**: Extract all version entries and categorise changes into:
   - **New features**: Entirely new capabilities
   - **Deprecations**: Features marked as deprecated
   - **Removals**: Features that were removed
   - **Renames**: Features that changed names or locations
   - **Breaking changes**: Changes that affect existing usage

3. **Scan training materials**: Search all files in:
   - `docs/*.md`
   - `exercises/**/*.md`
   - `solutions/**/*.md`

4. **Cross-reference for issues**:

   a. **Outdated references**: Find training content that references deprecated or removed features. Check for:
      - `~/.claude.json` (should be `~/.claude/settings.json`)
      - `@-mention MCP` (removed in 2.1.6)
      - `claude config` CLI commands (deprecated in 1.0.7)
      - `# memory shortcut` (removed in 2.0.70)
      - `total_cost` (renamed to `total_cost_usd` in 1.0.22)
      - Old SDK package names

   b. **Uncovered new features**: Identify significant features from the changelog that are NOT mentioned in any training material. Focus on:
      - Major new features (plugins, background tasks, agent teams, etc.)
      - New CLI flags
      - New slash commands
      - New hook events
      - New SDK features

5. **Output a structured report** in this format:

```markdown
# Training Materials Audit Report

## Outdated References Found

| File | Line | Issue | Recommended Fix |
|------|------|-------|-----------------|
| docs/example.md | 42 | References deprecated `claude config` | Use settings.json instead |

## Uncovered Features

| Feature | Version Added | Category | Suggested Coverage |
|---------|--------------|----------|-------------------|
| Plugin system | 2.0.12 | Major | New doc: plugins.md |

## Summary
- X outdated references found
- Y uncovered features identified
- Z files scanned
```

If `$ARGUMENTS` specifies a version range (e.g., "2.0.0-2.1.37"), only audit changes within that range.
