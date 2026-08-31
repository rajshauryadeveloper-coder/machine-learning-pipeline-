#!/bin/bash
# Note: The language for this script is swappable (can be .sh or .py).
set -e

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)}"
SLUG="$("$SCRIPT_DIR/../../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo "$BRANCH")"
ATTEMPTS_DIR="$AGENTFLOW_ROOT/worklogs/$SLUG/attempts"
ARTIFACTS_DIR="$AGENTFLOW_ROOT/worklogs/$SLUG/artifacts"
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
OUTPUT_FILE="${OUTPUT_FILE:-$ARTIFACTS_DIR/history-digest-$TIMESTAMP.md}"

mkdir -p "$ARTIFACTS_DIR"

if [ ! -d "$ATTEMPTS_DIR" ]; then
  echo "No attempts directory found at $ATTEMPTS_DIR"
  {
    echo "# History Digest for $BRANCH (slug: $SLUG)"
    echo "Total attempts: 0"
  } > "$OUTPUT_FILE"
  echo "Created output: $OUTPUT_FILE"
  exit 0
fi

ATTEMPT_COUNT=$(find "$ATTEMPTS_DIR" -maxdepth 1 -type f | wc -l | tr -d ' ')
DATE_RANGE=$(date +"%Y-%m-%d")

{
  echo "# History Digest for $BRANCH (slug: $SLUG)"
  echo "Total attempts: $ATTEMPT_COUNT"
  echo "Date range: $DATE_RANGE"
  echo ""
  echo "---"
  echo ""
} > "$OUTPUT_FILE"

for file in $(find "$ATTEMPTS_DIR" -maxdepth 1 -type f | sort); do
  basename_file=$(basename "$file")
  echo "## File: $basename_file" >> "$OUTPUT_FILE"
  cat "$file" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
done

echo "Created output: $OUTPUT_FILE"
