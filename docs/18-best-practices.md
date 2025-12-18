# Part 17: Best Practices & Tips

## Do's and Don'ts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BEST PRACTICES                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  DO ✓                                                                           │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Create a CLAUDE.md for every project                                         │
│  • Be specific in your requests                                                 │
│  • Use /plan for complex changes                                                │
│  • Start fresh sessions for new tasks                                           │
│  • Let subagents handle exploration                                             │
│  • Review generated code before committing                                      │
│  • Use custom commands for repetitive workflows                                 │
│                                                                                 │
│  DON'T ✗                                                                        │
│  ─────────────────────────────────────────────────────────────────────────────  │
│  • Don't read entire large files unnecessarily                                  │
│  • Don't continue sessions across unrelated tasks                               │
│  • Don't give vague prompts ("fix this", "improve this")                        │
│  • Don't skip reviewing generated code                                          │
│  • Don't forget to use /compact in long sessions                                │
│  • Don't ignore permission prompts - understand what's being done               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Productivity Tips

### 1. Create Project-Specific Commands

```markdown
# .claude/commands/pr.md
Create a pull request for the current branch:
1. Summarise all commits since branching from main
2. Generate a clear PR title and description
3. Create the PR using gh cli
```

### 2. Use Templates in CLAUDE.md

```markdown
## Code Patterns

When creating new endpoints, follow this template:
\```python
@router.post("/", response_model=schemas.Response)
async def create_item(
    data: schemas.CreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> schemas.Response:
    """Create a new item."""
    return await services.item.create(db, data=data, user=user)
\```
```

### 3. Leverage Non-Interactive Mode for Scripts

```bash
# Quick checks
claude -p "are there any TODO comments in src/?"

# Generate and save
claude -p "write a README for this project" > README.md

# Chain with other tools
claude -p "list all API endpoints" | grep POST
```

### 4. Use Keyboard Shortcuts

- `Ctrl+C` / `⌃C` to interrupt long operations
- `↑` / `↓` to recall previous prompts
- `Tab` to autocomplete paths
- `Ctrl+L` / `⌘K` to clear screen

### 5. Regular Context Maintenance

```
# Check context usage periodically
> /status

# Compact when above 50%
> /compact

# Start fresh for unrelated tasks
$ claude  # (not --continue)
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     CLAUDE CODE QUICK REFERENCE                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  STARTING                          SESSION COMMANDS                             │
│  claude                            /help         - Show help                    │
│  claude "prompt"                   /status       - Session info                 │
│  claude -c (continue)              /compact      - Reduce context               │
│  claude -p "prompt" (print)        /clear        - Clear history                │
│  claude --compact                  /plan         - Enter plan mode              │
│                                                                                 │
│  KEYBOARD (PC / Mac)               PROMPTING                                    │
│  Ctrl+C / ⌃C   - Cancel            Be specific, not vague                       │
│  Ctrl+D / ⌃D   - Exit              Use /plan for complex tasks                  │
│  ↑/↓           - History           Add constraints explicitly                   │
│  Tab           - Autocomplete      Reference existing patterns                  │
│                                                                                 │
│  CONTEXT TIPS                      FILES                                        │
│  Fresh session = new task          Use CLAUDE.md for project context            │
│  /compact when > 50% full          Route to detailed docs                       │
│  Subagents for exploration         Read sections, not whole files               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Additional Resources

### Official Documentation
- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- [Common Workflows](https://docs.anthropic.com/en/docs/claude-code/common-workflows)
- [Settings Reference](https://docs.anthropic.com/en/docs/claude-code/settings)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

### Repositories
- [anthropics/claude-code](https://github.com/anthropics/claude-code)
- [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action)
