---
type: skill
name: plan
version: 2.0.0
status: active
created: 2026-08-31T18:25:00Z
chain_to: implement
chain_on_failure: null
tags: [plan, design, scaffold]
---

# Plan Skill (Optimized)

## Goal
Initialize branch-scoped tracking, create a feature branch, generate the implementation plan, and set worklog status in a single step (`flow start`).

## When to Invoke
- **New Task**: First skill in the workflow for any feature or fix.

## Commands

```bash
./scripts/flow start <slug> \
  --title "Task Title" \
  --prompt prompts/my_prompt.md \
  --plan plans/20260831-my-plan.md
```

## Steps
1. Run `./scripts/flow start <slug>` with prompt and plan arguments.
2. Refine the plan in `plans/<timestamp>-<slug>.md` if custom architecture or steps are needed.
3. Automatically transitions worklog stage to `implement`.

## Outputs
- `plans/<timestamp>-<slug>.md`
- `worklogs/<branch-slug>/SUMMARY.md`
