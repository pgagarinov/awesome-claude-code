# Multi-Agent Docker Harness

Run multiple Claude Code agents in parallel on a shared Git repo using Docker
containers and a file-based task locking protocol.

## Inspiration

This example combines ideas from two sources:

- [Building a C Compiler with Claude](https://www.anthropic.com/engineering/building-c-compiler)
  — Nicholas Carlini's approach of orchestrating multiple Claude Code agents
  working on a shared codebase, each claiming tasks from a shared pool
- [Claude Code Agent Teams](https://reliantlabs.io/blog/claude-code-agent-teams)
  — Reliant Labs' pattern for running parallel Claude Code instances that
  coordinate through Git

The key insight from both: you don't need a complex orchestration framework.
Git itself can be the coordination layer. Agents push and pull from a shared
bare repo, claim tasks via lock files, and resolve conflicts through rebasing.

## How It Works

```
   run.sh
     |
     +-- creates a bare Git repo from your project
     +-- builds a Docker image with Claude Code pre-installed
     +-- launches N containers, each running agent_loop.sh
     |
     v
  +------------+   +------------+   +------------+
  | cc-agent-1 |   | cc-agent-2 |   | cc-agent-3 |
  |            |   |            |   |            |
  | clone repo |   | clone repo |   | clone repo |
  | read prompt|   | read prompt|   | read prompt|
  | claim task |   | claim task |   | claim task |
  | implement  |   | implement  |   | implement  |
  | test       |   | test       |   | test       |
  | push       |   | push       |   | push       |
  | loop...    |   | loop...    |   | loop...    |
  +-----+------+   +-----+------+   +-----+------+
        |               |               |
        v               v               v
  +------------------------------------------+
  |        upstream.git (bare repo)          |
  |                                          |
  |  current_tasks/                          |
  |    task_a.txt       (task description)   |
  |    task_a.lock      (claimed by agent-1) |
  |    task_b.txt       (unclaimed)          |
  +------------------------------------------+
```

Each agent runs in its own Docker container and communicates exclusively
through the shared bare Git repo. There is no direct inter-agent communication.

### Task Coordination

Agents coordinate without a central lock server. The bare Git repo IS the
coordination layer:

1. Agent pulls latest, finds an unclaimed task (`.txt` file with no `.lock`)
2. Creates a `.lock` file containing its agent ID
3. Commits and pushes the lock
4. If push fails (another agent pushed first), rebases — if the lock conflicts,
   that means someone else claimed it first, so the agent picks a different task
5. After implementing, the agent removes the `.lock` and moves to the next task

This handles race conditions naturally through Git's built-in conflict
detection.

### Agent Loop

Each container runs `agent_loop.sh`, which repeats until `MAX_ITERATIONS` is
reached:

1. **Fresh clone** — `rm -rf /workspace/repo && git clone /upstream`
2. **Invoke Claude** — `claude -p "$(cat AGENT_PROMPT.md)"` with full
   autonomy (`--dangerously-skip-permissions`)
3. **Sleep and repeat** — Claude handles all git operations (commit, pull,
   push, rebase, conflict resolution) during its session

Re-cloning each iteration ensures the agent always sees the latest state,
including tasks claimed by other agents and newly pushed code.

### Why a Loop?

**Fresh state each iteration.** Over a long session, the local checkout drifts
from the shared repo. Re-cloning gives each iteration the latest project state.

**Resilience to failures.** A single Claude session can fail (context window
full, API error, tool hang). The loop lets the agent recover by starting fresh.

**`--max-iterations` controls cost.** Setting `--max-iterations 1` gives each
agent exactly one Claude session — useful for tests and predictable cost.
Without a limit, agents loop until all goals are complete.

## Prerequisites

- **Docker** — for running agent containers
- **Claude Code CLI** — authenticated (the harness extracts your OAuth token
  from the macOS Keychain automatically)

## Quick Start

```bash
# Point at your Claude Code config (for authentication)
export CLAUDE_CONFIG_DIR="$HOME/.claude"

# Launch 3 agents on your project
./run.sh --agents 3 --project-dir ./my-project

# Monitor progress (Haiku-powered periodic summaries)
./monitor.sh

# Check container status and recent commits
./status.sh

# Stop all agents
./stop.sh
```

### `run.sh` Options

| Flag | Default | Description |
|------|---------|-------------|
| `--agents N` | 2 | Number of parallel agents |
| `--project-dir PATH` | (required) | Path to project with `AGENT_PROMPT.md` |
| `--max-iterations N` | 0 (unlimited) | Max loop iterations per agent |
| `--model MODEL` | `claude-opus-4-6` | Claude model to use |

## Project Setup

Your project directory must contain an `AGENT_PROMPT.md` file telling agents
what to build. See `AGENT_PROMPT.template.md` for the expected format:

- **Description** — what the project is
- **Setup** — how to install dependencies and build
- **Running Tests** — test commands
- **Goals** — numbered list of tasks for agents to work on
- **Task Coordination Protocol** — the locking rules (included in the template)

Tasks go in a `current_tasks/` directory as `.txt` files, one per task.

## Authentication

Three methods are supported, checked in priority order:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Direct API key — used first if set |
| `CLAUDE_CODE_OAUTH_TOKEN` | Raw OAuth token — used if no API key |
| `CLAUDE_CONFIG_DIR` | Path to Claude config dir — token extracted from macOS Keychain |

The recommended approach is `CLAUDE_CONFIG_DIR="$HOME/.claude"`, which uses
your existing Claude Code login without any manual token copying.

## Sample Projects

The `tests/samples/` directory contains three sample projects for testing:

| Sample | Agents | Tasks | What It Tests |
|--------|--------|-------|---------------|
| `hello-python` | 2 | 2 | Minimal: one function + tests |
| `fizzbuzz` | 1 | 2 | Single agent: function + CLI |
| `csv-stats` | 3 | 5 | Full coordination: 5 tasks, 3 agents racing |

Run a sample:

```bash
export CLAUDE_CONFIG_DIR="$HOME/.claude"
./tests/run_test.sh hello-python --agents 2
```

The test runner launches agents with `--max-iterations 1`, waits for
completion, then runs three evaluation layers:

1. **Acceptance checks** — Sonnet evaluates code against `ACCEPT_SPEC.md`
2. **Behavior analysis** — Haiku evaluates agent coordination from logs
3. **Monitor checks** — verifies the monitoring system worked

## Deep Dive

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed component diagrams
covering the startup sequence, Docker container layout, task locking protocol
(including race condition resolution), Git data flow, monitor system, test
framework, and authentication flow.

## Scripts Reference

| Script | Description |
|--------|-------------|
| `run.sh` | Initialize bare repo, build image, launch agent containers |
| `agent_loop.sh` | Entrypoint inside each container (clone, claude, push, repeat) |
| `monitor.sh` | Periodic Haiku-powered summaries of agent activity |
| `status.sh` | Show container status, recent commits, and log tails |
| `stop.sh` | Stop and remove all agent containers |
