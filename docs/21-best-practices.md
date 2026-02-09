# Part 21: Best Practices & Tips

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
│  • Use Ralf Loop pattern (Part 14) for critical tasks requiring completion     │
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

## Task Completion Guarantees

For long-running tasks where you need to guarantee Claude completes all work before stopping, use the **Ralf Loop pattern** with Stop hooks. This prevents the common frustration of Claude stopping prematurely before finishing everything you requested.

**When to use the Ralf Loop:**
- Production code changes requiring validation
- Multi-step features with dependencies
- Tasks with explicit testing/validation requirements
- Critical work that must be verified complete

**How it works:**
- Stop hooks intercept Claude's attempt to finish
- Run validation (tests, linting, builds)
- Block if validation fails, forcing Claude to fix issues
- Only approve when all completion criteria met

See [Part 14: The Ralf Loop - Preventing Premature Stops](14-ralf-loop.md) for implementation patterns and [Part 13: Claude Code Hooks](13-hooks.md) for configuration details.

---

## Checkpointing & Recovery

Claude Code automatically tracks the state of your code before each edit, providing a safety net for experimentation.

### How It Works

- **Automatic tracking**: Every user prompt creates a checkpoint
- **Persistent**: Checkpoints survive session restarts (30 days retention)
- **Selective recovery**: Restore code, conversation, or both

### Using Rewind

Press **`Esc` twice** (`Esc Esc`) or use `/rewind`:

```bash
> /rewind
```

Choose what to restore:
1. **Conversation only** - Rewind to earlier message, keep code changes
2. **Code only** - Revert files, keep conversation
3. **Both** - Restore code and conversation to prior point

### When to Use Checkpointing

- **Exploring alternatives**: Try different implementations safely
- **Recovering from mistakes**: Quickly undo broken changes
- **Ambitious refactoring**: Pursue big changes knowing you can revert

### Important Limitations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHECKPOINTING LIMITATIONS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ⚠️  Bash command changes are NOT tracked:                                  │
│      • rm file.txt                                                          │
│      • mv old.txt new.txt                                                   │
│      • git reset --hard                                                     │
│                                                                             │
│  ⚠️  Only Claude's file edits are tracked, not:                             │
│      • Manual edits outside Claude Code                                     │
│      • Changes from other sessions                                          │
│                                                                             │
│  ✓  Checkpointing complements Git, doesn't replace it                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Profile Switching (CLAUDE_CONFIG_DIR)

Use different Claude Code configurations for different contexts (work, personal, clients).

### Setting Up Profiles

Create separate config directories:

```bash
# Work profile
mkdir -p ~/.claude-work

# Personal profile
mkdir -p ~/.claude-personal

# Client-specific profile
mkdir -p ~/.claude-clientname
```

### Using Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Profile aliases
alias claude-work='CLAUDE_CONFIG_DIR=~/.claude-work claude'
alias claude-personal='CLAUDE_CONFIG_DIR=~/.claude-personal claude'
alias claude-client='CLAUDE_CONFIG_DIR=~/.claude-clientname claude'
```

### Profile Use Cases

| Profile | Configuration |
|---------|--------------|
| **Work** | Corporate MCP servers, strict permissions, audit logging |
| **Personal** | Relaxed permissions, personal API keys |
| **Client** | Client-specific settings, isolated credentials |
| **Testing** | Experimental settings, bypass permissions |

### Example: Work Profile Setup

```bash
# Create work profile
mkdir -p ~/.claude-work

# Copy base settings
cp ~/.claude/settings.json ~/.claude-work/

# Edit for work context
cat > ~/.claude-work/CLAUDE.md << 'EOF'
## Work Profile
- Follow corporate coding standards
- All commits require ticket numbers (JIRA-XXX)
- No external API calls without VPN
EOF

# Use it
claude-work
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
