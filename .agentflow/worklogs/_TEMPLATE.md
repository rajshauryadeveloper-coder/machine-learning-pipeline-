---
type: worklog
status: active
branch: <branch-name>
worklog_slug: <branch-slug>
created: 2026-08-31T16:40:51Z
tags: []
---

# Worklog: [Insert Task Title]

> **NOTE:** Worklog path uses branch slug (`feature/foo` → `feature-foo`). Create the branch **before** running `new_worklog.sh`. Sub-directories `attempts/` and `artifacts/` store detailed traces.

## Status
**active** - Not started. (Valid states: active, paused, completed, abandoned, escalated)

## Origin Prompt
[Link to Prompt File](../prompts/your_prompt.md)

## Plan
[Link to Plan File](../plans/your_plan.md)

## Current Stage
**plan**
*(Valid stages: plan | implement | test | review | merge | merged | postmortem | abandoned | escalated)*

## What Was Done
*(Updated by each skill's `post_complete.sh` or by the agent directly before chaining)*

- **[YYYY-MM-DD HH:MM]** Initiated plan skill. Created initial scaffold and scope.
- **[YYYY-MM-DD HH:MM]** Transitioned to implement. Writing core modules.
- *(Agent: append chronological updates here...)*

## Metrics

| Stage | Attempts | Outcome | Notes |
| --- | --- | --- | --- |
| `plan` | 1 | Success | Plan approved automatically. |
| `implement` | 2 | Ongoing | First attempt failed linting, retrying. |
| `test` | 0 | Pending | - |
| `review` | 0 | Pending | - |
| `merge` | 0 | Pending | - |
| `postmortem` | 0 | Pending | - |

## Outcome
*(To be filled when task is completed or escalated)*
**[Pending / Merged / Escalated]**
Brief summary of the final state, root cause of escalation, or success metrics.

## Artifacts
*(Link to files generated during execution)*
- [Initial Diff](artifacts/initial_implementation.patch)
- [Test Coverage Report](artifacts/coverage_run_1.txt)
- [Review Notes](artifacts/review_feedback.md)
- [Postmortem](postmortem.md)
