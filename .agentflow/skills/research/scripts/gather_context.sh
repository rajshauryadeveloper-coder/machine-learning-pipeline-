#!/usr/bin/env bash
set -euo pipefail

# gather_context.sh
# Scans the local codebase for existing patterns, prior art, and related tests
# matching the given research topic.

# Default environment variables
AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.}"
BRANCH="${BRANCH:-main}"
OUTPUT_DIR="${OUTPUT_DIR:-worklogs/$BRANCH/scratch}"
MAX_RESULTS="${MAX_RESULTS:-20}"

if [ -z "${TOPIC:-}" ]; then
    echo "Error: TOPIC environment variable must be set."
    exit 1
fi

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%s)
OUTPUT_FILE="$OUTPUT_DIR/context-${TIMESTAMP}.txt"

echo "Gathering context for topic: $TOPIC" > "$OUTPUT_FILE"
echo "=========================================" >> "$OUTPUT_FILE"

# Step 1: Recent git commits related to the topic
echo "-> Checking git log for relevant commits..."
echo "[Recent Commits]" >> "$OUTPUT_FILE"
if git rev-parse --git-dir > /dev/null 2>&1; then
    git log --oneline -20 --grep="$TOPIC" -i >> "$OUTPUT_FILE" || echo "No commits found." >> "$OUTPUT_FILE"
else
    echo "Not a git repository, skipping git log." >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# Step 2: Codebase files mentioning the topic
echo "-> Searching codebase for topic mentions..."
echo "[Code Matches]" >> "$OUTPUT_FILE"
# grep through common source file types, limit to MAX_RESULTS
grep -r --include="*.py" --include="*.ts" --include="*.go" -l -i "$TOPIC" "$AGENTFLOW_ROOT" 2>/dev/null | head -n "$MAX_RESULTS" >> "$OUTPUT_FILE" || echo "No code matches found." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Step 3: Identify potential test files
echo "-> Identifying related test files..."
echo "[Test Files]" >> "$OUTPUT_FILE"
grep -r --include="*test*.py" --include="*test*.ts" --include="*test*.go" --include="*spec*.ts" -l -i "$TOPIC" "$AGENTFLOW_ROOT" 2>/dev/null | head -n "$MAX_RESULTS" >> "$OUTPUT_FILE" || echo "No test matches found." >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "Context gathering complete."
echo "Output saved to: $OUTPUT_FILE"
