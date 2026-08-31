---
type: skill
name: review
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: merge
chain_on_failure: implement
tags: [review, quality]
---

# Review Skill

## Goal
Perform a thorough, objective review of a proposed change to ensure it meets all acceptance criteria, quality standards, and security requirements before merging.

## Routing & Reference Table
| Condition | Action |
|-----------|--------|
| Always | Load `references/review_criteria.md` for standard acceptance patterns. |
| Changes touch auth, input handling, or external APIs | Load `references/security_checklist.md`. |

## When to Invoke
Invoke this skill after the `test` skill reports all tests passing successfully on the current branch.

## Inputs
| Input | Description |
|-------|-------------|
| Branch Git Diff | The proposed code changes relative to the base branch. |
| Original Prompt | The stated acceptance criteria and functional requirements. |
| Worklogs | The full history of attempts (`worklogs/<branch>/attempts/`). |
| AGENT_CONTEXT.md | High-level architectural rules and constraints. |

## Hook Scripts
| Script | Language | Purpose |
|--------|----------|---------|
| `scripts/pre_check.sh` | Bash/Python | Verify latest test attempt passed and diff is non-empty. |
| `scripts/diff_summary.sh` | Bash/Python | Generate a readable diff summary and commit log. |
| `scripts/quality_checks.sh` | Bash/Python | Run automated linting and type-checking. |

## Steps
1. Run `scripts/pre_check.sh` to ensure the branch is ready for review.
2. Run `scripts/diff_summary.sh` to generate a readable summary of the changes.
3. Read the original prompt to understand the acceptance criteria.
4. Check each criterion systematically.
   - *Use a checklist or table format to track progress.*
5. Run `scripts/quality_checks.sh` to identify any lingering style or typing issues.
6. If the changes are security-relevant (auth, input, APIs), read `references/security_checklist.md` and verify constraints.
7. Determine the Verdict:
   - **Approve:** If all criteria are met and quality is acceptable.
   - **Reject:** If there are correctness issues, missing requirements, or security risks.

## Pre-Check
The pre-check ensures that the review skill is only invoked on a branch that has actually been tested and has changes. Do not proceed if the pre-check fails.

## Post-Complete
Depending on your verdict, write a post-completion report in the worklogs:
- **Approve Path:** Write a brief approval summary, noting any minor feedback or praise. Trigger the `merge` skill.
- **Reject Path:** Write a highly specific, actionable list of feedback. Include exact file paths and line numbers where possible. Trigger the `implement` skill to address the feedback.

## On Retry
If you are re-reviewing a branch after the `implement` skill has addressed previous feedback:
1. Review the previous rejection feedback.
2. Verify that the newly pushed changes explicitly address all points raised.
3. Perform a delta review of the new changes.

## Chain
- On Success (Approve): Chain to the `merge` skill.
- On Failure (Reject): Chain to the `implement` skill.

## Outputs
- Review verdict (approve/reject).
- Actionable feedback list (if rejected).
- Completed review artifact in the branch's worklog.
