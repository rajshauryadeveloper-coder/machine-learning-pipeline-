#!/usr/bin/env python3
# Note: The language choice for this script is customizable (can be swapped for .sh)
import argparse
import sys
import os
import re
from typing import List, Tuple

def parse_pytest_output(log_lines: List[str]) -> Tuple[int, int, int]:
    """Parse pytest summary lines for passes, fails, and errors."""
    passed = failed = errors = 0
    # E.g., "=== 2 failed, 1 passed, 1 error in 0.12s ==="
    for line in reversed(log_lines[-20:]):
        if "===" in line or "===" in line:
            if "failed" in line:
                m = re.search(r'(\d+)\s+failed', line)
                if m: failed = int(m.group(1))
            if "passed" in line:
                m = re.search(r'(\d+)\s+passed', line)
                if m: passed = int(m.group(1))
            if "error" in line:
                m = re.search(r'(\d+)\s+error', line)
                if m: errors = int(m.group(1))
            break
    return passed, failed, errors

def extract_failures(log_lines: List[str], max_lines: int = 30) -> str:
    """Extract key failure snippets."""
    failure_snippet = []
    in_failure = False
    for line in log_lines:
        if re.match(r'^_{3,}\s+FAILURES\s+_{3,}$', line):
            in_failure = True
        if in_failure:
            failure_snippet.append(line)
            if len(failure_snippet) >= max_lines:
                break
    
    if not failure_snippet:
        # Fallback to last few lines if no explicit failure block
        failure_snippet = log_lines[-max_lines:]
        
    return "".join(failure_snippet)

def main() -> int:
    parser = argparse.ArgumentParser(description="Capture and structure test results")
    parser.add_argument("--log-file", required=True, help="Path to the raw test log file")
    parser.add_argument("--output", required=True, help="Path to write the structured markdown result")
    args = parser.parse_args()

    if not os.path.exists(args.log_file):
        print(f"Error: Log file not found at {args.log_file}", file=sys.stderr)
        return 2

    with open(args.log_file, 'r', encoding='utf-8') as f:
        log_lines = f.readlines()

    passed, failed, errors = parse_pytest_output(log_lines)
    total = passed + failed + errors
    
    # Simple heuristic: if we couldn't parse metrics, assume failed if any "FAILED" string is near the end
    status = "failed"
    if total > 0:
        if failed == 0 and errors == 0:
            status = "passed"
    else:
        # generic exit code detection or text fallback
        last_chunk = "".join(log_lines[-30:]).lower()
        if "failed" not in last_chunk and "error" not in last_chunk and "ok" in last_chunk:
            status = "passed"

    failure_details = ""
    if status == "failed":
        failure_details = "### Failure Snippet\n```text\n" + extract_failures(log_lines) + "\n```\n"

    markdown_content = f"""---
type: artifact
kind: test-result
status: {status}
---

# Test Results

## Summary
| Metric | Count |
| :--- | :--- |
| Total | {total if total > 0 else 'Unknown'} |
| Passed | {passed} |
| Failed | {failed} |
| Errors | {errors} |

{failure_details}
"""

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Structured results written to {args.output}")
    return 0 if status == "passed" else 1

if __name__ == "__main__":
    sys.exit(main())
