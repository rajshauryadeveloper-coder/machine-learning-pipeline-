#!/usr/bin/env bash
set -euo pipefail

# Note: The language choice for this script is customizable (can be swapped for .py)
# pre_check.sh - Verify preconditions before running tests

# Environment Setup
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
AGENTFLOW_ROOT=${AGENTFLOW_ROOT:-$(pwd)}
ATTEMPTS_DIR="${AGENTFLOW_ROOT}/worklogs/${BRANCH}/attempts"
AGENT_CONTEXT="${AGENTFLOW_ROOT}/AGENT_CONTEXT.md"

echo "Running pre-checks for test skill..."

# Check: not on main/master branch
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
    echo "ERROR: Cannot run tests directly on main/master branch in this workflow."
    exit 1
fi

# Check: TEST_CMD is defined
TEST_CMD="pytest"
if [[ -f "$AGENT_CONTEXT" ]]; then
    CONTEXT_CMD=$(grep -i "test command" "$AGENT_CONTEXT" | cut -d':' -f2 | xargs || true)
    if [[ -n "$CONTEXT_CMD" ]]; then
        TEST_CMD="$CONTEXT_CMD"
    fi
fi
if [[ -n "${ENV_TEST_CMD:-}" ]]; then
    TEST_CMD="$ENV_TEST_CMD"
fi

# Check: latest attempt is complete in implement stage
LATEST_ATTEMPT=$(ls -t "${ATTEMPTS_DIR}"/*.md 2>/dev/null | head -n 1 || true)
if [[ -n "$LATEST_ATTEMPT" ]]; then
    if ! grep -q "stage: implement" "$LATEST_ATTEMPT" || ! grep -q "status: complete" "$LATEST_ATTEMPT"; then
        echo "WARNING: Latest attempt does not indicate implement is complete. Proceeding with caution."
    fi
else
    echo "WARNING: No attempts found in $ATTEMPTS_DIR"
fi

echo "Pre-checks passed."
echo "Test command to be used: $TEST_CMD"
exit 0
