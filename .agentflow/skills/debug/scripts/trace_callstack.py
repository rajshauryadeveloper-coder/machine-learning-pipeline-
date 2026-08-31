#!/usr/bin/env python3
from __future__ import annotations

# Language: python — swap for a .sh version if preferred

import argparse
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple

def parse_tracebacks(log_path: str) -> Dict[str, Dict[int, Dict[str, int]]]:
    """Parses Python traceback blocks and extracts file, line, exception type and counts."""
    # Pattern to match: File "path/to/file.py", line 42, in function
    file_pattern = re.compile(r'^\s*File\s+"([^"]+)",\s+line\s+(\d+),')
    # Exception type usually starts at the beginning of the line with no spaces after a traceback block
    exc_pattern = re.compile(r'^([a-zA-Z0-9_]+Error|[a-zA-Z0-9_]+Exception):\s*(.*)')
    
    tracebacks = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    in_traceback = False
    current_files = []
    
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "Traceback (most recent call last):" in line:
                in_traceback = True
                current_files = []
                continue
            
            if in_traceback:
                file_match = file_pattern.search(line)
                if file_match:
                    path = file_match.group(1)
                    line_num = int(file_match.group(2))
                    current_files.append((path, line_num))
                    continue
                
                exc_match = exc_pattern.search(line)
                if exc_match and current_files:
                    exc_type = exc_match.group(1)
                    # The root file is typically the last file referenced before the exception line
                    root_path, root_line = current_files[-1]
                    tracebacks[root_path][root_line][exc_type] += 1
                    in_traceback = False
                    current_files = []
    
    return tracebacks

def write_report(tracebacks: Dict[str, Dict[int, Dict[str, int]]], output_path: str | None) -> None:
    lines = ["# Callstack Traceback Report\n"]
    
    if not tracebacks:
        lines.append("No tracebacks found in the provided log.\n")
    else:
        lines.append("| File | Line | Exception Type | Count |")
        lines.append("| --- | --- | --- | --- |")
        
        flat_data = []
        for file_path, lines_dict in tracebacks.items():
            for line_num, exc_dict in lines_dict.items():
                for exc_type, count in exc_dict.items():
                    flat_data.append((count, file_path, line_num, exc_type))
        
        # Sort by frequency descending
        flat_data.sort(key=lambda x: x[0], reverse=True)
        
        for count, file_path, line_num, exc_type in flat_data:
            lines.append(f"| {file_path} | {line_num} | {exc_type} | {count} |")
    
    report_content = "\n".join(lines)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report written to {output_path}")
    else:
        print(report_content)

def main() -> int:
    parser = argparse.ArgumentParser(description="Parse test logs for tracebacks.")
    parser.add_argument("--log", required=True, help="Path to the test log file")
    parser.add_argument("--output", help="Optional output markdown path")
    args = parser.parse_args()
    
    if not os.path.exists(args.log):
        print(f"Error: Log file {args.log} does not exist.")
        # Ensure we write an empty report even on error for safe defaults
        write_report({}, args.output)
        return 0
        
    tracebacks = parse_tracebacks(args.log)
    write_report(tracebacks, args.output)
    return 0

if __name__ == "__main__":
    exit(main())
