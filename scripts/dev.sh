#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
