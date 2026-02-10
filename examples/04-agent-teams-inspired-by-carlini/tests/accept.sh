#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 <bare-repo-path> <accept-spec-path>

Clones the bare repo, runs Claude to evaluate it against the acceptance spec.
Prints PASS/FAIL table. Exits 0 if all pass, 1 otherwise.
EOF
    exit 0
}

[[ $# -lt 2 ]] && usage

BARE_REPO="$1"
ACCEPT_SPEC="$2"

if [[ ! -d "$BARE_REPO" ]]; then
    echo "Error: bare repo not found at $BARE_REPO"
    exit 1
fi

if [[ ! -f "$ACCEPT_SPEC" ]]; then
    echo "Error: accept spec not found at $ACCEPT_SPEC"
    exit 1
fi

# Clone to temp dir
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

git clone "$BARE_REPO" "$TMPDIR/repo"
cd "$TMPDIR/repo"


SPEC_CONTENT=$(cat "$ACCEPT_SPEC")

PROMPT="You are evaluating a project against an acceptance specification.

IMPORTANT: Before running any tests, install pytest if needed: pip3 install --break-system-packages pytest 2>/dev/null || pip install pytest 2>/dev/null

## Acceptance Specification
${SPEC_CONTENT}

## Instructions
1. Examine the project files in the current directory.
2. Run all checks described in the spec (run Python scripts, tests, etc.).
3. Output ONLY a JSON object in this exact format, with no other text:

\`\`\`json
{\"results\": [{\"criterion\": \"description\", \"pass\": true, \"detail\": \"explanation\"}, ...]}
\`\`\`

Evaluate every criterion in the spec. Be strict — only mark pass:true if the criterion is fully met."

RESULT_FILE="$TMPDIR/result.json"

claude --dangerously-skip-permissions \
    -p "$PROMPT" \
    --model "${CLAUDE_MODEL:-claude-sonnet-4-5-20250929}" \
    --output-format text \
    2>&1 | tee "$TMPDIR/claude_output.txt" || true

# Extract JSON from Claude's output (find the JSON block)
CLAUDE_OUTPUT=$(cat "$TMPDIR/claude_output.txt")

# Try to extract JSON from markdown code block or raw JSON
if echo "$CLAUDE_OUTPUT" | python3 -c "
import sys, json, re

text = sys.stdin.read()

# Try to find JSON in code block
m = re.search(r'\`\`\`(?:json)?\s*(\{.*?\})\s*\`\`\`', text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
else:
    # Try to find raw JSON object
    m = re.search(r'(\{\"results\".*\})', text, re.DOTALL)
    if m:
        data = json.loads(m.group(1))
    else:
        print('ERROR: No JSON found in Claude output', file=sys.stderr)
        sys.exit(1)

json.dump(data, open('$RESULT_FILE', 'w'), indent=2)

# Print results table
all_pass = True
print()
print(f'{\"STATUS\":<8} {\"CRITERION\":<50} DETAIL')
print('-' * 90)
for r in data['results']:
    status = 'PASS' if r['pass'] else 'FAIL'
    if not r['pass']:
        all_pass = False
    criterion = r['criterion'][:48]
    detail = r.get('detail', '')[:40]
    print(f'{status:<8} {criterion:<50} {detail}')
print('-' * 90)
if all_pass:
    print('ALL CHECKS PASSED')
    sys.exit(0)
else:
    print('SOME CHECKS FAILED')
    sys.exit(1)
"; then
    exit 0
else
    echo "Failed to parse acceptance results"
    echo "Raw Claude output:"
    echo "$CLAUDE_OUTPUT"
    exit 1
fi
