---
type: workflow
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T18:30:00Z
---

# Agent Workflow Engine (v2 Optimized)

*The state machine governing agent execution, transitions, and limits.*

## Streamlined Stage Sequence

```ascii
[START] --> (Plan: flow start) --> (Implement) <--> (Verify: flow verify)
                                                      |
                                          (all gates pass)
                                                      |
                                                      v
                                            (Ship: flow ship)
                                                      |
                                                      v
                                                   [CLOSED]
```

## Stage Transitions

| From Stage | To Stage | Trigger / Condition | Command |
| --- | --- | --- | --- |
| `Plan` | `Implement` | Feature branch & plan initialized | `./scripts/flow start <slug>` |
| `Implement` | `Verify` | Code changes and unit tests written | Direct code editing |
| `Verify` | `Implement` | Tests fail or lint/formatting issues | `./scripts/flow verify` (exit code 1) |
| `Verify` | `Ship` | All tests pass, coverage >=60%, lint/format clean | `./scripts/flow verify` (exit code 0) |
| `Ship` | `Closed` | Commits merged, pushed to main, postmortem recorded | `./scripts/flow ship` |

## Verification Gates (Unified in `flow verify`)

1. **Pytest Suite**: All unit and integration tests must pass.
2. **Coverage Gate**: Test coverage must meet or exceed 60% across application modules.
3. **Flake8 Linter**: 0 PEP-8 or syntax violations.
4. **Black Formatter**: Code must adhere strictly to black format standards.
5. **Git Diff**: Automated diff capture and statistics logged to worklog artifacts.

## Shipping Engine (Unified in `flow ship`)

1. **Atomic Git Commit**: Stages all changes with descriptive commit messages.
2. **Branch Synchronization**: Pushes feature branch to `origin`.
3. **Main Branch Merge**: Fast-forwards/merges feature branch into `main` and pushes `main`.
4. **Automated Postmortem**: Writes structured `postmortem.md` in branch worklog.
5. **Rollup Ledger**: Appends the key lesson learned to `.agentflow/postmortems/ROLLUP.md`.
6. **Task Closure**: Updates worklog and origin prompt status to `completed`.

## Retry & Guardrail Limits

| Metric | Limit | Consequence |
| --- | --- | --- |
| `max_attempts_per_stage` | 3 | Escalates to human on 4th verification failure |
| `max_workflow_steps` | 10 | Hard cap to prevent infinite development cycles |
