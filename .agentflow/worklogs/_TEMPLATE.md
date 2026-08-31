---
type: worklog
status: active
branch: <branch-name>
created: 2026-08-31T16:40:51Z
tags: []
---

# Worklog: [Insert Task Title]

> **NOTE:** Sub-directories `attempts/` and `artifacts/` are created on demand by skill scripts to store detailed execution traces, test outputs, and diffs. Do not put massive logs directly in this file.

## Status
**active** - Not started. (Valid states: active, paused, completed, abandoned, escalated)

## Origin Prompt
[Link to Prompt File](../prompts/your_prompt.md)

## Plan
[Link to Plan File](../plans/your_plan.md)

## Current Stage
**implement**
*(Valid stages: plan | implement | test | review | merging | merged | abandoned | escalated)*

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

## Outcome
*(To be filled when task is completed or escalated)*
**[Pending / Merged / Escalated]**
Brief summary of the final state, root cause of escalation, or success metrics.

## Artifacts
*(Link to files generated during execution)*
- [Initial Diff](artifacts/initial_implementation.patch)
- [Test Coverage Report](artifacts/coverage_run_1.txt)
- [Review Notes](artifacts/review_feedback.md)
