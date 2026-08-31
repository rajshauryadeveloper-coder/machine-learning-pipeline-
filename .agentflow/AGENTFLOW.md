---
type: entrypoint
status: active
created: 2026-08-31T16:23:00Z
---

# AgentFlow Catalog & Entrypoint

*The central directory of all agent behaviors, context, and conventions for this repository.*

## Quick-Start

To kick off an agentic workflow:
1. **Read Context**: Review `AGENT_CONTEXT.md` to understand the project architecture.
2. **Understand Workflow**: Review `WORKFLOW.md` to see the permitted state transitions.
3. **Pick a Prompt**: Select or write a prompt in `prompts/` (e.g., `prompts/add_auth.md`).
4. **Run a Skill**: Execute the initial skill to start the chain.
   ```bash
   agy run .agentflow/skills/plan/SKILL.md --prompt=.agentflow/prompts/add_auth.md
   ```
5. **Monitor**: Watch the agent create a worklog and progress through the chained skills until the objective is met.

## Directory Layout

```text
.agentflow/
├── skills/
│   ├── plan/        # Generates _TEMPLATE.md plans
│   ├── research/    # Explores unfamiliar codebase/API
│   ├── implement/   # Writes code and updates worklogs
│   ├── test/        # Runs tests and reports coverage
│   ├── debug/       # Investigates complex test failures
│   ├── review/      # Analyzes code for quality and style
│   ├── document/    # Updates inline docs and docs-generated/
│   └── postmortem/  # Logs learnings from task execution
├── plans/           # Where the plan skill outputs
├── prompts/         # Where users put task requests
├── worklogs/        # Where execution state is tracked
├── docs-generated/  # Where the document skill outputs
└── postmortems/     # Where the review skill logs outcomes
```

## Configuration

The workflow engine enforces strict limits to prevent runaway execution.

```yaml
limits:
  max_attempts_per_stage: 3      # Fails task if a single stage loops more than this
  max_total_workflow_steps: 15   # Hard cap on total skill transitions per task
  escalation_timeout_hours: 24   # How long to wait for human input on escalation
```

- **`max_attempts_per_stage`**: If the test skill fails 3 times and kicks back to implement, the task escalates to a human on the 4th failure.
- **`max_total_workflow_steps`**: Prevents infinite ping-pong between `implement` -> `test` -> `implement` -> `review` across the entire lifecycle.
- **`escalation_timeout_hours`**: Ensures stalled tasks are eventually purged or reviewed.

## Skill Catalog

| Skill | Trigger | Next (chain_to) | Scripts Folder |
| --- | --- | --- | --- |
| `plan` | Manual (`agy run`) | `skills/implement/SKILL.md` | `skills/plan/scripts/` |
| `research` | Before implementation when unfamiliar | `skills/implement/SKILL.md` | `skills/research/scripts/` |
| `implement` | Triggered by `plan` or `research` | `skills/test/SKILL.md` | `skills/implement/scripts/` |
| `test` | Triggered by `implement` | `skills/review/SKILL.md` | `skills/test/scripts/` |
| `debug` | When tests fail and root cause unclear | `skills/implement/SKILL.md` | `skills/debug/scripts/` |
| `review` | Triggered by `test` | `None` (Merge/Escalate) | `skills/review/scripts/` |
| `document` | Optional side-chain | `None` | `skills/document/scripts/` |

## Conventions

- **File Granularity**: One file per concept. Do not merge plans, prompts, and worklogs into a single mega-file.
- **Frontmatter**: Every markdown file in `.agentflow/` must begin with YAML frontmatter containing at least `type`, `status`, and `created`.
- **Attempt Naming**: When skills create artifacts, suffix them with the attempt number (e.g., `coverage_report_v2.md`).
- **Progressive Disclosure**: High-level summaries belong in `WORKLOG.md`. Detailed trace logs belong in `worklogs/attempts/`.

## Adding New Skills

1. **Create the Folder**: `mkdir -p .agentflow/skills/<new_skill>/scripts/` (Scripts can be `.sh` OR `.py` based on preference).
2. **Define the Skill**: Create `.agentflow/skills/<new_skill>/SKILL.md`. Fill out the frontmatter, including `chain_to` if it should trigger another skill automatically.
3. **Register**: Add a row to the Skill Catalog table in this file (`AGENTFLOW.md`).
