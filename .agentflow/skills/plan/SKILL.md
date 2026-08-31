---
type: skill
name: plan
version: 1.0.0
status: active
created: 2026-08-31T17:45:00Z
chain_to: implement
chain_on_failure: null
tags: [plan, design]
---

# Plan Skill

## Goal
Produce an approved implementation plan and initialize branch-scoped tracking before any code changes.

## When to Invoke
- **New Task**: First skill in the workflow for any feature or fix.
- **Re-plan**: When scope changes significantly mid-task (increment plan version, do not overwrite).

## Inputs

| Input | Path | Purpose |
| --- | --- | --- |
| Prompt | `prompts/<file>.md` | Requirements and acceptance criteria |
| Context | `AGENT_CONTEXT.md` | Architecture rules and commands |
| Template | `plans/_TEMPLATE.md` | Plan structure |

## Hook Scripts

| Script | Command | Purpose |
| --- | --- | --- |
| Pre-Check | `bash scripts/pre_check.sh` | Verify git repo and branch state |
| New Worklog | `bash scripts/new_worklog.sh` | Create worklog using branch slug convention |

## Steps

1. **Create feature branch** (unless bootstrap task on `main`):
   ```bash
   git checkout -b feature/<short-description>
   ```
2. **Run new worklog** using the **current branch name** (slug is derived automatically):
   ```bash
   bash .agentflow/skills/plan/scripts/new_worklog.sh \
     --title "Task Title" \
     --prompt prompts/my_task.md \
     --plan plans/<timestamp>-<slug>.md
   ```
3. **Write plan** to `plans/<timestamp>-<slug>.md` from `_TEMPLATE.md`.
4. **Mark prompt** status `in_progress` in frontmatter.
5. **Update worklog** stage to `implement` when plan is approved.

## Branch & Worklog Rules (from postmortem)

| Rule | Rationale |
| --- | --- |
| Create the worklog on the **same branch** you will merge from | Avoids orphaned worklogs when branch is renamed |
| Worklog path uses slug: `feature/foo` → `worklogs/feature-foo/` | Slashes are invalid in some tooling paths |
| Bootstrap-only tasks may run on `main` | Repository initialization is the exception |
| Never rename a branch after creating its worklog | Create a new worklog if branch must change |

## Pre-Check
- Git repository exists with at least one commit (except bootstrap).
- Feature branch created (except bootstrap on `main`).

## Post-Complete
- Plan file exists with `status: approved`.
- Worklog `SUMMARY.md` links to plan and prompt.
- Worklog `Current Stage` set to `implement`.

## Chain
- **Success**: Chains to `implement` skill.
- **Failure**: Stops; user must clarify requirements.

## Outputs
- `plans/<timestamp>-<slug>.md`
- `worklogs/<branch-slug>/SUMMARY.md`
