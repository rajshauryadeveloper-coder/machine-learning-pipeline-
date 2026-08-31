#!/usr/bin/env bash
set -euo pipefail

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: Not a git repository. Run git init first."
    exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
if [[ "$BRANCH" == "HEAD" ]]; then
    echo "ERROR: No commits yet. Create an initial commit before starting a plan."
    exit 1
fi

SLUG="$("$SCRIPT_DIR/../../../scripts/worklog_path.sh" "$BRANCH")"
WORKLOG_DIR="$AGENTFLOW_ROOT/worklogs/$SLUG"

echo "Running Pre-Check for plan skill..."
echo "Branch: $BRANCH"
echo "Worklog slug: $SLUG"

if [[ -f "$WORKLOG_DIR/SUMMARY.md" ]]; then
    echo "Worklog already exists at $WORKLOG_DIR/SUMMARY.md"
else
    echo "WARNING: No worklog found. Run new_worklog.sh before planning."
fi

echo "Pre-check passed."
