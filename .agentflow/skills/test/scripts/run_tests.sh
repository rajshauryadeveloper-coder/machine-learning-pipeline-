#!/usr/bin/env bash
set -uo pipefail

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)}"
SLUG="$("$SCRIPT_DIR/../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo "$BRANCH")"
TEST_CMD="${TEST_CMD:-uv run pytest tests/ --cov=src}"
LOG_DIR="$AGENTFLOW_ROOT/worklogs/$SLUG/artifacts"
COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-60}"

echo "Preparing to run tests..."
echo "Branch: $BRANCH (slug: $SLUG)"

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/test_run_${TIMESTAMP}.log"
SUMMARY_FILE="${LOG_DIR}/test_run_summary_${TIMESTAMP}.md"

echo "Executing: $TEST_CMD"
echo "Logging to: $LOG_FILE"

eval "$TEST_CMD" 2>&1 | tee "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

{
  echo "---"
  echo "type: artifact"
  echo "status: $([ "$EXIT_CODE" -eq 0 ] && echo completed || echo failed)"
  echo "created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "---"
  echo ""
  echo "# Test Run Summary"
  echo ""
  echo "- **Branch:** $BRANCH"
  echo "- **Slug:** $SLUG"
  echo "- **Exit code:** $EXIT_CODE"
  echo "- **Log:** test_run_${TIMESTAMP}.log"
  echo ""
  if [[ "$EXIT_CODE" -eq 0 ]]; then
    echo "Review coverage output in the log. Flag any module below ${COVERAGE_THRESHOLD}% for integration test follow-up."
  fi
} > "$SUMMARY_FILE"

echo "Summary: $SUMMARY_FILE"
echo "Exit code: $EXIT_CODE"
exit $EXIT_CODE
