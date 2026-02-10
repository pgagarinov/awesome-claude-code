# Architecture: Multi-Agent Claude Code Harness

A system for launching multiple Claude Code agents in parallel Docker containers
to collaborate on a shared Git repository via a file-based task locking protocol.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Map](#component-map)
3. [Startup Sequence](#startup-sequence)
4. [Docker Container Architecture](#docker-container-architecture)
5. [Agent Loop Lifecycle](#agent-loop-lifecycle)
6. [Task Coordination Protocol](#task-coordination-protocol)
7. [Git Data Flow](#git-data-flow)
8. [Monitor System](#monitor-system)
9. [Test Framework](#test-framework)
10. [Authentication Flow](#authentication-flow)
11. [File Reference](#file-reference)

---

## System Overview

```
+-------------------------------------------------------------------+
|                          HOST MACHINE                              |
|                                                                    |
|  +------------------+    +------------------+   +---------------+  |
|  |    run.sh        |    |   monitor.sh     |   |   stop.sh     |  |
|  | (orchestrator)   |    | (Haiku observer) |   | (teardown)    |  |
|  +--------+---------+    +--------+---------+   +---------------+  |
|           |                       |                                |
|           v                       v                                |
|  +------------------------------------------------------------+   |
|  |                  upstream.git  (bare repo)                  |   |
|  |                                                             |   |
|  |  refs/heads/main          agent_logs/                       |   |
|  |    |                        |                               |   |
|  |    +-- project files        +-- agent_1_iter1_*.log         |   |
|  |    +-- current_tasks/       +-- agent_2_iter1_*.log         |   |
|  |         +-- task_a.txt      +-- agent_3_iter1_*.log         |   |
|  |         +-- task_a.lock                                     |   |
|  |         +-- task_b.txt                                      |   |
|  +------------------------------------------------------------+   |
|           ^           ^           ^                                |
|           |           |           |   (docker volume mount)        |
|  +--------+--+ +------+-----+ +--+----------+                     |
|  | Container | | Container  | | Container   |                     |
|  | cc-agent-1| | cc-agent-2 | | cc-agent-3  |                     |
|  |           | |            | |             |                      |
|  | agent_    | | agent_     | | agent_      |                      |
|  | loop.sh   | | loop.sh    | | loop.sh     |                      |
|  |   |       | |   |        | |   |         |                      |
|  |   v       | |   v        | |   v         |                      |
|  | claude    | | claude     | | claude      |                      |
|  | (Opus)    | | (Opus)     | | (Opus)      |                      |
|  +-----------+ +------------+ +-------------+                     |
+-------------------------------------------------------------------+
```

Each agent runs in its own Docker container, communicates exclusively through
the shared bare Git repo mounted at `/upstream`, and writes logs to
`upstream.git/agent_logs/`. There is no direct inter-agent communication.

---

## Component Map

```
cc-harness-01-docker/
|
|-- run.sh                  Orchestrator: init repo, build image, launch containers
|-- stop.sh                 Graceful shutdown of all agent containers
|-- status.sh               Live view: containers, commits, log tails
|-- monitor.sh              Periodic Haiku-powered activity summaries
|-- agent_loop.sh           Entrypoint inside each container (clone -> claude -> push)
|-- Dockerfile              Container image: Ubuntu + Python + Node + Claude CLI
|-- AGENT_PROMPT.template.md   Template for project-specific agent instructions
|
|-- tests/
|   |-- run_test.sh         E2E test runner: launch agents, wait, evaluate
|   |-- accept.sh           Code quality checker (Sonnet evaluates ACCEPT_SPEC)
|   |-- analyze_logs.sh     Agent behavior checker (Haiku evaluates logs)
|   |
|   +-- samples/
|       |-- csv-stats/              3-agent test (5 tasks)
|       |   |-- ACCEPT_SPEC.md      10 acceptance criteria
|       |   +-- project/
|       |       |-- AGENT_PROMPT.md  Project goals + coordination protocol
|       |       |-- stats.py         Starter code (TODOs)
|       |       |-- sample.csv       Test data (10 rows)
|       |       +-- current_tasks/   Task definitions (5 .txt files)
|       |
|       |-- hello-python/           2-agent test (2 tasks)
|       |   |-- ACCEPT_SPEC.md
|       |   +-- project/
|       |
|       +-- fizzbuzz/               1-agent test (2 tasks)
|           |-- ACCEPT_SPEC.md
|           +-- project/
```

---

## Startup Sequence

`run.sh --agents 3 --project-dir ./project --max-iterations 1`

```
                         run.sh
                           |
            +--------------+--------------+
            |                             |
            v                             v
    1. Resolve Auth                2. Init Bare Repo
    (API key, OAuth,               (copy project -> tmp,
     or Keychain)                   git init, commit,
            |                       clone --bare)
            |                             |
            +----------+------------------+
                       |
                       v
              3. Build Docker Image
              (docker build -t cc-agent .)
                       |
                       v
              4. Stop Old Containers
              (docker rm -f cc-agent-{1..20})
                       |
                       v
              5. Launch N Containers
                       |
          +------------+------------+
          |            |            |
          v            v            v
     docker run    docker run   docker run
     cc-agent-1    cc-agent-2   cc-agent-3
     AGENT_ID=1    AGENT_ID=2   AGENT_ID=3

     Each container mounts upstream.git at /upstream
     and receives auth credentials via -e env vars.
```

After launch, `run.sh` prints the monitor command and exits.
Agents continue running in the background.

---

## Docker Container Architecture

```
+-------------------------------------------------------+
|  Docker Container (cc-agent-N)                        |
|                                                       |
|  Image: cc-agent (built from Dockerfile)              |
|  Base:  ghcr.io/prefix-dev/pixi:noble (Ubuntu)       |
|                                                       |
|  Installed:                                           |
|    - git, curl, build-essential, jq                   |
|    - python3, pip, pytest                             |
|    - node.js 20, npm                                  |
|    - @anthropic-ai/claude-code (global)               |
|                                                       |
|  User: agent (non-root, required by claude CLI)       |
|                                                       |
|  Volumes:                                             |
|    /upstream  <---->  host: upstream.git/              |
|                                                       |
|  Env:                                                 |
|    AGENT_ID=N                                         |
|    MAX_ITERATIONS=1                                   |
|    CLAUDE_MODEL=claude-opus-4-6                       |
|    ANTHROPIC_API_KEY=... OR CLAUDE_CODE_OAUTH_TOKEN=. |
|                                                       |
|  Entrypoint: agent_loop.sh                            |
|                                                       |
|  Filesystem:                                          |
|    /workspace/repo/    <-- fresh clone each iteration |
|    /upstream/          <-- shared bare repo (mounted) |
|      +-- agent_logs/   <-- log files written here     |
+-------------------------------------------------------+
```

---

## Agent Loop Lifecycle

Each container runs `agent_loop.sh`, which repeats until `MAX_ITERATIONS` is reached:

```
agent_loop.sh (inside container, runs as user "agent")
|
+---> iteration = 1
|
|  1. Fresh Clone
|     rm -rf /workspace/repo
|     git clone /upstream /workspace/repo
|     cd /workspace/repo
|          |
|  2. Ensure .gitignore
|     (add __pycache__, .venv, etc. if missing)
|     git push origin main
|          |
|  3. Check for AGENT_PROMPT.md
|     (if missing, sleep 10 and retry)
|          |
|  4. Invoke Claude Code
|     +--------------------------------------------------+
|     | claude --dangerously-skip-permissions             |
|     |   -p "$(cat AGENT_PROMPT.md) ... agent-N"        |
|     |   --model claude-opus-4-6                        |
|     |   --output-format stream-json --verbose          |
|     |   2>&1 | tee /upstream/agent_logs/agent_N_*.log  |
|     +--------------------------------------------------+
|     |
|     |  Claude reads AGENT_PROMPT.md, then:
|     |    - Claims a task (creates .lock file)
|     |    - Implements the task (writes code)
|     |    - Runs tests
|     |    - Commits, pulls, pushes
|     |    - Removes .lock, claims next task
|     |    - Repeats until all tasks done
|     |
|  5. Sleep 2s
|
+---> iteration = 2 (if MAX_ITERATIONS allows)
|     ...
+---> exit (MAX_ITERATIONS reached)
```

Claude handles **all git operations** (commit, pull, push, rebase, conflict
resolution) autonomously inside step 4. The agent loop just provides the
environment and fresh clones.

---

## Task Coordination Protocol

Agents coordinate without any central lock server. The bare Git repo IS the
coordination layer. Each task is a `.txt` file; ownership is a `.lock` file.

### Repository State (current_tasks/)

```
current_tasks/
  |-- load_csv.txt           <-- task description (always present)
  |-- load_csv.lock          <-- "agent-1" (claimed by agent 1)
  |-- compute_stats.txt
  |-- compute_stats.lock     <-- "agent-2"
  |-- filter_rows.txt        <-- (no .lock = unclaimed, available)
  |-- cli.txt
  |-- tests.txt
```

### Claim Sequence (Happy Path)

```
Agent-1                        upstream.git                      Agent-2
  |                               |                                |
  |  git pull origin main         |                                |
  |<------------------------------|                                |
  |                               |                                |
  |  ls current_tasks/            |                                |
  |  (sees: load_csv.txt,         |                                |
  |   no load_csv.lock)           |                                |
  |                               |                                |
  |  echo "agent-1" >             |                                |
  |    load_csv.lock              |                                |
  |                               |                                |
  |  git add + commit + push ---->|                                |
  |  "claim load_csv"             |                                |
  |                               |                                |
  |  git pull (verify) ---------> |                                |
  |  cat load_csv.lock            |                                |
  |  => "agent-1" (confirmed!)    |                                |
  |                               |    git pull origin main        |
  |                               |------------------------------->|
  |                               |                                |
  |  (begin implementation)       |    ls current_tasks/           |
  |                               |    (sees load_csv.lock,        |
  |                               |     picks filter_rows instead) |
  |                               |                                |
  |                               |    echo "agent-2" >            |
  |                               |      filter_rows.lock          |
  |                               |                                |
  |                               |<-------------------------------+
  |                               |    git add + commit + push     |
  |                               |    "claim filter_rows"         |
```

### Claim Sequence (Race Condition — Resolved)

```
Agent-1                        upstream.git                      Agent-3
  |                               |                                |
  |  git pull origin main         |     git pull origin main       |
  |<------------------------------|------------------------------->|
  |                               |                                |
  |  (both see filter_rows        |  (both see filter_rows         |
  |   is unclaimed)               |   is unclaimed)                |
  |                               |                                |
  |  echo "agent-1" >             |     echo "agent-3" >           |
  |    filter_rows.lock           |       filter_rows.lock         |
  |                               |                                |
  |  git commit + push ---------> |                                |
  |  (SUCCESS - pushed first)     |                                |
  |                               |  <-- git commit + push --------|
  |                               |      (REJECTED! non-fast-fwd)  |
  |                               |                                |
  |                               |      git pull --rebase ------->|
  |                               |                                |
  |                               |      CONFLICT on                |
  |                               |      filter_rows.lock!          |
  |                               |                                |
  |                               |      git rebase --abort         |
  |                               |      (pick a DIFFERENT task)    |
  |                               |                                |
  |  git pull (verify)            |      echo "agent-3" >          |
  |  cat filter_rows.lock         |        cli.lock                |
  |  => "agent-1" (confirmed!)    |      git commit + push ------->|
  |                               |      (SUCCESS)                 |
```

Key rules that prevent duplicate work:

1. **Push rejection = someone else pushed first** — rebase and inspect
2. **Conflict on `.lock` file = task already claimed** — abort, pick another
3. **Post-rebase check** — if lock has different agent ID, abandon claim
4. **Post-push verify** — pull and confirm your ID is still in the lock

### Task Lifecycle

```
   UNCLAIMED              CLAIMED                COMPLETED
  +-----------+        +-----------+          +-----------+
  | task.txt  |------->| task.txt  |--------->| task.txt  |
  |           | claim  | task.lock | finish   |           |
  | (no lock) |        | ="agent-N"|          | (no lock) |
  +-----------+        +-----------+          +-----------+

  Agent actions:        Agent actions:          Agent actions:
  - git pull            - implement code        - rm task.lock
  - create .lock        - run tests             - git commit
  - git push            - git commit            - git push
  - verify claim        - git pull --rebase     - pick next task
                        - git push
```

### Push-Retry Flow (During Implementation)

```
Agent-N tries to push implementation changes:

    git pull --rebase origin main
              |
              v
     +------ rebase clean? ------+
     |                           |
    YES                          NO (conflict)
     |                           |
     v                           v
  git push              resolve conflicts
     |                  (keep both changes)
     v                           |
  success? ------+               v
     |           |          git rebase --continue
    YES          NO              |
     |        (rejected)         v
     v           |          git push (retry)
   done!    git pull             |
            --rebase       (repeat up to 5x)
            (retry)
```

---

## Git Data Flow

All agents push to and pull from the same bare repo. There is no branching —
everything happens on `main`.

```
+-------------------+        +-------------------+
|   cc-agent-1      |        |   cc-agent-2      |
|   /workspace/repo |        |   /workspace/repo |
|                   |        |                   |
|  working tree     |        |  working tree     |
|  + .git/          |        |  + .git/          |
+--------+----------+        +---------+---------+
         |                              |
         | git push                     | git push
         | git pull --rebase            | git pull --rebase
         |                              |
         v                              v
  +------+------------------------------+------+
  |         upstream.git (bare repo)           |
  |                                            |
  |  HEAD -> refs/heads/main                   |
  |                                            |
  |  Commit history (linear, rebased):         |
  |                                            |
  |  * agent-3: implement tests                |
  |  * agent-3: claim tests                    |
  |  * agent-1: implement cli                  |
  |  * agent-1: remove filter_rows.lock        |
  |  * agent-2: implement compute_stats        |
  |  * agent-1: implement filter_rows          |
  |  * agent-1: claim filter_rows              |
  |  * agent-2: claim compute_stats            |
  |  * agent-1: claim load_csv                 |
  |  * Initial project import                  |
  |                                            |
  |  agent_logs/ (not in git, on volume):      |
  |    agent_1_iter1_1738900000.log            |
  |    agent_2_iter1_1738900001.log            |
  |    agent_3_iter1_1738900002.log            |
  +--------------------------------------------+
         ^
         |  git pull --rebase
         |  git push
         |
+--------+----------+
|   cc-agent-3      |
|   /workspace/repo |
+-------------------+
```

Agent logs are written to the **bare repo's filesystem** (not tracked by git)
via the Docker volume mount. This lets the monitor and test framework read
them without agents needing to commit logs.

---

## Monitor System

`monitor.sh` runs on the host (or in the test harness) and periodically
summarizes agent activity using Claude Haiku.

```
                   monitor.sh (runs on host)
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
   Docker API     upstream.git    upstream.git/
   (container     (git log for    agent_logs/
    status)       new commits)    (byte offsets
          |             |          per file)
          |             |             |
          +------+------+------+------+
                 |             |
                 v             v
           has changes?   has new logs?
                 |             |
                 +------+------+
                        |
               +--------+--------+
               |                 |
              YES                NO
               |                 |
               v                 v
        Build delta          Print "no new
        prompt with          activity" and
        new data             sleep
               |
               v
        +-------------------+
        | claude (Haiku)    |
        | --model haiku-4.5 |
        | -p "$PROMPT"      |
        +-------------------+
               |
               v
        Print structured summary:
        - Agent Status
        - Recent Activity
        - New Commits
        - Issues

        Sleep $INTERVAL seconds
        (repeat)
```

### Monitor Delta Tracking

The monitor avoids re-processing old data by tracking:

```
State between iterations:
  +----------------------------------+
  | LAST_COMMIT = abc123f            |  <-- git HEAD at last check
  | LOG_OFFSETS = {                  |
  |   "agent_1_*.log" => 45230,     |  <-- byte offset per file
  |   "agent_2_*.log" => 38100,     |
  |   "agent_3_*.log" => 51000,     |
  | }                               |
  +----------------------------------+

Each cycle:
  1. Read current HEAD -- if different from LAST_COMMIT,
     fetch new commits with: git log LAST_COMMIT..HEAD
  2. stat() each log file -- if size > stored offset,
     read only the new bytes with: tail -c $NEW_BYTES
  3. If nothing changed, skip the Haiku call entirely
```

---

## Test Framework

`tests/run_test.sh` runs a full end-to-end test of the harness.

```
tests/run_test.sh csv-stats --agents 3
         |
         v
  1. Copy harness + sample to temp dir
         |
         v
  2. run.sh --agents 3 --project-dir ./project --max-iterations 1
     (launches 3 containers, they work, they finish)
         |
         v
  3. Start monitor.sh in background (--max-updates 3)
         |
         v
  4. docker wait cc-agent-{1,2,3}
     (block until all containers exit)
         |
         v
  5. Kill monitor, collect monitor output
         |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
  accept.sh             analyze_logs.sh     Monitor checks
  (code quality)        (agent behavior)    (inline in
         |                   |               run_test.sh)
         v                   v                   v
  +--------------+   +--------------+   +--------------+
  | Clone repo   |   | Parse logs   |   | grep monitor |
  | from bare    |   | (Python:     |   | output for   |
  |              |   |  extract git |   | updates,     |
  | Claude       |   |  ops, locks, |   | errors,      |
  | (Sonnet)     |   |  errors)     |   | activity     |
  | evaluates    |   |              |   |              |
  | against      |   | Claude       |   +--------------+
  | ACCEPT_SPEC  |   | (Haiku)      |         |
  |              |   | evaluates    |         |
  +--------------+   | 6 criteria   |         |
         |           +--------------+         |
         v                  v                  v
  ACCEPT_EXIT=0|1    ANALYZE_EXIT=0|1    MONITOR_EXIT=0|1
         |                  |                  |
         +------------------+------------------+
                            |
                            v
                   All zero? ----+---- Any non-zero?
                      |                    |
                      v                    v
               TEST PASSED            TEST FAILED
```

### Three Evaluation Layers

```
+-------------------------------------------------------------------+
|                    Layer 1: Acceptance Checks                      |
|                    (accept.sh + Sonnet)                            |
|                                                                   |
|  "Does the code work?"                                            |
|                                                                   |
|  Input:  cloned repo + ACCEPT_SPEC.md                             |
|  Method: Claude Sonnet runs scripts, imports modules, runs tests  |
|  Output: JSON with pass/fail per criterion                        |
|                                                                   |
|  Example criteria:                                                |
|    - load_csv returns 10 dicts with correct keys                  |
|    - compute_stats returns correct min/max/mean/median            |
|    - pytest reports 8+ passing tests                              |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                    Layer 2: Behavior Analysis                      |
|                    (analyze_logs.sh + Haiku)                       |
|                                                                   |
|  "Did agents collaborate correctly?"                              |
|                                                                   |
|  Input:  agent log files (stream-json NDJSON)                     |
|  Method: Python extracts coordination events,                     |
|          Claude Haiku evaluates against 6 criteria                |
|  Output: JSON with pass/fail per criterion                        |
|                                                                   |
|  Criteria:                                                        |
|    1. Push Success      - every agent pushed at least once        |
|    2. Conflict Resolution - conflicts resolved, not abandoned     |
|    3. No Duplicate Work - each task claimed by only one agent     |
|    4. Task Protocol     - .lock files created/removed properly    |
|    5. No Crashes        - no unrecovered fatal errors             |
|    6. Git Workflow      - pull before push, rebase on rejection   |
+-------------------------------------------------------------------+

+-------------------------------------------------------------------+
|                    Layer 3: Monitor Checks                         |
|                    (inline grep in run_test.sh)                    |
|                                                                   |
|  "Did the monitor work?"                                          |
|                                                                   |
|  Input:  monitor stdout captured to file                          |
|  Method: grep for expected patterns                               |
|  Output: 4 pass/fail checks                                      |
|                                                                   |
|  Checks:                                                          |
|    - Monitor produced at least one "Monitor Update"               |
|    - No "(Haiku summarization failed)" messages                   |
|    - Detected repo activity ("New Commits" or "no new activity")  |
|    - No bash errors (unbound variable, command not found, etc.)   |
+-------------------------------------------------------------------+
```

### Log Processing Pipeline (analyze_logs.sh)

```
agent_logs/*.log (stream-json NDJSON)
         |
         v
  Python extractor
  (inline in analyze_logs.sh)
         |
         |  Filters for:
         |    - Bash tool_use with git commands
         |    - Bash tool_use with current_tasks/*.lock paths
         |    - Write/Edit tool_use on .lock files
         |    - tool_results with errors/conflicts
         |    - result events (cost, duration, session_id)
         |
         v
  Extracted events per agent (max 100KB each)
         |
         v
  Claude Haiku prompt:
    "Here are the events, evaluate these 6 criteria..."
         |
         v
  JSON response: {"results": [{"criterion": ..., "pass": ...}, ...]}
         |
         v
  Parse JSON, print table, exit 0 (all pass) or 1 (any fail)
```

---

## Authentication Flow

`run.sh` supports three authentication methods, checked in priority order:

```
                    Resolve Auth
                        |
        +---------------+---------------+
        |               |               |
        v               v               v
  ANTHROPIC_API_KEY  CLAUDE_CODE_    CLAUDE_CONFIG_DIR
  env var set?       OAUTH_TOKEN     env var set?
        |            env var set?          |
       YES               |               YES
        |                YES               |
        v                 |                v
  Use API key            v           Extract from
  directly          Use OAuth        macOS Keychain
        |           token directly         |
        |                |                 |
        |                |          +------+------+
        |                |          |             |
        |                |          v             v
        |                |    Default path?   Custom path?
        |                |    ~/.claude       other
        |                |          |             |
        |                |          v             v
        |                |    Service name:   Service name:
        |                |    "Claude Code-   "Claude Code-
        |                |     credentials"    credentials-
        |                |          |           {sha256:8}"
        |                |          |             |
        |                |          +------+------+
        |                |                 |
        |                |                 v
        |                |          security find-generic-password
        |                |          -> JSON -> python3 -> accessToken
        |                |                 |
        +--------+-------+--------+--------+
                 |
                 v
          -e "AUTH_VAR=token" passed to docker run
```

---

## File Reference

| File | Role | Runs On | Model Used |
|---|---|---|---|
| `run.sh` | Init repo, build image, launch containers | Host | - |
| `stop.sh` | Stop and remove all agent containers | Host | - |
| `status.sh` | Show containers, commits, log tails | Host | - |
| `monitor.sh` | Periodic activity summaries | Host | Haiku 4.5 |
| `agent_loop.sh` | Clone, invoke Claude, repeat | Container | - |
| `Dockerfile` | Container image definition | Docker build | - |
| `AGENT_PROMPT.template.md` | Template for project instructions | - | - |
| `tests/run_test.sh` | E2E test orchestrator | Host | - |
| `tests/accept.sh` | Code quality evaluation | Host | Sonnet 4.5 |
| `tests/analyze_logs.sh` | Agent behavior evaluation | Host | Haiku 4.5 |

### Model Usage

```
+-------------------+---------------------+---------------------------+
|  Component        |  Model              |  Purpose                  |
+-------------------+---------------------+---------------------------+
|  Agent (Claude)   |  claude-opus-4-6    |  Write code, run tests,   |
|                   |                     |  coordinate via git        |
+-------------------+---------------------+---------------------------+
|  Monitor          |  claude-haiku-4.5   |  Summarize agent activity  |
+-------------------+---------------------+---------------------------+
|  Acceptance check |  claude-sonnet-4.5  |  Run code, evaluate spec   |
+-------------------+---------------------+---------------------------+
|  Behavior check   |  claude-haiku-4.5   |  Evaluate coordination     |
+-------------------+---------------------+---------------------------+
```

### Sample Test Configurations

```
+----------------+--------+-------+----------------------------------+
|  Sample        | Agents | Tasks | Complexity                       |
+----------------+--------+-------+----------------------------------+
|  hello-python  |   2    |   2   | Minimal: 1 function + tests      |
|  fizzbuzz      |   1    |   2   | Single agent: function + CLI     |
|  csv-stats     |   3    |   5   | Full: 5 tasks, 3 agents racing   |
+----------------+--------+-------+----------------------------------+
```

---

## End-to-End Example: csv-stats with 3 Agents

```
TIME  AGENT-1              AGENT-2              AGENT-3           UPSTREAM
 |
 |    clone                clone                clone
 |    read AGENT_PROMPT    read AGENT_PROMPT    read AGENT_PROMPT
 |
 |    claim load_csv       claim compute_stats  claim filter_rows
 |    push (ok) ---------> push (ok) ---------> push (ok) ------->
 |    verify (ok)          verify (ok)          verify (ok)
 |
 |    implement            implement            implement
 |    load_csv()           compute_stats()      filter_rows()
 |    run tests            run tests            run tests
 |
 |    pull --rebase        pull --rebase        pull --rebase
 |    push (ok) ---------> push (rejected!)     push (ok) ------->
 |                         pull --rebase
 |                         push (ok) ---------->
 |
 |    rm load_csv.lock     rm compute_stats     rm filter_rows
 |    push --------->       .lock               .lock
 |                         push --------->      push ------------>
 |
 |    claim cli            claim tests          (all tasks claimed)
 |    push (ok) ---------> push (ok) ---------> (done, exit)
 |
 |    implement cli        implement tests
 |    push --------->      push ---------->
 |
 |    rm cli.lock          rm tests.lock
 |    push --------->      push ---------->
 |
 |    (done, exit)         (done, exit)
 |
 v
```

After all agents exit, the test framework clones the repo and runs all three
evaluation layers. A passing test requires all acceptance criteria met, all
behavior criteria met, and the monitor working correctly.
