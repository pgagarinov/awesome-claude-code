# RALF Loop Demo

**RALF = Run All tests, Loop on Failure**

This project demonstrates a Claude Code "Stop hook" that forces Claude to fix
failing tests before it can finish responding.

## Rules

- **Tests are truth.** Never modify tests to make them pass. Fix `app.py`.
- **Do not touch `.claude/settings.json`.** The hook config is protected.
- **Do not touch `tests/`.** Test files are protected by permissions.
- When the Stop hook fails, fix the production code in `app.py`.

## Files

- `app.py` - The only file you should edit
- `tests/test_app.py` - Protected tests (read-only for Claude)
- `.claude/settings.json` - Protected hook config (read-only for Claude)
