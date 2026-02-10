#!/usr/bin/env bash
set -euo pipefail

TMPFILE=$(mktemp /tmp/pytest-results-XXXXXXXX)

python -m pytest tests/ -v > "$TMPFILE" 2>&1 || true

if grep -q "failed" "$TMPFILE"; then
    echo "Tests failed. Full results: $TMPFILE" >&2
    echo "" >&2
    grep -A 100 "FAILURES" "$TMPFILE" >&2
    exit 2
fi

rm -f "$TMPFILE"
exit 0
