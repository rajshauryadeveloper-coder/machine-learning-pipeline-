---
type: skill
name: ship
version: 2.0.0
status: active
created: 2026-08-31T18:25:00Z
chain_to: null
chain_on_failure: implement
tags: [ship, merge, git, postmortem, rollup]
---

# Ship Skill (Optimized Merged Release)

## Goal
Atomically commit changes, push to remote, merge feature branch to `main`, write the postmortem learning, append to `ROLLUP.md`, and mark the task completed in a single command (`flow ship`).

## When to Invoke
- Immediately after `verify` skill reports all verification gates passing.

## Hook Commands

| Action | Command | Automated By |
| --- | --- | --- |
| **All-In-One Ship** | `./scripts/flow ship --lesson "<Category>" --details "<Details>"` | `flow.py` |

## Steps

1. **Ship the Task**:
   ```bash
   ./scripts/flow ship \
     -m "feat(<slug>): describe feature changes" \
     --lesson "Key Domain/Technical Lesson" \
     --details "Actionable insight learned from this iteration."
   ```
2. **Review Output**:
   - Commits all tracked and untracked changes with descriptive message.
   - Pushes feature branch to `origin`.
   - Checks out `main`, merges feature branch, and pushes `main`.
   - Automatically writes `worklogs/<branch-slug>/postmortem.md`.
   - Automatically appends entry to `.agentflow/postmortems/ROLLUP.md`.
   - Marks prompt and worklog status `completed`.

## Chain
- **Terminal**: Workflow successfully completed and closed.

## Outputs
- Merged commits on `main` and remote `origin/main`.
- `worklogs/<branch-slug>/postmortem.md`
- Appended entry in `.agentflow/postmortems/ROLLUP.md`
- Worklog `SUMMARY.md` marked `completed` and `merged`.
