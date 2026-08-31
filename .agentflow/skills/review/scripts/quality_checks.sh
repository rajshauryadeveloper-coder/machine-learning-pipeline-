#!/bin/bash
# Quality Checks
# Note: The language for this script is swappable (.sh or .py)

set -e

LINT_CMD="${LINT_CMD:-ruff check .}"
TYPE_CMD="${TYPE_CMD:-mypy .}"
AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.}"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
ARTIFACTS_DIR="${AGENTFLOW_ROOT}/worklogs/${BRANCH}/artifacts"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
OUTPUT_FILE="${ARTIFACTS_DIR}/quality-${TIMESTAMP}.md"

mkdir -p "$ARTIFACTS_DIR"

echo "Running Quality Checks..."
ERRORS=0

echo "Running lint check: $LINT_CMD"
if ! $LINT_CMD > /tmp/lint_out 2>&1; then
    echo "Lint check failed."
    ERRORS=1
    echo -e "## Lint Errors\n\n\`\`\`\n$(cat /tmp/lint_out)\n\`\`\`\n" >> "$OUTPUT_FILE"
fi

if [ -n "$TYPE_CMD" ]; then
    echo "Running type check: $TYPE_CMD"
    if command -v $(echo "$TYPE_CMD" | awk '{print $1}') >/dev/null 2>&1; then
        if ! $TYPE_CMD > /tmp/type_out 2>&1; then
            echo "Type check failed."
            ERRORS=1
            echo -e "## Type Check Errors\n\n\`\`\`\n$(cat /tmp/type_out)\n\`\`\`\n" >> "$OUTPUT_FILE"
        fi
    else
        echo "WARNING: Type checker command not found. Skipping type check."
    fi
fi

if [ "$ERRORS" -ne 0 ]; then
    echo "Quality checks failed! Results saved to: $OUTPUT_FILE"
    # Prepend frontmatter
    sed -i.bak '1i\
---\
type: quality-report\
status: failed\
---\
' "$OUTPUT_FILE"
    rm -f "${OUTPUT_FILE}.bak"
    exit 1
fi

echo "Quality checks passed successfully."
exit 0
