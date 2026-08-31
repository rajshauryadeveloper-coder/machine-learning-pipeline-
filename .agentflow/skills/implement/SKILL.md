---
type: skill
name: implement
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: test
chain_on_failure: null
tags: [implement, code]
---

# Implement Skill

## Routing & Reference Table

| Condition | Reference File | Action |
|---|---|---|
| Plan is missing or ambiguous | `references/planning.md` | Read reference to write or refine the plan before starting |
| Modifying core architecture | `references/code_patterns.md` | Read reference to ensure patterns adhere to standards |

## When to Invoke
- **New Task**: Triggered from `prompts/` directory to begin implementation.
- **Retry**: Triggered when a downstream stage (`test`, `review`) fails and returns execution context to implementation.

## Inputs

| Input Type | Path/Pattern | Purpose |
|---|---|---|
| Prompt | `prompts/<file>.md` | Raw requirements and task definition |
| Plan | `plans/<timestamp>-<slug>.md` | Implementation strategy and architecture decisions |
| Context | `AGENT_CONTEXT.md` | High-level system state and active invariants |
| Worklog | `worklogs/<branch>/attempts/` | Historical attempts and retry feedback |

## Hook Scripts

| Script | Command | Purpose | Language |
|---|---|---|---|
| Pre-Check | `bash scripts/pre_check.sh` | Validate branch, check uncommitted changes, verify worklog and plan exist | bash (swap for .py version if preferred) |
| Capture Diff | `python scripts/capture_diff.py` | Record file changes into an artifact markdown file | python (swap for .sh version if preferred) |
| Post-Complete | `bash scripts/post_complete.sh` | Write attempt file and update summary metadata | bash (swap for .py version if preferred) |

## Steps

1. **Run pre-check**: Execute `bash scripts/pre_check.sh` to validate the environment. Address any failures before proceeding.
2. **Read plan**: Review the active plan in `plans/` and identify target files for modification.
3. **Review feedback**: If this is a retry, check `worklogs/<branch>/attempts/` for previous feedback and avoid repeating errors.
4. **Implement**: Make minimal, targeted changes. Apply one concern per commit. Adhere to code patterns.
5. **Capture changes**: Run `python scripts/capture_diff.py` to record the exact changes made during this step.
6. **Finalize**: Run `bash scripts/post_complete.sh` to update tracking files and finalize the implementation stage.

## Pre-Check
The `pre_check.sh` script verifies that execution is not on the main/master branch, detects uncommitted changes not authored by this session, ensures the worklog `SUMMARY.md` exists, and confirms a plan file is available.

## Post-Complete
The `post_complete.sh` script determines the current attempt number, generates a timestamped attempt file containing a summary and the git diff file list, and updates the `SUMMARY.md` stage tracker.

## On Retry
When invoked as a retry:
- Read the most recent attempt file in `attempts/`.
- Address specific issues raised in the feedback before expanding the scope.
- **NEVER** overwrite old attempt files; always append new attempts.

## Chain
- **Success**: Chains to `test` skill.
- **Failure**: Chains to `implement` (retry), up to `max_retries_per_stage`.

## Outputs
- **Attempt File**: Path to the generated attempt record in `worklogs/<branch>/attempts/`.
- **Stage Update**: Modified `SUMMARY.md` reflecting the new stage status.
