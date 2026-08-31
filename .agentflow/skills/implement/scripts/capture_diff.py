#!/usr/bin/env python3
# Language: python (swap for .sh version if preferred)
from __future__ import annotations

import argparse
import subprocess
import sys
import os
from datetime import datetime, timezone

def run_git_command(args: list[str]) -> str:
    try:
        result = subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git command failed: {' '.join(args)}", file=sys.stderr)
        print(f"Git stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(description="Capture git diff as a markdown artifact")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    try:
        branch = run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    except Exception:
        branch = "unknown"

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    
    if args.output:
        output_path = args.output
    else:
        output_path = f".agentflow/worklogs/{branch}/artifacts/diff-{timestamp}.md"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    diff_stat = run_git_command(["git", "diff", "--stat", "HEAD"])
    full_diff = run_git_command(["git", "diff", "HEAD"])

    if not full_diff:
        print("Note: No differences found. Exiting cleanly.")
        sys.exit(0)

    content = f"""---
type: artifact
kind: diff
timestamp: {timestamp}
---

# Diff Capture

## Statistics
```text
{diff_stat}
```

## Changes
```diff
{full_diff}
```
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Diff captured to {output_path}")

if __name__ == "__main__":
    main()
