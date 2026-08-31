#!/bin/bash
# Note: The language for this script is swappable (can be .sh or .py).
# script to scaffold documentation

set -e

# Require TOPIC_SLUG
if [ -z "$TOPIC_SLUG" ]; then
  echo "Error: TOPIC_SLUG environment variable is required."
  exit 1
fi

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.}"
TEMPLATE_PATH="${TEMPLATE_PATH:-$AGENTFLOW_ROOT/docs-generated/_TEMPLATE.md}"
DOC_DIR="$AGENTFLOW_ROOT/docs-generated/$TOPIC_SLUG"
DOC_PATH="$DOC_DIR/README.md"

# Create directory
mkdir -p "$DOC_DIR"

# Copy template if it exists, otherwise create empty file
if [ -f "$TEMPLATE_PATH" ]; then
  cp "$TEMPLATE_PATH" "$DOC_PATH"
else
  echo "# $TOPIC_SLUG" > "$DOC_PATH"
fi

# Inject timestamp into frontmatter (assuming it exists or creating one)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
if grep -q "^---" "$DOC_PATH"; then
  # Insert after first ---
  sed -i.bak "1,/^---/s/^---$/---\ncreated: $TIMESTAMP/" "$DOC_PATH"
  rm -f "${DOC_PATH}.bak"
else
  # Prepend frontmatter
  TEMP_FILE=$(mktemp)
  echo "---" > "$TEMP_FILE"
  echo "created: $TIMESTAMP" >> "$TEMP_FILE"
  echo "---" >> "$TEMP_FILE"
  echo "" >> "$TEMP_FILE"
  cat "$DOC_PATH" >> "$TEMP_FILE"
  mv "$TEMP_FILE" "$DOC_PATH"
fi

echo "Created document stub at: $DOC_PATH"
