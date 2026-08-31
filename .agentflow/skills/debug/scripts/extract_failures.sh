#!/usr/bin/env bash
set -euo pipefail

# Language: bash — swap for a .py version if preferred

# extract_failures.sh
# Purpose: Extract and deduplicate failure snippets from test logs

LOG_FILE=""
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --log)
      LOG_FILE="$2"
      shift 2
      ;;
    --output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [[ -z "$LOG_FILE" ]]; then
  echo "Error: --log <path> is required."
  exit 1
fi

if [[ ! -f "$LOG_FILE" ]]; then
  echo "Warning: Log file '$LOG_FILE' not found or is not a file."
  exit 1
fi

# We extract lines containing key error signatures
# grep -E is used for extended regex
# We then take the last 50 lines to maintain a decent context window
# and deduplicate identical lines.

TMP_FILE=$(mktemp)

grep -E "FAILED|ERROR|AssertionError|Exception|Traceback" "$LOG_FILE" > "$TMP_FILE" || true

if [[ ! -s "$TMP_FILE" ]]; then
  echo "No failures found in log."
  rm "$TMP_FILE"
  exit 0
fi

if [[ -n "$OUTPUT_FILE" ]]; then
  tail -n 50 "$TMP_FILE" | sort | uniq > "$OUTPUT_FILE"
  echo "Wrote extracted failures to $OUTPUT_FILE"
else
  tail -n 50 "$TMP_FILE" | sort | uniq
fi

rm "$TMP_FILE"
exit 0
