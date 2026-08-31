#!/usr/bin/env bash
# Convert a git branch name to a filesystem-safe worklog directory slug.
# Example: feature/add-auth -> feature-add-auth
#
# Usage:
#   worklog_slug="$(bash .agentflow/scripts/worklog_path.sh)"
#   worklog_slug="$(bash .agentflow/scripts/worklog_path.sh feature/add-auth)"

set -euo pipefail

branch="${1:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")}"

if [[ -z "$branch" || "$branch" == "HEAD" ]]; then
    echo "unknown" >&2
    exit 1
fi

echo "${branch//\//-}"
