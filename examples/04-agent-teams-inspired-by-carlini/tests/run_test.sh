#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HARNESS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SAMPLE_NAME=""
NUM_AGENTS=2

usage() {
    cat <<EOF
Usage: $0 <sample-name> [OPTIONS]

Arguments:
  sample-name          Name of sample under tests/samples/ (e.g. hello-python)

Options:
  --agents N           Number of parallel agents (default: 2)
  -h, --help           Show this help
EOF
    exit 0
}

[[ $# -eq 0 ]] && usage

SAMPLE_NAME="$1"; shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agents) NUM_AGENTS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

SAMPLE_DIR="$SCRIPT_DIR/samples/$SAMPLE_NAME"

if [[ ! -d "$SAMPLE_DIR/project" ]]; then
    echo "Error: sample not found at $SAMPLE_DIR/project"
    exit 1
fi

if [[ ! -f "$SAMPLE_DIR/ACCEPT_SPEC.md" ]]; then
    echo "Error: ACCEPT_SPEC.md not found at $SAMPLE_DIR/"
    exit 1
fi

# Create temp working directory
TMPDIR=$(mktemp -d)

cleanup() {
    echo ""
    echo "Cleaning up..."
    # Kill monitor if running
    if [[ -n "${MONITOR_PID:-}" ]]; then
        kill "$MONITOR_PID" 2>/dev/null || true
    fi
    # Stop agent containers
    for i in $(seq 1 "$NUM_AGENTS"); do
        docker rm -f "cc-agent-${i}" 2>/dev/null || true
    done
    rm -rf "$TMPDIR"
}
trap cleanup EXIT

echo "=== Running test: $SAMPLE_NAME with $NUM_AGENTS agent(s) ==="
echo "Temp dir: $TMPDIR"

# Copy harness files
cp "$HARNESS_DIR/Dockerfile" "$TMPDIR/"
cp "$HARNESS_DIR/agent_loop.sh" "$TMPDIR/"
cp "$HARNESS_DIR/run.sh" "$TMPDIR/"
cp "$HARNESS_DIR/stop.sh" "$TMPDIR/"
cp "$HARNESS_DIR/status.sh" "$TMPDIR/"
cp "$HARNESS_DIR/monitor.sh" "$TMPDIR/"

# Copy sample project
cp -r "$SAMPLE_DIR/project" "$TMPDIR/project"

cd "$TMPDIR"

# Run the harness
echo "Starting harness..."
./run.sh --agents "$NUM_AGENTS" --project-dir ./project --max-iterations 1

# Start monitor in background
MONITOR_LOG="$TMPDIR/monitor_output.txt"
"$HARNESS_DIR/monitor.sh" \
    --upstream "$TMPDIR/upstream.git" \
    --interval 15 \
    --max-updates 3 \
    > "$MONITOR_LOG" 2>&1 &
MONITOR_PID=$!

echo ""
echo "Waiting for agents to complete (monitor reads from $TMPDIR/upstream.git/agent_logs/)..."

# Wait for all agent containers to exit
for i in $(seq 1 "$NUM_AGENTS"); do
    docker wait "cc-agent-${i}" 2>/dev/null || true
done

echo "All agents finished."

# Give monitor time to process final state, then stop it
sleep 5
kill "$MONITOR_PID" 2>/dev/null || true
wait "$MONITOR_PID" 2>/dev/null || true

# Run acceptance checks (code quality)
echo ""
echo "=== Running acceptance checks ==="
ACCEPT_EXIT=0
"$SCRIPT_DIR/accept.sh" "$TMPDIR/upstream.git" "$SAMPLE_DIR/ACCEPT_SPEC.md" || ACCEPT_EXIT=$?

# Run agent log analysis (agent behavior)
echo ""
echo "=== Running agent behavior analysis ==="
ANALYZE_EXIT=0
"$SCRIPT_DIR/analyze_logs.sh" "$TMPDIR/upstream.git" || ANALYZE_EXIT=$?

# Check monitor behavior
echo ""
echo "=== Checking monitor behavior ==="
MONITOR_EXIT=0

# Check: monitor produced at least one update
if grep -q "Monitor Update" "$MONITOR_LOG" 2>/dev/null; then
    echo "PASS     Monitor produced updates"
else
    echo "FAIL     Monitor produced no updates"
    MONITOR_EXIT=1
fi

# Check: Haiku calls didn't all fail
if grep -q "(Haiku summarization failed)" "$MONITOR_LOG" 2>/dev/null; then
    echo "FAIL     Monitor Haiku summarization failed"
    MONITOR_EXIT=1
else
    echo "PASS     Monitor Haiku calls succeeded"
fi

# Check: monitor picked up commits (first run always shows them)
if grep -q "New Commits\|no new activity" "$MONITOR_LOG" 2>/dev/null; then
    echo "PASS     Monitor detected repo activity"
else
    echo "FAIL     Monitor didn't detect any repo activity"
    MONITOR_EXIT=1
fi

# Check: no bash errors/crashes in monitor output
if grep -q ": unbound variable$\|: command not found$\|: syntax error" "$MONITOR_LOG" 2>/dev/null; then
    echo "FAIL     Monitor had script errors"
    MONITOR_EXIT=1
else
    echo "PASS     Monitor ran without script errors"
fi

# All must pass
if [[ $ACCEPT_EXIT -eq 0 && $ANALYZE_EXIT -eq 0 && $MONITOR_EXIT -eq 0 ]]; then
    echo ""
    echo "=== TEST PASSED: $SAMPLE_NAME ==="
    exit 0
else
    echo ""
    echo "=== TEST FAILED: $SAMPLE_NAME ==="
    exit 1
fi
