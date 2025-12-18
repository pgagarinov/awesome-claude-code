# Part 2: The Claude Code Interface

When you run `claude`, you enter an interactive terminal session:

```
╭────────────────────────────────────────────────────────────────────────────────╮
│ Claude Code                                                    v1.0.0 (Opus)   │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ~/projects/my-app                                                             │
│                                                                                │
│  ┌─ Context ─────────────────────────────────────────────────────────────────┐ │
│  │ Files: 42  │  Tokens: 12,450 / 200,000  │  Session: 5m 32s               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  > What would you like to do?                                                  │
│                                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │ Type your message, or use:                                                │ │
│  │   /help          - Show available commands                                │ │
│  │   /status        - Show session info                                      │ │
│  │   Ctrl+C (⌃C)    - Cancel current operation                               │ │
│  │   Ctrl+D (⌃D)    - Exit Claude Code                                       │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
╰────────────────────────────────────────────────────────────────────────────────╯
```

## Interface Elements

| Element | Description |
|---------|-------------|
| **Status Bar** | Shows version, model, and connection status |
| **Working Directory** | Current project path |
| **Context Indicator** | Files loaded, tokens used, session duration |
| **Input Area** | Where you type prompts and commands |
| **Output Area** | Claude's responses, tool outputs, and status messages |
