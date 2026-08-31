#!/bin/bash
# Pre-Check for Review Skill
# Note: The language for this script is swappable (.sh or .py)

set -e

# Default variables
AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
SLUG="$("$SCRIPT_DIR/../../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo "$BRANCH")"
WORKLOG_DIR="${AGENTFLOW_ROOT}/worklogs/${SLUG}"
LATEST_ATTEMPT_FILE=$(ls -1t "${WORKLOG_DIR}/attempts/"*.md 2>/dev/null | head -n 1 || true)

echo "Running Pre-Check for branch: ${BRANCH}"

if [ -z "$LATEST_ATTEMPT_FILE" ] || [ ! -f "$LATEST_ATTEMPT_FILE" ]; then
    echo "ERROR: No attempt logs found in ${WORKLOG_DIR}/attempts/"
    exit 1
fi

if ! grep -q "stage: test" "$LATEST_ATTEMPT_FILE"; then
    echo "ERROR: Latest attempt is not a test stage."
    exit 1
fi

if ! grep -q "status: passed" "$LATEST_ATTEMPT_FILE"; then
    echo "ERROR: Latest test attempt did not pass."
    exit 1
fi

# Check if diff is not empty
# Assume base branch is origin/main if not specified
BASE_BRANCH="${BASE_BRANCH:-origin/main}"
FILES_CHANGED=$(git diff --name-only "$BASE_BRANCH"..."$BRANCH" | wc -l | awk '{print $1}')

if [ "$FILES_CHANGED" -eq 0 ]; then
    echo "ERROR: No files changed relative to ${BASE_BRANCH}."
    exit 1
fi

echo "Pre-check passed."
echo "Branch: ${BRANCH}"
echo "Files changed: ${FILES_CHANGED}"
exit 0
