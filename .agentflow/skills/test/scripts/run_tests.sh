#!/usr/bin/env bash
set -uo pipefail

# Note: The language choice for this script is customizable (can be swapped for .py)
# run_tests.sh - Discover and run test suite, logging output

AGENTFLOW_ROOT=${AGENTFLOW_ROOT:-$(pwd)}
BRANCH=${BRANCH:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")}
TEST_CMD=${TEST_CMD:-pytest}
LOG_DIR="${AGENTFLOW_ROOT}/worklogs/${BRANCH}/artifacts"

echo "Preparing to run tests..."

# Create LOG_DIR if missing
if [[ ! -d "$LOG_DIR" ]]; then
    echo "Creating log directory: $LOG_DIR"
    mkdir -p "$LOG_DIR"
fi

# Generate timestamped log filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/test_run_${TIMESTAMP}.log"

echo "Executing test command: $TEST_CMD"
echo "Logging output to: $LOG_FILE"

# Run TEST_CMD, tee output to log file
# We disable errexit (set -e) because tests failing is normal and we want to capture the exit code
eval "$TEST_CMD" 2>&1 | tee "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}

echo "Test run completed."
echo "Log file path: $LOG_FILE"
echo "Exit code: $EXIT_CODE"

# Pass through the test suite exit code
exit $EXIT_CODE
