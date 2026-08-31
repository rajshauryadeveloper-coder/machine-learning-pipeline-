---
name: plan
status: active
chain_to: implement
tags: [plan, start, scaffold, context]
---
# Plan Skill (v3 High-Speed)

## Goal
Start a task, create branch, capture single-shot context snapshot, and scaffold plan in 1 step.

## Commands
```bash
./scripts/flow start <slug> --title "Task Title" --prompt prompts/<file>.md
./scripts/flow context   # Capture full DB schema, API routes, and ML state in 1 shot
```

## Steps
1. Run `./scripts/flow start <slug>` to create branch and worklog.
2. Run `./scripts/flow context` to obtain full repository state without multiple file reads.
3. Present plan with files and dependencies to user. Upon approval, chain to `implement`.
