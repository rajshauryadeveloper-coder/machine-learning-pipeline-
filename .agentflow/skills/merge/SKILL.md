---
type: skill
name: merge
version: 1.0.0
status: active
created: 2026-08-31T17:45:00Z
chain_to: postmortem
chain_on_failure: null
tags: [merge, git]
---

# Merge Skill

## Goal
Commit final changes, merge to the target branch, push to remote, and close the task worklog.

## When to Invoke
- After `review` approves the change.
- When the user explicitly requests commit and push.

## Inputs

| Input | Description |
| --- | --- |
| Worklog | `worklogs/<branch-slug>/SUMMARY.md` |
| Git diff | Staged and unstaged changes on the feature branch |

## Steps

1. **Verify** all acceptance criteria in the prompt are met.
2. **Commit** with a message focused on *why* (not just what).
3. **Push** feature branch to remote (if not already on `main`).
4. **Merge** to `main` via PR or fast-forward as appropriate.
5. **Update worklog**:
   - `Current Stage` → `merged`
   - `Status` → `completed`
   - Record commit SHA(s) in `What Was Done`
6. **Update prompt** frontmatter `status: completed`.

## Pre-Check
- Review skill approved the change.
- Tests and lint passed on the final commit.

## Post-Complete
- Worklog reflects merged state with commit references.
- Chains to `postmortem` skill for retrospective.

## Chain
- **Success**: Chains to `postmortem` skill.
- **Failure**: Returns to `implement` if merge conflicts or push fails.

## Outputs
- Git commit(s) on `main` (or target branch)
- Updated worklog with merge metadata
