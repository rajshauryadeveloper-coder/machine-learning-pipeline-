#!/usr/bin/env bash
# Language: bash (swap for .py version if preferred)
set -euo pipefail

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SLUG="$("$SCRIPT_DIR/../../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo "$BRANCH")"
WORKLOG_DIR="${WORKLOG_DIR:-$AGENTFLOW_ROOT/worklogs/$SLUG}"
STAGE="${STAGE:-implement}"

# Determine Attempt Number
ATTEMPT_DIR="$WORKLOG_DIR/attempts"
mkdir -p "$ATTEMPT_DIR"

# Count existing files starting with the stage name to auto-detect attempt number
COUNT=$(find "$ATTEMPT_DIR" -maxdepth 1 -name "${STAGE}_attempt_*.md" 2>/dev/null | wc -l | tr -d ' ')
ATTEMPT_NUM=$((COUNT + 1))

# Generate UTC timestamp
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")

ATTEMPT_FILE="$ATTEMPT_DIR/${STAGE}_attempt_${ATTEMPT_NUM}_${TIMESTAMP}.md"

# Generate File Content
FILES_CHANGED=$(git diff HEAD --name-only || echo "No tracked files changed")

cat <<EOF > "$ATTEMPT_FILE"
---
type: attempt
stage: $STAGE
attempt: $ATTEMPT_NUM
status: complete
timestamp: $TIMESTAMP
---

## Summary
Completed implementation stage attempt $ATTEMPT_NUM.

## Files Changed
\`\`\`
$FILES_CHANGED
\`\`\`

## Next Stage
test
EOF

# Update SUMMARY.md's ## Current stage line
SUMMARY_FILE="$WORKLOG_DIR/SUMMARY.md"
if [[ -f "$SUMMARY_FILE" ]]; then
    # Create a temporary file to hold the updated content
    TMP_SUMMARY=$(mktemp)
    awk -v stage="$STAGE" '/^## Current stage/{print "## Current stage: " stage; next} {print}' "$SUMMARY_FILE" > "$TMP_SUMMARY"
    mv "$TMP_SUMMARY" "$SUMMARY_FILE"
fi

# Output success
echo "Attempt recorded successfully: $ATTEMPT_FILE"
