#!/bin/bash
# Note: The language for this script is swappable (can be .sh or .py).
# script to collect history of attempts for postmortem

set -e

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.}"
if [ -z "$BRANCH" ]; then
  echo "Error: BRANCH environment variable is required."
  exit 1
fi

TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
ATTEMPTS_DIR="$AGENTFLOW_ROOT/worklogs/$BRANCH/attempts"
ARTIFACTS_DIR="$AGENTFLOW_ROOT/worklogs/$BRANCH/artifacts"
OUTPUT_FILE="${OUTPUT_FILE:-$ARTIFACTS_DIR/history-digest-$TIMESTAMP.md}"

# Create artifacts dir if it doesn't exist
mkdir -p "$ARTIFACTS_DIR"

if [ ! -d "$ATTEMPTS_DIR" ]; then
  echo "No attempts directory found at $ATTEMPTS_DIR"
  echo "# History Digest for $BRANCH" > "$OUTPUT_FILE"
  echo "Total attempts: 0" >> "$OUTPUT_FILE"
  echo "Created output: $OUTPUT_FILE"
  exit 0
fi

# Count attempts
ATTEMPT_COUNT=$(ls -1 "$ATTEMPTS_DIR" | wc -l)
DATE_RANGE=$(date +"%Y-%m-%d")

# Create header
echo "# History Digest for $BRANCH" > "$OUTPUT_FILE"
echo "Total attempts: $ATTEMPT_COUNT" >> "$OUTPUT_FILE"
echo "Date range: $DATE_RANGE" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Concatenate files sorted by name
for file in $(ls -1 "$ATTEMPTS_DIR" | sort); do
  echo "## File: $file" >> "$OUTPUT_FILE"
  cat "$ATTEMPTS_DIR/$file" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "---" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
done

echo "Created output: $OUTPUT_FILE"
