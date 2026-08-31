#!/usr/bin/env bash
# Language: bash (swap for .py version if preferred)
set -euo pipefail

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
SLUG="$("$SCRIPT_DIR/../../scripts/worklog_path.sh" "$BRANCH" 2>/dev/null || echo unknown)"
WORKLOG_DIR="${WORKLOG_DIR:-$AGENTFLOW_ROOT/worklogs/$SLUG}"

echo "Running Pre-Check for implement skill..."

# Check 1: Refuse to run on main/master unless bootstrap bypass is set
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
    if [[ "${ALLOW_MAIN_BRANCH:-}" != "1" ]]; then
        echo "ERROR: Refusing to run on $BRANCH branch."
        echo "Hint: Create a feature branch, or set ALLOW_MAIN_BRANCH=1 for bootstrap tasks only."
        exit 1
    fi
    echo "WARNING: Running on $BRANCH with ALLOW_MAIN_BRANCH=1 (bootstrap only)."
fi

# Check 2: Require at least one commit
if [[ "$BRANCH" == "HEAD" ]]; then
    echo "ERROR: No commits yet. Cannot determine branch."
    exit 1
fi

# Check 3: Detect uncommitted changes
if git status --porcelain | grep -q "^??"; then
    echo "WARNING: Untracked files detected. Proceed with caution."
elif git status --porcelain | grep -q "^ M"; then
    echo "WARNING: Unstaged changes detected. Ensure these are intended."
fi

# Check 4: Verify the worklog SUMMARY.md exists (using branch slug)
if [[ ! -f "$WORKLOG_DIR/SUMMARY.md" ]]; then
    echo "ERROR: Worklog SUMMARY.md missing at $WORKLOG_DIR/SUMMARY.md"
    echo "Hint: Run plan skill new_worklog.sh for branch '$BRANCH' (slug: $SLUG)."
    exit 1
fi

# Check 5: Verify plan file exists
PLAN_DIR="$AGENTFLOW_ROOT/plans"
if [[ -d "$PLAN_DIR" ]]; then
    if ! compgen -G "$PLAN_DIR/*.md" > /dev/null; then
        echo "WARNING: No plan files found in $PLAN_DIR."
    fi
else
    echo "WARNING: Plan directory $PLAN_DIR does not exist."
fi

echo "Pre-check passed."
echo "Current Branch: $BRANCH"
echo "Worklog Slug: $SLUG"
echo "Worklog Path: $WORKLOG_DIR"
