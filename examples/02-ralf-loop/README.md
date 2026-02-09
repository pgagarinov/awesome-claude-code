# RALF Loop - Self-Healing AI Coding Demo

**RALF = Run All tests, Loop on Failure**

## The Problem

When you ask an AI coding agent to change your code, it might break something.
Normally you'd have to notice the breakage yourself, paste the error back, and
ask for a fix. That's slow and error-prone.

## The Idea

What if the agent **couldn't finish** until all tests pass?

Claude Code has a feature called **hooks** - commands that run automatically at
certain points. One hook type is **Stop** - it fires every time Claude tries to
finish its response. If the hook command exits with a non-zero code (failure),
Claude sees the output and **must keep going** to fix the problem.

This creates a loop:

```
   You ask Claude to change code
              |
              v
     Claude edits app.py
              |
              v
     Claude tries to stop
              |
              v
   Stop hook runs pytest -----> Tests pass? --yes--> Claude stops. Done.
              ^                      |
              |                     no
              |                      |
              |                      v
              +---- Claude sees the failure,
                    fixes the code, and
                    tries to stop again
```

Claude **cannot stop responding** until the tests pass. It will keep fixing
code in a loop until everything is green. That's the RALF loop.

## How It Works (3 Files)

### 1. `app.py` - The code being guarded

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b
```

### 2. `tests/test_app.py` - The safety net

```python
def test_greet_returns_hello():
    assert greet("World") == "Hello, World!"

def test_add_positive_numbers():
    assert add(2, 3) == 5
```

### 3. `.claude/settings.json` - The hook (this is the magic)

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cd $CLAUDE_PROJECT_DIR && python -m pytest tests/ -v 2>&1 | tail -20",
            "timeout": 30000
          }
        ]
      }
    ]
  }
}
```

That's it. Three files. The hook is just one shell command: run pytest.

- Exit code 0 (tests pass) = Claude can stop
- Exit code 1 (tests fail) = Claude is blocked, sees the output, must fix

## Protections (Preventing Claude from Cheating)

Without protections, Claude could "pass" the tests by:
- Deleting the test file
- Weakening the assertions
- Editing `.claude/settings.json` to remove the hook

Two mechanisms prevent this:

### 1. Permission deny list (in `.claude/settings.json`)

```json
"permissions": {
  "deny": [
    "Edit(.claude/settings.json)",
    "Write(.claude/settings.json)",
    "Edit(tests/**)",
    "Write(tests/**)"
  ]
}
```

Claude is physically blocked from modifying test files or the hook config.
It can only fix problems by changing `app.py` - the production code.

### 2. Early exit (in the hook command)

```bash
git diff --name-only HEAD -- . | grep -q '\.py$'
```

If no `.py` files changed (e.g. Claude only edited docs), the hook skips
entirely. No wasted time running tests when nothing relevant changed.

### What this means for the demo

When Claude hits a failing test, its only option is to fix `app.py`.
It cannot:
- Edit the tests to match its broken code
- Delete the test file
- Disable the hook
- Skip the check

This forces Claude to do what you actually want: **fix the code, not the
tests**.

## Prerequisites

- Python 3.10+
- Claude Code CLI installed ([claude.ai/download](https://claude.ai/download))
- Install dependencies: `pip install -e .` (installs pytest)

## Demo: Try It Yourself

### Step 1: Start Claude Code in this folder

```bash
cd ralf-loop
claude
```

### Step 2: Ask Claude to break something

Type this prompt:

> Change the greet function to return "Hi" instead of "Hello"

### Step 3: Watch the loop

Here's what will happen:

1. Claude changes `app.py` to return `f"Hi, {name}!"`
2. Claude tries to finish
3. The Stop hook runs pytest
4. `test_greet_returns_hello` **fails** because it expects `"Hello, World!"`
5. Claude sees the failure and fixes the test (or the code)
6. The hook runs again
7. All tests pass - Claude stops

You'll see this play out in real time in the terminal.

### Step 4: Try a harder one

> Add a `multiply` function and make `add` return `a - b` instead

Now Claude must:
- Fix `add` (the test will catch the wrong behavior)
- Add `multiply` (no test exists yet, so the hook won't catch missing tests -
  but you can add a test requirement to the prompt!)

### Step 5: Make it stricter

Try this prompt:

> Add a divide function. Write a test for it too. Make sure division by zero
> raises a ValueError.

Now Claude writes both code and tests - and the hook verifies everything works
together before Claude can finish.

## Why This Matters

| Without RALF Loop | With RALF Loop |
|---|---|
| Claude changes code, says "done" | Claude changes code, tries to stop |
| You run tests manually | Tests run automatically |
| You paste the error back | Claude sees the error directly |
| You ask Claude to fix it | Claude fixes it on its own |
| Back and forth, multiple messages | One prompt, fully resolved |

The RALF loop turns Claude from a **tool you supervise** into an **agent that
self-corrects**.

## Going Further

This demo uses a simple pytest run. In a real project, the Stop hook can run
anything:

- Linting (`ruff check`)
- Type checking (`pyright`)
- Integration tests
- Multiple validation tiers

The [pixi-project-skeleton](https://github.com/HighviewPower/pixi-project-skeleton)
repository uses a 6-tier validation pipeline in its Stop hook: formatting,
code validation, fast tests, slow tests, Docker builds, and local CI replay.

Same principle, just more checks.
