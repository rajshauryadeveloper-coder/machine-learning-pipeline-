---
type: skill
name: postmortem
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: null
chain_on_failure: null
tags: [postmortem, retrospective]
---

# Postmortem Skill

This skill analyzes completed workflows to extract lessons and improve future execution.

## Routing & Reference Table

| Reference | When to Use |
| :--- | :--- |
| `references/lessons_taxonomy.md` | To categorize lessons. |

## When to Invoke

This skill is invoked automatically by the orchestrator after:
- A workflow is merged to main.
- A workflow is abandoned.
- A workflow is escalated past the retry limit.

## Inputs

| Input | Description |
| :--- | :--- |
| `worklogs/<branch>/SUMMARY.md` | The final worklog. |
| `worklogs/<branch>/attempts/` | Full history of attempts. |
| `postmortems/ROLLUP.md` | Prior patterns and historical lessons. |

## Hook Scripts

| Script | Purpose | Language |
| :--- | :--- | :--- |
| `collect_history.sh` | Aggregates all attempt files into a digest. | Bash (swappable) |
| `append_rollup.py` | Writes a new entry to `ROLLUP.md`. | Python (swappable) |

## Steps

1. **Verify Terminal State**: Verify the worklog reached a terminal state (merged/abandoned/escalated).
2. **Collect History**: Run `collect_history.sh` to produce a history digest of all attempts.
3. **Identify Lessons**: Analyze the digest and worklog to identify what worked, what failed, and what needs to change.
4. **Write Postmortem**: Write the detailed postmortem to `worklogs/<branch>/postmortem.md`.
5. **Update Rollup**: Run `append_rollup.py` to add the key lesson to `postmortems/ROLLUP.md`.

## Pre-Check

- The worklog is in a terminal state.

## Post-Complete

- `postmortem.md` is written to the branch's worklog directory.
- `ROLLUP.md` is appended with a new entry.
- The worklog status is set to closed.

## Rollup Format

Entries in `postmortems/ROLLUP.md` follow this format:

```markdown
### <branch> — <date>
**Outcome:** [merged|abandoned|escalated]
**Attempts:** [number]
**Key lesson:** [category: brief description]
**Details:** [short explanation of the lesson]
```

## Chain

This skill is **terminal**. There is no automatic next skill.

## Outputs

- `worklogs/<branch>/artifacts/history-digest-<timestamp>.md`
- `worklogs/<branch>/postmortem.md`
- Updated `postmortems/ROLLUP.md`
