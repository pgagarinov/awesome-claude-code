# Part 12: Custom Slash Commands

## Creating Custom Commands

Create `.claude/commands/` directory in your project with markdown files:

```
project/
└── .claude/
    └── commands/
        ├── review.md
        ├── test.md
        └── deploy-check.md
```

## Command Structure

```markdown
# .claude/commands/review.md

Review the current changes for:
- Code quality issues
- Potential bugs
- Security vulnerabilities
- Performance concerns

Provide specific, actionable feedback.
```

**Usage:** `/project:review`

## Examples

### Code Review Command

```markdown
# .claude/commands/review.md

Review the staged changes (git diff --cached) for:

1. **Code Quality**
   - Naming conventions
   - Function length and complexity
   - DRY violations

2. **Potential Bugs**
   - Edge cases
   - Null/None handling
   - Error handling

3. **Security**
   - Input validation
   - SQL injection
   - Sensitive data exposure

4. **Testing**
   - Are new functions tested?
   - Are edge cases covered?

Provide specific line-by-line feedback.
```

### New Feature Command

```markdown
# .claude/commands/new-feature.md

Create a new feature following our project patterns:

Feature: $ARGUMENTS

Steps:
1. Create model in src/models/
2. Create schema in src/schemas/
3. Create service in src/services/
4. Create API routes in src/api/
5. Add tests in tests/
6. Update API documentation

Follow patterns from existing features. Ask clarifying questions if needed.
```

**Usage:** `/project:new-feature user preferences`

### Debug Command

```markdown
# .claude/commands/debug.md

Debug the following issue:

Issue: $ARGUMENTS

Process:
1. Identify relevant files
2. Trace the code path
3. Identify root cause
4. Propose fix
5. Wait for approval before implementing
```

**Usage:** `/project:debug users can't log in after password reset`

## Personal Commands

Create user-wide commands in `~/.claude/commands/`:

```
~/.claude/
└── commands/
    ├── my-review.md     # Available in all projects as /user:my-review
    └── standup.md       # /user:standup
```

Personal commands are prefixed with `/user:` to distinguish from project commands (`/project:`).

See [Common Workflows: Custom Slash Commands](https://code.claude.com/docs/en/common-workflows#create-custom-slash-commands).
