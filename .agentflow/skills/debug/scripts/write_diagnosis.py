#!/usr/bin/env python3
from __future__ import annotations

# Language: python — swap for a .sh version if preferred

import argparse
import datetime
import os
import sys

def generate_timestamp() -> str:
    """Generates a UTC timestamp suitable for filenames."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S")

def create_diagnosis(branch: str | None, hypothesis: str, affected_files: str, output: str | None) -> str:
    """Creates the markdown content for a diagnosis file."""
    timestamp = generate_timestamp()
    
    if not output:
        # Default filename based on current timestamp
        if branch:
            output = f"worklogs/{branch}/artifacts/diagnosis-{timestamp}.md"
        else:
            output = f"diagnosis-{timestamp}.md"
            
    files_list = "\n".join([f"- {f.strip()}" for f in affected_files.split(",") if f.strip()])
    if not files_list:
        files_list = "- (No specific files provided)"

    md_content = f"""---
type: artifact
kind: diagnosis
status: active
created: {timestamp}
---

## Root Cause Hypothesis
{hypothesis}

## Affected Files
{files_list}

## Evidence
<!-- Agent: Fill this section with specific tracebacks, logs, or code snippets -->


## Fix Strategy
<!-- Agent: Detail exactly how this will be fixed, constrained to the affected files above -->


## What Was Already Tried
<!-- Agent: Summarize from attempt history what has been attempted and why it failed -->


## Escalate If
After 2 debug passes without resolution
"""
    return md_content, output

def main() -> int:
    parser = argparse.ArgumentParser(description="Write a structured diagnosis file.")
    parser.add_argument("--branch", help="Current branch name (used for default pathing)")
    parser.add_argument("--hypothesis", required=True, help="One-sentence root cause hypothesis")
    parser.add_argument("--affected-files", required=True, help="Comma-separated list of affected files")
    parser.add_argument("--output", help="Optional output path")
    args = parser.parse_args()
    
    content, out_path = create_diagnosis(args.branch, args.hypothesis, args.affected_files, args.output)
    
    # Ensure directory exists if path has directories
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Diagnosis written to {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
