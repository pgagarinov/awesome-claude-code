# Part 7: Effective Prompting

## Prompting Regimes

### 1. Direct Execution (Default)
For straightforward tasks where you trust Claude's approach:

```
> Add input validation to the create_user endpoint

> Fix the TypeError in services/payment.py line 45

> Write pytest tests for the UserService class
```

### 2. Plan Mode
For complex tasks where you want to review the approach first:

```
> /plan Refactor the authentication system to use OAuth2

> I want to add caching. Enter plan mode and design the approach before implementing.
```

**When to use Plan Mode:**
- Architectural changes
- Multi-file refactoring
- Unfamiliar codebases
- When multiple valid approaches exist

Enable plan mode via CLI with `claude --permission-mode plan` or toggle with `Shift+Tab` during a session. See [Common Workflows: Plan Mode](https://code.claude.com/docs/en/common-workflows#use-plan-mode-for-safe-code-analysis).

### 3. Exploration Mode
When you need information before acting:

```
> Before making any changes, explore how error handling currently
  works across the codebase and summarise the patterns used.

> Don't modify anything yet - just explain how the payment flow works.
```

### 4. Extended Thinking
For complex reasoning tasks, enable extended thinking mode to allocate dedicated thinking tokens:

```
> Design the optimal indexing strategy for this database query.
  Consider query patterns, write frequency, and storage constraints.
```

Enable extended thinking via:
- CLI flag: `claude --thinking-budget 10000` (specify token budget)
- Keyboard toggle: Press `Alt+T` during a session to enable/disable thinking mode
- Settings: Configure default thinking budget in `~/.claude/settings.json`

**Note:** The `ultrathink` keyword syntax was deprecated in v2.1.0. Use the methods above instead.

See [Part 27: Extended Thinking](27-extended-thinking.md) for full details on thinking modes, token budgets, and configuration options.

## Prompt Patterns

### The Context-Setting Pattern

```
Context: We're building a REST API for a mobile app.
Constraint: Must support offline-first architecture.
Task: Design the sync mechanism for user data.
Output: Implementation plan with code examples.
```

### The Step-by-Step Pattern

```
Implement user authentication:
1. First, show me your planned approach
2. Wait for my approval
3. Then implement step by step
4. Test each component before moving on
```

### The Constraint Pattern

```
Refactor this function with these constraints:
- No external dependencies
- Must remain backwards compatible
- Keep under 50 lines
- Include error handling
```

### The Example-Driven Pattern

```
Add a new API endpoint following the exact pattern used in
src/api/users.py - same structure, error handling, and response format
```

### The Negative Pattern

```
Update the database schema.
Do NOT:
- Drop any existing columns
- Change column types
- Modify indexes on production tables
```

## Multi-Phase Workflows

```
Let's refactor the payment module:

Phase 1 - Analysis:
- Map all payment-related files
- Identify dependencies
- Document current flow

Phase 2 - Planning:
- Propose new structure
- Identify breaking changes
- Plan migration path

Phase 3 - Implementation:
- Implement changes incrementally
- Update tests after each change
- Verify no regressions

Start with Phase 1 and wait for my go-ahead before each phase.
```

> **Preventing Premature Stops**: Multi-phase workflows are prone to Claude stopping between phases or within a phase before completion. To prevent this, use the Ralf Loop pattern with phase-specific validation hooks. See [Part 14: The Ralf Loop - Preventing Premature Stops](14-ralf-loop.md) for implementation details.
