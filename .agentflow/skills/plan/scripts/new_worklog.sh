#!/usr/bin/env bash
# Create a worklog directory for the current (or given) branch.
#
# Usage:
#   bash .agentflow/skills/plan/scripts/new_worklog.sh \
#     --title "Add Auth" \
#     --prompt prompts/add_auth.md \
#     --plan plans/20260831-add-auth.md

set -euo pipefail

AGENTFLOW_ROOT="${AGENTFLOW_ROOT:-.agentflow}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TITLE=""
PROMPT=""
PLAN=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --title) TITLE="$2"; shift 2 ;;
        --prompt) PROMPT="$2"; shift 2 ;;
        --plan) PLAN="$2"; shift 2 ;;
        *) echo "Unknown argument: $1" >&2; exit 1 ;;
    esac
done

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
SLUG="$("$SCRIPT_DIR/../../scripts/worklog_path.sh" "$BRANCH")"
WORKLOG_DIR="$AGENTFLOW_ROOT/worklogs/$SLUG"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$WORKLOG_DIR/attempts" "$WORKLOG_DIR/artifacts"

cat > "$WORKLOG_DIR/SUMMARY.md" <<EOF
---
type: worklog
status: active
branch: $BRANCH
worklog_slug: $SLUG
created: $TIMESTAMP
tags: []
---

# Worklog: ${TITLE:-$BRANCH}

> **NOTE:** Sub-directories \`attempts/\` and \`artifacts/\` store detailed execution traces. Use worklog slug \`$SLUG\` (branch \`$BRANCH\`).

## Status
**active** - Not started.

## Origin Prompt
${PROMPT:+[Prompt](../$PROMPT)}
${PROMPT:-*(not set)*}

## Plan
${PLAN:+[Plan](../$PLAN)}
${PLAN:-*(not set)*}

## Current Stage
**plan**

## What Was Done

- **[$TIMESTAMP]** Worklog created for branch \`$BRANCH\` (slug: \`$SLUG\`).

## Metrics

| Stage | Attempts | Outcome | Notes |
| --- | --- | --- | --- |
| \`plan\` | 0 | Pending | - |
| \`implement\` | 0 | Pending | - |
| \`test\` | 0 | Pending | - |
| \`review\` | 0 | Pending | - |
| \`merge\` | 0 | Pending | - |
| \`postmortem\` | 0 | Pending | - |

## Outcome
**Pending**

## Artifacts
- *(none yet)*
EOF

echo "Created worklog at $WORKLOG_DIR/SUMMARY.md"
echo "Branch: $BRANCH"
echo "Slug: $SLUG"
