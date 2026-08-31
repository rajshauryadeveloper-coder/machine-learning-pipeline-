#!/bin/bash
# Generate diff summary
# Note: The language for this script is swappable (.sh or .py)

set -e

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
SLUG="$("$SCRIPT_DIR/../../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo "$BRANCH")"
BASE_BRANCH="${BASE_BRANCH:-main}"
ARTIFACTS_DIR="${AGENTFLOW_ROOT}/worklogs/${SLUG}/artifacts"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
OUTPUT_FILE="${ARTIFACTS_DIR}/diff-summary-${TIMESTAMP}.md"

mkdir -p "$ARTIFACTS_DIR"

echo "Generating diff summary against origin/${BASE_BRANCH}..."

cat << 'EOF' > "$OUTPUT_FILE"
---
type: diff-summary
status: generated
---

# Diff Summary

## Commit Log
```
EOF

git log --oneline "origin/${BASE_BRANCH}..HEAD" >> "$OUTPUT_FILE" || true

cat << 'EOF' >> "$OUTPUT_FILE"
```

## Diff Stat
```
EOF

git diff --stat "origin/${BASE_BRANCH}..HEAD" >> "$OUTPUT_FILE" || true

cat << 'EOF' >> "$OUTPUT_FILE"
```
EOF

echo "Diff summary generated at: $OUTPUT_FILE"
exit 0
