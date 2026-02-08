# Part 33: Background Tasks

## What Are Background Tasks?

Background tasks let you run operations in the background while continuing to work in your main Claude Code session. This includes bash commands, subagents, and full background agent sessions.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         BACKGROUND TASKS                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Main Session (foreground)          Background Tasks                           │
│  ─────────────────────────          ────────────────                           │
│                                                                                 │
│  You: "Fix the login bug"           Task 1: npm test (running)                 │
│  Claude: editing auth.py...         Task 2: Research API docs (agent)          │
│                                     Task 3: git fetch (completed)              │
│                                                                                 │
│  You continue working normally      Tasks notify on completion                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Starting Background Tasks

### The & Prefix

Start any message as a background task by prefixing with `&`:

```
> & Research all the API endpoints and document them in api-docs.md
```

The task runs independently while you continue working.

### Ctrl+B — Background a Running Task

Press `Ctrl+B` while a bash command or agent is running to send it to the background:

```
> Run the full test suite
  [Tests running... press Ctrl+B to background]

  # Press Ctrl+B
  Task backgrounded. You can continue working.
```

`Ctrl+B` backgrounds all running foreground tasks simultaneously.

### Auto-Background for Long-Running Commands

Bash commands that exceed the default timeout are automatically backgrounded instead of being killed. Customise the threshold with:

```bash
export BASH_DEFAULT_TIMEOUT_MS=120000  # 2 minutes (default)
```

## Managing Background Tasks

### View Running Tasks

```
> /tasks
```

Shows all background tasks with their status. If only one task is running, goes directly to task details.

### Task Notifications

When a background task completes, you receive a notification with the result:

```
Background task completed: "Research API endpoints"
  • Found 12 API endpoints across 4 service files
  • Documentation written to api-docs.md
```

Multiple completions are capped at 3 lines with an overflow summary.

## Background Agents

Background agents are full Claude sessions that run independently:

```
> & Analyse the entire codebase and create a dependency graph
```

Background agents:
- Run with their own context window
- Can use all tools (subject to permissions)
- Prompt for tool permissions before launching
- Notify the main session when complete

## Disabling Background Tasks

If background tasks cause issues, disable them entirely:

```bash
export CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1
```

This disables:
- The `&` prefix
- The `Ctrl+B` shortcut
- Auto-backgrounding of long-running commands

## Use Cases

### Running Tests While Editing

```
> & Run the full test suite and report any failures

# Continue working on code changes while tests run
> Fix the type error in utils.py
```

### Parallel Research

```
> & Research how other projects implement WebSocket authentication
> & Check if our API rate limiting follows best practices

# Both research tasks run simultaneously
```

### Dev Server and Work

```
> Start the dev server on port 3000
  # Press Ctrl+B to background the server

> Now fix the login form styling
```

## Official Documentation

- [Background Tasks](https://code.claude.com/docs/en/background-tasks)
