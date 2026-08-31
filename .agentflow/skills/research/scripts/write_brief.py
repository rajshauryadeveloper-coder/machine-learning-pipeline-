#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import time
from datetime import datetime
from glob import glob

def get_default_output_path(branch: str) -> str:
    """Generates the default path for the research brief."""
    timestamp = int(time.time())
    directory = os.path.join("worklogs", branch, "artifacts")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, f"research-{timestamp}.md")

def gather_sources(output_dir: str) -> list[str]:
    """Finds all context and fetched doc files in the output directory."""
    if not os.path.exists(output_dir):
        return []
        
    sources = []
    # Collect gather_context outputs
    for f in glob(os.path.join(output_dir, "context-*.txt")):
        sources.append(f)
        
    # Collect fetch_docs outputs (assuming they are saved nearby)
    for f in glob(os.path.join(output_dir, "fetched-*.md")):
        sources.append(f)
        
    return sources

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate structure for a research brief")
    parser.add_argument('--branch', default="main", help="Current branch name")
    parser.add_argument('--topic', required=True, help="The research topic")
    parser.add_argument('--output', help="Custom output path (optional)")
    args = parser.parse_args()

    output_path = args.output
    if not output_path:
        output_path = get_default_output_path(args.branch)
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Optional: could read sources to inject them, for now we just create the skeleton
    scratch_dir = os.path.join("worklogs", args.branch, "scratch")
    sources = gather_sources(scratch_dir)
    sources_text = "\n".join([f"- {s}" for s in sources]) if sources else "- No local source files provided."

    brief_content = f"""---
type: artifact
kind: research-brief
topic: {args.topic}
created: {timestamp}
---

# Research Brief: {args.topic}

## Research Question
*What specific gap does this research address?*
[To be filled by agent]

## Findings
*Summary of facts, constraints, and observations discovered during research.*
[To be filled by agent]

## Implementation Options
*Potential paths forward based on findings.*
1. [Option 1]
2. [Option 2]
3. [Option 3]

## Recommended Approach
*The selected option and why it is the best fit.*
[To be filled by agent]

## Risks & Unknowns
*What could go wrong? What do we still not know?*
[To be filled by agent]

## Sources
*Files and URLs investigated during this research phase.*
{sources_text}
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(brief_content)
        
    print(output_path)

if __name__ == '__main__':
    main()
