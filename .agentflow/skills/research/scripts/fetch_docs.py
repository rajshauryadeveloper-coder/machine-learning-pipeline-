#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

def strip_html_tags(text: str) -> str:
    """Removes HTML tags from a string using regex."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def fetch_url(url: str) -> str | None:
    """Fetches a URL and returns the text content, stripping HTML tags."""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'AgentFlow-Research/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            text = strip_html_tags(content)
            # Take only the first 200 lines to prevent context bloat
            lines = text.splitlines()[:200]
            return '\n'.join(lines)
    except urllib.error.URLError as e:
        print(f"Warning: Failed to fetch {url} - {e}")
        return None
    except Exception as e:
        print(f"Warning: Unexpected error fetching {url} - {e}")
        return None

def fetch_file(filepath: str) -> str | None:
    """Reads content from a local file."""
    if not os.path.exists(filepath):
        print(f"Warning: Local file not found - {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Failed to read file {filepath} - {e}")
        return None

def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch documentation for research")
    parser.add_argument('--topic', required=True, help="The research topic")
    parser.add_argument('--url', help="URL to fetch documentation from")
    parser.add_argument('--file', help="Local file to read documentation from")
    parser.add_argument('--output', required=True, help="Output path for fetched docs")
    args = parser.parse_args()

    content = None
    source = "Unknown"

    if args.url:
        print(f"Fetching from URL: {args.url}")
        content = fetch_url(args.url)
        source = args.url
    elif args.file:
        print(f"Fetching from File: {args.file}")
        content = fetch_file(args.file)
        source = args.file
    else:
        print("Warning: Neither --url nor --file provided. Exiting.")
        sys.exit(0)

    if not content:
        # Exit 0 so we don't break the agent chain on network/missing file issues
        sys.exit(0)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"---\n")
        f.write(f"source: {source}\n")
        f.write(f"topic: {args.topic}\n")
        f.write(f"fetched_at: {timestamp}\n")
        f.write(f"---\n\n")
        f.write(content)
        
    print(f"Successfully wrote fetched docs to: {args.output}")

if __name__ == '__main__':
    main()
