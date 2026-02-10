#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 <bare-repo-path>

Analyzes agent logs from the bare repo's agent_logs/ directory.
Calls Haiku to evaluate agent behavior against coordination criteria.
Prints PASS/FAIL table. Exits 0 if all pass, 1 otherwise.
EOF
    exit 0
}

[[ $# -lt 1 ]] && usage

BARE_REPO="$1"

if [[ ! -d "$BARE_REPO" ]]; then
    echo "Error: bare repo not found at $BARE_REPO"
    exit 1
fi

LOG_DIR="$BARE_REPO/agent_logs"

if [[ ! -d "$LOG_DIR" ]]; then
    echo "Error: agent_logs/ not found in $BARE_REPO"
    echo ""
    echo "STATUS   CRITERION                                          DETAIL"
    echo "------------------------------------------------------------------------------------------"
    echo "FAIL     Agent logs present                                  No agent_logs/ directory found"
    echo "------------------------------------------------------------------------------------------"
    echo "SOME CHECKS FAILED"
    exit 1
fi

LOG_FILES=("$LOG_DIR"/*.log)
if [[ ! -f "${LOG_FILES[0]}" ]]; then
    echo "Error: no .log files found in $LOG_DIR"
    echo ""
    echo "STATUS   CRITERION                                          DETAIL"
    echo "------------------------------------------------------------------------------------------"
    echo "FAIL     Agent logs present                                  No .log files found"
    echo "------------------------------------------------------------------------------------------"
    echo "SOME CHECKS FAILED"
    exit 1
fi

echo "Found ${#LOG_FILES[@]} log file(s) in $LOG_DIR"

# Preprocess logs: extract coordination-relevant events
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

EXTRACTED="$TMPDIR/extracted.txt"

python3 - "$LOG_DIR" "$EXTRACTED" <<'PYEOF'
import sys, os, json, re

log_dir = sys.argv[1]
out_path = sys.argv[2]

MAX_PER_AGENT = 100 * 1024  # 100KB per agent max

# Patterns that indicate coordination-relevant events
GIT_COMMANDS = re.compile(r'git\s+(push|pull|rebase|commit|merge|clone|fetch|add)', re.IGNORECASE)
TASK_LOCK_OPS = re.compile(r'current_tasks/.*\.lock', re.IGNORECASE)
ERROR_PATTERNS = re.compile(r'(error|fatal|CONFLICT|rejected|non-fast-forward|failed to push)', re.IGNORECASE)

def extract_from_event(event):
    """Extract coordination-relevant items from a stream-json event.

    Stream-json format nests tool calls inside assistant/user messages:
      {"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{...}}]}}
      {"type":"user","tool_use_result":{"stdout":"...","stderr":"..."}}
      {"type":"result","total_cost_usd":...,"duration_ms":...}
    """
    etype = event.get("type", "")
    results = []

    if etype == "assistant":
        for block in event.get("message", {}).get("content", []):
            if block.get("type") != "tool_use":
                continue
            tool_name = block.get("name", "")
            inp = block.get("input", {})
            if tool_name == "Bash":
                cmd = inp.get("command", "")
                if GIT_COMMANDS.search(cmd) or TASK_LOCK_OPS.search(cmd):
                    results.append({"type": "tool_use", "tool": tool_name, "command": cmd[:500]})
            elif tool_name in ("Write", "Edit"):
                path = inp.get("file_path", "")
                if TASK_LOCK_OPS.search(path):
                    results.append({"type": "tool_use", "tool": tool_name, "file_path": path})

    elif etype == "user":
        # tool_use_result has stdout/stderr directly
        tr = event.get("tool_use_result")
        if isinstance(tr, dict):
            combined = str(tr.get("stdout", "")) + " " + str(tr.get("stderr", ""))
            if ERROR_PATTERNS.search(combined) or GIT_COMMANDS.search(combined) or TASK_LOCK_OPS.search(combined):
                results.append({"type": "tool_result", "output": combined[:500]})

    elif etype == "result":
        results.append({
            "type": "result",
            "cost": event.get("total_cost_usd"),
            "duration": event.get("duration_ms"),
            "session_id": event.get("session_id"),
        })

    return results

# Process each log file
agents = {}
for fname in sorted(os.listdir(log_dir)):
    if not fname.endswith(".log"):
        continue

    # Extract agent ID from filename (agent_1_iter1_*.log)
    parts = fname.split("_")
    agent_id = parts[1] if len(parts) > 1 else "unknown"
    agent_key = f"agent-{agent_id}"

    if agent_key not in agents:
        agents[agent_key] = []

    fpath = os.path.join(log_dir, fname)
    try:
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Try parsing as JSON (stream-json NDJSON)
                try:
                    event = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    # Non-JSON line (bash log() output) — check for errors
                    if ERROR_PATTERNS.search(line):
                        agents[agent_key].append({"type": "log", "text": line[:300]})
                    continue

                for item in extract_from_event(event):
                    agents[agent_key].append(item)
    except Exception as e:
        agents[agent_key].append({"type": "error", "text": f"Failed to read {fname}: {e}"})

# Truncate per-agent if too large
output_parts = []
for agent_key in sorted(agents.keys()):
    events = agents[agent_key]
    agent_json = json.dumps(events, indent=1)
    if len(agent_json) > MAX_PER_AGENT:
        # Keep most recent events
        while len(json.dumps(events, indent=1)) > MAX_PER_AGENT and len(events) > 10:
            events.pop(0)
        agent_json = json.dumps(events, indent=1)
    output_parts.append(f"### {agent_key}\n{agent_json}")

with open(out_path, "w") as f:
    f.write("\n\n".join(output_parts))

print(f"Extracted {sum(len(v) for v in agents.values())} events from {len(agents)} agent(s)")
PYEOF

EXTRACTED_CONTENT=$(cat "$EXTRACTED")

if [[ -z "$EXTRACTED_CONTENT" ]]; then
    echo "Warning: no coordination events extracted from logs"
    EXTRACTED_CONTENT="(No coordination events found in agent logs — agents may not have performed any git or task operations)"
fi

# Build the Haiku prompt
PROMPT="You are analyzing agent behavior logs from a multi-agent coding system.

## Agent Log Summaries
Each section below shows coordination-relevant events extracted from an agent's session log (git operations, task lock operations, errors).

${EXTRACTED_CONTENT}

## Behavioral Criteria

Evaluate each criterion below. For each, output pass:true only if fully met. Base your evaluation on evidence from the logs above. Cite specific agent IDs and events.

### 1. Push Success
- **Pass**: Every agent pushed at least one commit successfully (look for git push commands with successful output, no error in the following tool_result).
- **Fail**: An agent finished with zero successful pushes.

### 2. Conflict Resolution
- **Pass**: No merge conflicts occurred, OR conflicts were resolved and changes were subsequently pushed.
- **Fail**: A merge conflict was left unresolved, or an agent gave up after a conflict.

### 3. No Duplicate Work
- **Pass**: Each task was claimed by only one agent (each .lock file was created by a single agent).
- **Fail**: Two agents claimed or implemented the same task.

### 4. Task Protocol Compliance
- **Pass**: Agents created .lock files before working, pushed their claims, and removed .lock files when done.
- **Fail**: An agent skipped the locking protocol or left stale .lock files.

### 5. No Crashes or Errors
- **Pass**: No unrecovered fatal errors. Agents completed their sessions normally.
- **Fail**: An agent had an unrecoverable error or abnormal termination (not including transient push failures that were retried).

### 6. Git Workflow Correctness
- **Pass**: Agents pulled before pushing, rebased on rejection, and retried pushes.
- **Fail**: An agent pushed without pulling first, or didn't handle push rejections correctly.

## Single-Agent Note
If there is only one agent, criteria 2 (Conflict Resolution) and 3 (No Duplicate Work) should pass by default since there's no concurrency.

## Output
Output ONLY a JSON object in this exact format, with no other text:

\`\`\`json
{\"results\": [{\"criterion\": \"Push Success\", \"pass\": true, \"detail\": \"explanation with evidence\"}, ...]}
\`\`\`

Include all 6 criteria. Be strict but fair — transient failures that were retried successfully should not cause a fail."

RESULT_FILE="$TMPDIR/result.json"

claude --dangerously-skip-permissions \
    -p "$PROMPT" \
    --model "${CLAUDE_MODEL:-claude-haiku-4-5-20251001}" \
    --output-format text \
    2>&1 | tee "$TMPDIR/claude_output.txt" || true

# Extract JSON from Claude's output and print results table
set +e
python3 - "$TMPDIR/claude_output.txt" "$RESULT_FILE" <<'PARSE_EOF'
import sys, json

text = open(sys.argv[1]).read()
result_file = sys.argv[2]

# Find "results" key and scan back for the opening brace
decoder = json.JSONDecoder()
rpos = text.find('"results"')
if rpos < 0:
    print("ERROR: No JSON found in Claude output", file=sys.stderr)
    sys.exit(2)
# Find the '{' before "results" (skip whitespace / code fences)
brace = text.rfind('{', 0, rpos)
if brace < 0:
    print("ERROR: No opening brace found before 'results'", file=sys.stderr)
    sys.exit(2)
data, _ = decoder.raw_decode(text, brace)
json.dump(data, open(result_file, "w"), indent=2)

# Print results table
all_pass = True
print()
print(f'{"STATUS":<8} {"CRITERION":<50} DETAIL')
print("-" * 90)
for r in data["results"]:
    status = "PASS" if r["pass"] else "FAIL"
    if not r["pass"]:
        all_pass = False
    print(f'{status:<8} {r["criterion"][:48]:<50} {r.get("detail","")[:40]}')
print("-" * 90)
if all_pass:
    print("ALL CHECKS PASSED")
    sys.exit(0)
else:
    print("SOME CHECKS FAILED")
    sys.exit(1)
PARSE_EOF
PARSE_EXIT=$?
set -e
if [[ $PARSE_EXIT -eq 2 ]]; then
    echo "Failed to parse log analysis results"
    echo "Raw Claude output:"
    cat "$TMPDIR/claude_output.txt"
    exit 1
fi
exit $PARSE_EXIT
