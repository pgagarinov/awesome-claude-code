# Project: CSV Stats

## Description
A Python tool to load CSV files, compute statistics, filter rows, and provide a CLI interface.

## Setup
No dependencies beyond Python 3 and pytest (`pip install pytest`).

## Running Tests
```bash
python -m pytest test_stats.py -v
```

## Goals
1. **`load_csv(path)`** in `stats.py` — reads a CSV file and returns a list of dicts (use `csv.DictReader`). Numeric-looking values should be converted to `float`.
2. **`compute_stats(rows, column)`** in `stats.py` — returns a dict with keys `min`, `max`, `mean`, `median` for the given column's numeric values.
3. **`filter_rows(rows, column, op, value)`** in `stats.py` — filters rows where `column op value` is true. Supported ops: `>`, `<`, `==`, `>=`, `<=`. Value should be compared numerically if possible.
4. **CLI with argparse** — `python stats.py sample.csv --column score` prints stats. Adding `--filter "age>25"` filters first, then computes stats. Output should be human-readable.
5. **`test_stats.py`** — at least 8 pytest tests covering `load_csv`, `compute_stats`, `filter_rows`, and edge cases.

## Task Coordination Protocol

You are one of several agents working on this project simultaneously. You are responsible for all git operations — committing, pulling, pushing, and resolving merge conflicts.

### Task files
Each goal has a corresponding `current_tasks/<task_name>.txt` file describing the task. When an agent claims a task, it creates `current_tasks/<task_name>.lock` containing its agent ID.

### Claiming a task
1. First, `git pull origin main` to get the latest state.
2. Check `current_tasks/` — pick a `.txt` task that doesn't have a corresponding `.lock` file.
3. Create `current_tasks/<task_name>.lock` containing **only** your agent ID (e.g., `echo "agent-1" > current_tasks/<task_name>.lock`).
4. Run `git add current_tasks/<task_name>.lock && git commit -m "claim <task_name>" && git push origin main`.
5. **If the push fails**, another agent pushed concurrently. Run `git pull --rebase origin main`.
   - If the rebase has a **conflict on your `.lock` file**, another agent already claimed that task. Run `git rebase --abort`, then go back to step 1 and pick a **different** task.
   - If the rebase succeeds, check `cat current_tasks/<task_name>.lock`. If it contains a **different** agent's ID, their claim landed first. Run `git reset --hard origin/main`, then go back to step 1 and pick a different task.
   - If it still contains your agent ID, retry the push.
6. **After a successful push**, verify your claim: run `git pull origin main` and `cat current_tasks/<task_name>.lock`. If it contains your agent ID, the task is yours — begin working. If it contains a different ID, another agent won the race — pick a different task.

### Working on a task
1. Implement your changes and run tests.
2. Commit frequently with clear messages describing what was done.

### Pushing changes
1. Before pushing, always pull first: `git pull --rebase origin main`.
2. If there are merge conflicts, resolve them intelligently — keep both your changes and the other agent's changes where possible.
3. Push: `git push origin main`.
4. **If the push fails** (another agent pushed in the meantime), pull and rebase again, resolve any new conflicts, and retry. Repeat up to 5 times.

### Completing a task
1. Remove your lock file: `rm current_tasks/<task_name>.lock`
2. Commit the lock removal along with any final changes.
3. Pull and push as described above.
4. If other goals remain unclaimed, claim and work on another.

### Guidelines
- **You must push your changes before you finish.** Unpushed work is lost.
- Run tests before pushing.
- Keep changes focused on your claimed task.
- Do not modify files that another agent is actively working on (check `current_tasks/` for `.lock` files).
- If you finish all goals, you're done.
