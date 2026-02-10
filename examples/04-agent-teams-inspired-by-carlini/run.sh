#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IMAGE_NAME="cc-agent"
CONTAINER_PREFIX="cc-agent"
NUM_AGENTS=2
PROJECT_DIR=""
MAX_ITERATIONS=0
CLAUDE_MODEL="claude-opus-4-6"

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --agents N          Number of parallel agents (default: 2)
  --project-dir PATH  Path to project directory (must contain AGENT_PROMPT.md)
  --max-iterations N  Max iterations per agent, 0=unlimited (default: 0)
  --model MODEL       Claude model to use (default: claude-opus-4-6)
  -h, --help          Show this help
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agents) NUM_AGENTS="$2"; shift 2 ;;
        --project-dir) PROJECT_DIR="$2"; shift 2 ;;
        --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        --model) CLAUDE_MODEL="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

if [[ -z "$PROJECT_DIR" ]]; then
    echo "Error: --project-dir is required"
    usage
fi

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

if [[ ! -f "$PROJECT_DIR/AGENT_PROMPT.md" ]]; then
    echo "Error: $PROJECT_DIR/AGENT_PROMPT.md not found"
    exit 1
fi

# Resolve authentication: ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, or CLAUDE_CONFIG_DIR
AUTH_ENV_ARGS=()

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    AUTH_ENV_ARGS+=(-e "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY")
    echo "Auth: using ANTHROPIC_API_KEY"
elif [[ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
    AUTH_ENV_ARGS+=(-e "CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN")
    echo "Auth: using CLAUDE_CODE_OAUTH_TOKEN"
elif [[ -n "${CLAUDE_CONFIG_DIR:-}" ]]; then
    echo "Auth: extracting OAuth token from macOS Keychain for CLAUDE_CONFIG_DIR=$CLAUDE_CONFIG_DIR"
    if [[ "$CLAUDE_CONFIG_DIR" = "$HOME/.claude" ]]; then
        KEYCHAIN_SERVICE="Claude Code-credentials"
    else
        KEYCHAIN_SUFFIX=$(echo -n "$CLAUDE_CONFIG_DIR" | shasum -a 256 | head -c 8)
        KEYCHAIN_SERVICE="Claude Code-credentials-${KEYCHAIN_SUFFIX}"
    fi
    CREDS_JSON=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null) || {
        echo "Error: Could not find Keychain entry '$KEYCHAIN_SERVICE'"
        echo "Make sure you've logged in with Claude Code using this config directory."
        exit 1
    }
    CLAUDE_CODE_OAUTH_TOKEN=$(echo "$CREDS_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['claudeAiOauth']['accessToken'])")
    if [[ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]]; then
        echo "Error: Failed to extract accessToken from Keychain entry"
        exit 1
    fi
    AUTH_ENV_ARGS+=(-e "CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_CODE_OAUTH_TOKEN")
    echo "Auth: extracted OAuth token from Keychain (${CLAUDE_CODE_OAUTH_TOKEN:0:20}...)"
else
    echo "Error: Set one of ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, or CLAUDE_CONFIG_DIR"
    exit 1
fi

UPSTREAM="${SCRIPT_DIR}/upstream.git"

# Initialize bare repo from project if needed
if [[ ! -d "$UPSTREAM" ]]; then
    echo "Initializing bare repo from project..."
    TMPDIR=$(mktemp -d)
    git init "$TMPDIR"
    cp -r "$PROJECT_DIR"/. "$TMPDIR"/
    # Inject .gitignore to prevent binary/generated files from being committed
    if ! grep -q '__pycache__' "$TMPDIR/.gitignore" 2>/dev/null; then
        cat >> "$TMPDIR/.gitignore" <<'GITIGNORE'

# Python
__pycache__/
*.py[cod]
*.pyo
*.so
*.egg-info/
dist/
build/
.pytest_cache/

# Virtual environments
.venv/
venv/

# pixi
.pixi/

# Node
node_modules/

# OS
.DS_Store
GITIGNORE
    fi
    cd "$TMPDIR"
    git add -A
    git commit -m "Initial project import"
    cd "$SCRIPT_DIR"
    git clone --bare "$TMPDIR" "$UPSTREAM"
    rm -rf "$TMPDIR"
    echo "Bare repo created at $UPSTREAM"
else
    echo "Using existing bare repo at $UPSTREAM"
fi

# Create agent_logs dir and fix permissions for non-root container user
mkdir -p "$UPSTREAM/agent_logs"
chmod -R a+rwX "$UPSTREAM"

# Build Docker image
echo "Building Docker image..."
docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"

# Stop any existing agent containers
echo "Stopping any existing agent containers..."
for i in $(seq 1 20); do
    docker rm -f "${CONTAINER_PREFIX}-${i}" 2>/dev/null || true
done

# Launch agents
echo "Launching $NUM_AGENTS agents..."
for i in $(seq 1 "$NUM_AGENTS"); do
    CONTAINER_NAME="${CONTAINER_PREFIX}-${i}"
    echo "  Starting $CONTAINER_NAME..."
    docker run -d \
        --name "$CONTAINER_NAME" \
        -e AGENT_ID="$i" \
        "${AUTH_ENV_ARGS[@]}" \
        -e MAX_ITERATIONS="$MAX_ITERATIONS" \
        -e CLAUDE_MODEL="$CLAUDE_MODEL" \
        -v "$UPSTREAM:/upstream" \
        "$IMAGE_NAME"
done

echo ""
echo "=== $NUM_AGENTS agents running ==="
echo "Bare repo: $UPSTREAM"
echo ""
docker ps --filter "name=${CONTAINER_PREFIX}-" --format "table {{.Names}}\t{{.Status}}\t{{.ID}}"
echo ""
echo "========================================================================"
echo "  MONITOR:  $SCRIPT_DIR/monitor.sh --upstream $UPSTREAM"
echo "  STOP:     ./stop.sh"
echo "  CLONE:    git clone $UPSTREAM ./checkout"
echo "========================================================================"
