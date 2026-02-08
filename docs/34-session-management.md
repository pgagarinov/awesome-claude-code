# Part 34: Session Management

## Overview

Claude Code provides powerful session management features for organising, resuming, and navigating your work across conversations.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SESSION MANAGEMENT                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Named Sessions          Resume & History          Utilities                   │
│  ──────────────          ────────────────          ─────────                   │
│  /rename <name>          /resume                   /rewind                     │
│  --resume <name>         Ctrl+R (history search)   /export                     │
│  --from-pr <num>         --continue                --session-id                │
│                          --resume <id>             /compact                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Named Sessions

Name your sessions for easy recall:

```
> /rename auth-refactor
```

Resume by name later:

```bash
claude --resume auth-refactor
```

### Session Resume Hint

On exit, Claude Code shows a hint with the command to resume your session:

```
To resume this conversation, run:
  claude --resume auth-refactor
```

## Resuming Sessions

### Continue Most Recent

```bash
# Resume the most recent session
claude --continue
claude -c
```

### Resume a Specific Session

```bash
# By session ID
claude --resume ses_abc123

# By name
claude --resume auth-refactor
```

### Session Picker

`claude --resume` opens an interactive picker:

- `↑`/`↓` — Navigate sessions
- `Enter` — Select session
- `P` — Preview session
- `R` — Rename session
- `/` — Search sessions
- `B` — Filter by git branch

Sessions are grouped by repository and worktree, with forked sessions grouped together.

### In-Session Resume

Switch conversations without leaving Claude Code:

```
> /resume
# Opens session picker

> /resume auth-refactor
# Resume directly by name
```

## History Search

Press `Ctrl+R` to search through your prompt history, similar to bash/zsh:

```
(reverse-i-search): auth
> Fix the authentication bug in login.py
```

Navigate results with `↑`/`↓` and press `Enter` to use the selected prompt.

## Session Undo with /rewind

Undo conversation to a previous point, reverting code changes:

```
> /rewind
```

Opens a message selector to choose the point to rewind to. Claude undoes any file changes made after that point.

### Partial Summarisation

Use "Summarize from here" in the message selector to summarise part of the conversation without losing recent context.

## Exporting Sessions

Export a conversation for sharing:

```
> /export
```

Creates a shareable summary of the conversation.

## PR-Linked Sessions

Link sessions to GitHub pull requests:

```bash
# Resume sessions linked to a PR
claude --from-pr 123
claude --from-pr https://github.com/org/repo/pull/123
```

Sessions created via `gh pr create` are automatically linked to the PR.

## Custom Session IDs

Use custom session IDs for programmatic workflows:

```bash
claude --session-id my-custom-id

# Combine with forking
claude --resume ses_abc --fork-session --session-id my-fork
```

## Session Statistics

View interesting session statistics:

```
> /stats
```

Shows usage graphs, favourite model, usage streak, and more. Press `r` to cycle between time ranges (7 days, 30 days, all time).

## Official Documentation

- [Session Management](https://code.claude.com/docs/en/common-workflows#resume-previous-conversations)
