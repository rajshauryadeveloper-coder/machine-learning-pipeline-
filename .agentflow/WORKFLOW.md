---
type: workflow
status: active
created: 2026-08-31T16:23:00Z
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
                          [MERGE]                [ESCALATE]
```

## Transitions

| From Stage | To Stage | Trigger / Condition | Concrete Example |
| --- | --- | --- | --- |
| `Plan` | `Implement` | Plan approved/completed | Agent creates `plans/add_auth.md`, user approves, agent triggers `implement`. |
| `Implement` | `Test` | Code written & compiled | Agent finishes `auth.py`, runs `pytest`, triggers `test` skill for deep analysis. |
| `Test` | `Implement` | Tests fail | `test` skill finds failing `test_auth.py`, increments attempt in worklog, chains back to `implement`. |
| `Test` | `Review` | Tests pass | Coverage hits 90%, agent triggers `review` skill for style checks. |
| `Review` | `Implement` | Linter/Style fails | `flake8` fails, agent logs failure, chains back to `implement` to fix spacing. |
| `Review` | `Merge` | Final approval | Clean code, agent creates PR, marks state as `MERGING`. |
| *Any* | `Escalate` | Max retries reached | `implement` fails tests 3 times, agent sets status to `ESCALATED`. |

*Note: The `research` skill can optionally precede `implement` when the codebase or API is unfamiliar. The `debug` skill can be invoked when test failures are non-trivial and the root cause is unclear.*

## Retry Limits

| Metric | Limit | Consequence of Exceeding |
| --- | --- | --- |
| `max_attempts_per_stage` | 3 | Task moves to `ESCALATED`. Human intervention required to fix the logic flaw the agent cannot resolve. |
| `max_workflow_steps` | 15 | Task moves to `ESCALATED`. Prevents infinite loops. |
| `max_parallel_tasks` | 4 | Additional tasks queue up until a slot is free. |

## How Chaining Works

AgentFlow orchestrates execution by reading the `chain_to` field in the frontmatter of each `SKILL.md` file. 
When a skill completes its objective successfully, the agent looks at `chain_to` and automatically invokes the next skill.
For instance, if `skills/test/SKILL.md` has `chain_to: skills/review/SKILL.md`, passing the tests automatically triggers the review process. If the tests fail, the agent overrides the chain and invokes `skills/implement/SKILL.md` to fix the code, incrementing the attempt counter in the worklog.

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
1. Update the `Current Stage` in `WORKLOG.md` to `escalated`.
2. Write a clear summary of the blockage in the `What Was Done` section, including specific error messages, the failed skill, and what was attempted so far.
3. Stop execution and notify the user via the chat interface.
