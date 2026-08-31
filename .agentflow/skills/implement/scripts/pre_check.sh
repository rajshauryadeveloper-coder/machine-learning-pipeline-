#!/usr/bin/env bash
# Language: bash (swap for .py version if preferred)
set -euo pipefail

# Define environment variables with defaults
AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
WORKLOG_DIR="${WORKLOG_DIR:-$AGENTFLOW_ROOT/worklogs/$BRANCH}"

echo "Running Pre-Check for implement skill..."

# Check 1: Refuse to run on main/master branches
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
    echo "ERROR: Refusing to run on $BRANCH branch. Please create a feature branch."
    exit 1
fi

# Check 2: Detect uncommitted changes NOT created by this agent
if git status --porcelain | grep -q "^??"; then
    echo "WARNING: Uncommitted files detected. Proceed with caution to avoid losing manual work."
elif git status --porcelain | grep -q "^ M"; then
    echo "WARNING: Unstaged changes detected. Ensure these are intended."
fi

# Check 3: Verify the worklog SUMMARY.md exists
if [[ ! -f "$WORKLOG_DIR/SUMMARY.md" ]]; then
    echo "ERROR: Worklog SUMMARY.md missing at $WORKLOG_DIR/SUMMARY.md"
    echo "Hint: Run new-worklog to initialize the tracking structure for this branch."
    exit 1
fi

# Check 4: Verify plan file exists
PLAN_DIR="$AGENTFLOW_ROOT/plans"
if [[ -d "$PLAN_DIR" ]]; then
    if [[ -z "$(ls -A "$PLAN_DIR"/*.md 2>/dev/null || true)" ]]; then
        echo "WARNING: No plan files found in $PLAN_DIR."
    fi
else
    echo "WARNING: Plan directory $PLAN_DIR does not exist."
fi

# Check 5: Print confirmation
echo "Pre-check passed."
echo "Current Branch: $BRANCH"
echo "Worklog Path: $WORKLOG_DIR"
