# Part 25: Working on Multiple Features in Parallel

## The Challenge

When working on multiple features or bug fixes simultaneously, each needs an isolated environment:
- Separate branches with different code states
- Independent Claude Code sessions
- No cross-contamination of changes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL FEATURE DEVELOPMENT                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional (slow):                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                                  │
│  │Feature A │→ │Feature B │→ │Feature C │    Sequential: 3× time           │
│  │  stash   │  │  stash   │  │  stash   │                                  │
│  └──────────┘  └──────────┘  └──────────┘                                  │
│                                                                             │
│  With worktrees (fast):                                                     │
│  ┌──────────┐                                                               │
│  │Feature A │──┐                                                            │
│  └──────────┘  │                                                            │
│  ┌──────────┐  │                                                            │
│  │Feature B │──┼──► All features in parallel                                │
│  └──────────┘  │                                                            │
│  ┌──────────┐  │                                                            │
│  │Feature C │──┘                                                            │
│  └──────────┘                                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Option A: Git Worktrees (Recommended)

Git worktrees create isolated working directories that share the same Git history. Each worktree has its own file state and branch.

### Setup

```bash
# From your main repository
cd ~/projects/my-app

# Create a worktree for feature A
git worktree add ../my-app-feature-a -b feature-a

# Create a worktree for feature B (from existing branch)
git worktree add ../my-app-feature-b feature-b

# List all worktrees
git worktree list
```

Output:
```
/Users/you/projects/my-app              abc1234 [main]
/Users/you/projects/my-app-feature-a    def5678 [feature-a]
/Users/you/projects/my-app-feature-b    ghi9012 [feature-b]
```

### Running Claude Code in Each Worktree

**Terminal 1:**
```bash
cd ~/projects/my-app-feature-a
claude
```

**Terminal 2:**
```bash
cd ~/projects/my-app-feature-b
claude
```

Each Claude Code instance works independently with its own:
- Branch and file state
- Session history
- Tool permissions

### Initialize Each Worktree

Remember to set up dependencies in new worktrees:

```bash
# JavaScript/Node
cd ../my-app-feature-a
npm install

# Python
cd ../my-app-feature-a
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Rust
cd ../my-app-feature-a
cargo build
```

### Session Management Across Worktrees

Claude Code's `/resume` command sees sessions from all worktrees in the same repository:

```bash
# From any worktree
claude --resume

# Name sessions for clarity
> /rename feature-a-auth-work
```

### Managing Worktrees

```bash
# List worktrees
git worktree list

# Remove a worktree (after merging)
git worktree remove ../my-app-feature-a

# Or manually
rm -rf ../my-app-feature-a
git worktree prune
```

### Merging Changes

When feature A is ready:

```bash
# In main worktree
cd ~/projects/my-app
git checkout main
git merge feature-a

# Clean up
git worktree remove ../my-app-feature-a
git branch -d feature-a
```

See also [Common Workflows: Git Worktrees](https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-git-worktrees).

## Option B: AutoClaude

[AutoClaude](https://github.com/AndyMik90/Auto-Claude) is an autonomous multi-agent framework that automates parallel development workflows.

### What It Provides

- **Up to 12 parallel agent terminals**: Multiple Claude instances working simultaneously
- **Automatic worktree management**: Creates isolated environments automatically
- **AI-powered merge resolution**: Handles conflicts when combining work
- **Self-validating QA loop**: Each agent validates its work before integration
- **Memory layer**: Agents retain knowledge across sessions

### Basic Usage

```bash
# Clone and install
git clone https://github.com/AndyMik90/Auto-Claude.git
cd Auto-Claude
npm install

# Start AutoClaude
npm start
```

### When to Use AutoClaude

| Use Case | AutoClaude | Git Worktrees |
|----------|------------|---------------|
| Solo developer | Overkill | Simple and sufficient |
| Multiple related features | Good fit | Manual coordination |
| Large team | Excellent | Works but more manual |
| Complex orchestration | Built-in | DIY |
| CI integration | Built-in | Manual setup |

## Comparison

| Feature | Git Worktrees | AutoClaude |
|---------|---------------|------------|
| Setup complexity | Low (built into Git) | Medium (separate install) |
| Max parallel sessions | Unlimited | 12 terminals |
| Merge handling | Manual | AI-assisted |
| Learning curve | Minimal | Moderate |
| Coordination | Manual | Automated |
| Cost | Free | Free (uses your API key) |
| Best for | Solo/small teams | Teams, complex features |

## Best Practices

### 1. Name Sessions Clearly

```bash
# In each worktree
> /rename auth-feature-work
> /rename payment-refactor
```

### 2. Use Descriptive Branch Names

```bash
git worktree add ../app-auth -b feature/user-authentication
git worktree add ../app-payment -b fix/payment-validation
```

### 3. Keep Worktrees Short-Lived

Merge and remove worktrees promptly to avoid:
- Merge conflicts accumulating
- Disk space bloat
- Confusion about which worktree is which

### 4. Share CLAUDE.md

Your CLAUDE.md file is per-repository, shared across worktrees. Keep it in the main branch so all worktrees benefit from the same project context.

### 5. Consider Resource Usage

Each Claude Code session consumes:
- API calls (costs)
- Memory (~100-300MB per session)
- File watchers

Run only as many parallel sessions as you need.

## Common Workflows

### Workflow 1: Bug Fix While Working on Feature

```bash
# Currently working on feature
cd ~/projects/my-app-feature

# Urgent bug comes in - create worktree without leaving feature
git worktree add ../my-app-hotfix -b hotfix/critical-bug

# New terminal
cd ../my-app-hotfix
claude
# Fix bug, commit, push, create PR

# Clean up after merge
git worktree remove ../my-app-hotfix
```

### Workflow 2: Review PR While Working

```bash
# Create worktree for PR review
git fetch origin
git worktree add ../my-app-review origin/pr-123

cd ../my-app-review
claude
# Review, test, comment

# Clean up
git worktree remove ../my-app-review
```

### Workflow 3: Compare Approaches

```bash
# Try two different implementations
git worktree add ../my-app-approach-a -b experiment/approach-a
git worktree add ../my-app-approach-b -b experiment/approach-b

# Terminal 1: Claude implements approach A
# Terminal 2: Claude implements approach B

# Compare results, keep the better one
```

## Summary

| Task | Command |
|------|---------|
| Create worktree (new branch) | `git worktree add ../dir -b branch` |
| Create worktree (existing branch) | `git worktree add ../dir branch` |
| List worktrees | `git worktree list` |
| Remove worktree | `git worktree remove ../dir` |
| Prune stale worktrees | `git worktree prune` |
| Name Claude session | `/rename session-name` |
| Resume session | `claude --resume` |

## Troubleshooting

### "Branch already checked out"

```bash
# Can't create worktree for branch that's checked out elsewhere
git worktree add ../dir main  # Error if main is checked out

# Solution: Use a different branch or checkout something else first
```

### Worktree Out of Sync

```bash
# Update worktree with latest from remote
cd ../my-app-feature-a
git fetch origin
git rebase origin/main
```

### Stale Worktrees

```bash
# If you deleted a worktree folder manually
git worktree prune
```
