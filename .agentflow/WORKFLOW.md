---
type: workflow
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T17:45:00Z
---

# Agent Workflow Engine

*The state machine governing agent execution, transitions, and limits.*

## Stage Sequence

```ascii
[START] --> (Plan) --> (Implement) <--> (Test)
                                          |
                                          v
                                       (Review)
                                          |
                              +-----------+-----------+
                              |                       |
                              v                       v
                           (Merge)               [ESCALATE]
                              |
                              v
                        (Postmortem)
                              |
                              v
                          [CLOSED]
```

## Transitions

| From Stage | To Stage | Trigger / Condition | Concrete Example |
| --- | --- | --- | --- |
| `Plan` | `Implement` | Plan approved/completed | Agent creates `plans/add_auth.md`, worklog initialized, chains to `implement`. |
| `Implement` | `Test` | Code written & compiled | Agent finishes `auth.py`, triggers `test` skill. |
| `Test` | `Implement` | Tests fail | `test` skill finds failing `test_auth.py`, increments attempt, chains back to `implement`. |
| `Test` | `Review` | Tests pass | All tests green, agent triggers `review` skill. |
| `Test` | `Debug` | Root cause unclear | Repeated failures with no clear fix; invoke `debug` before next `implement`. |
| `Review` | `Implement` | Linter/Style fails | `flake8` fails, agent logs failure, chains back to `implement`. |
| `Review` | `Merge` | Final approval | Clean code, all acceptance criteria met. |
| `Merge` | `Postmortem` | Pushed to remote | Commit on `main`, worklog marked `merged`. |
| `Postmortem` | `Closed` | Retrospective written | `postmortem.md` and `ROLLUP.md` updated. |
| *Any* | `Escalate` | Max retries reached | 3 failed test cycles; status set to `ESCALATED`, postmortem still required. |

*Note: The `research` skill can optionally precede `implement` when the codebase or API is unfamiliar. The `debug` skill can be invoked when test failures are non-trivial and the root cause is unclear.*

## Worklog & Branch Conventions

Derived from the [Initialize Repository postmortem](worklogs/main/postmortem.md):

1. **Create branch first**, then worklog:
   ```bash
   git checkout -b feature/add-auth
   bash .agentflow/skills/plan/scripts/new_worklog.sh --title "Add Auth" ...
   ```
2. **Slug mapping**: `feature/add-auth` → `worklogs/feature-add-auth/SUMMARY.md`
3. **Never rename** a branch after its worklog is created. If unavoidable, create a new worklog and archive the old one with a redirect note.
4. **Bootstrap tasks** (repo init only) may use `main` with `ALLOW_MAIN_BRANCH=1`.
5. **Terminal states** (`merged`, `abandoned`, `escalated`) must always run the `postmortem` skill.

## Testing Strategy

| Layer | When | Example |
| --- | --- | --- |
| Unit | Always | Mock `check_database_connection` in health tests |
| Integration | After schema/API contracts exist | Live Postgres tests in `tests/integration/` |
| Coverage gate | Review stage | Flag modules below 60% coverage for follow-up |

## Retry Limits

| Metric | Limit | Consequence of Exceeding |
| --- | --- | --- |
| `max_attempts_per_stage` | 3 | Task moves to `ESCALATED`. Human intervention required. |
| `max_workflow_steps` | 15 | Task moves to `ESCALATED`. Prevents infinite loops. |
| `max_parallel_tasks` | 4 | Additional tasks queue up until a slot is free. |

## How Chaining Works

AgentFlow orchestrates execution by reading the `chain_to` field in the frontmatter of each `SKILL.md` file.
When a skill completes successfully, the agent invokes the next skill in the chain.
If a skill fails, `chain_on_failure` overrides the success chain (e.g., `test` → `implement` on failure).

**Full success chain:**
`plan` → `implement` → `test` → `review` → `merge` → `postmortem`

## Parallel Dispatch

Agents can dispatch multiple independent tasks concurrently using the following YAML schema in their worklog or plan:

```yaml
dispatch:
  - task_id: T1
    skill: implement
    prompt: "Update frontend components"
    depends_on: []
  - task_id: T2
    skill: implement
    prompt: "Update backend API"
    depends_on: []
  - task_id: T3
    skill: test
    prompt: "Integration test T1 and T2"
    depends_on: [T1, T2]
```
*Usage Note*: Parallel dispatch is best for isolated sub-tasks (e.g., independent microservices). Shared state (like a single database schema file) should be handled serially.

## Dispatch Rules

1. Tasks with empty `depends_on` lists run immediately.
2. Dependent tasks block until all prerequisites hit `COMPLETED`.
3. If any prerequisite hits `ESCALATED` or `FAILED`, dependent tasks are marked `ABORTED`.

**Concrete Example:**
In a 3-task DAG, Task A (Database Schema) and Task B (Frontend UI) have no dependencies and run in parallel. Task C (API Integration) depends on `[A, B]`. Task C waits. If Task A fails and escalates, Task C is aborted immediately.

## DAG Resolution Algorithm

1. Scan all tasks in the dispatch block.
2. Identify tasks where `status == PENDING` and all `depends_on` tasks have `status == COMPLETED`.
3. Launch these tasks in parallel, up to `max_parallel_tasks`.
4. Monitor task execution. Upon completion, update task status in the worklog.
5. Loop back to step 1 until all tasks are `COMPLETED` or `ABORTED`/`ESCALATED`.

## Escalation

When a task exceeds its retry limits or encounters an unrecoverable error, the agent MUST explicitly escalate. The agent will:
1. Update the `Current Stage` in `worklogs/<slug>/SUMMARY.md` to `escalated`.
2. Write a clear summary of the blockage in the `What Was Done` section, including specific error messages, the failed skill, and what was attempted so far.
3. Run the `postmortem` skill to capture lessons even on failure.
4. Stop execution and notify the user via the chat interface.
