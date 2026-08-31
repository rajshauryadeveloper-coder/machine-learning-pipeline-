---
type: entrypoint
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T17:45:00Z
---

# AgentFlow Catalog & Entrypoint

*The central directory of all agent behaviors, context, and conventions for this repository.*

## Quick-Start

To kick off an agentic workflow:
1. **Read Context**: Review `AGENT_CONTEXT.md` to understand the project architecture.
2. **Understand Workflow**: Review `WORKFLOW.md` to see the permitted state transitions.
3. **Pick a Prompt**: Select or write a prompt in `prompts/` (e.g., `prompts/add_auth.md`).
4. **Create branch & worklog**: Run the plan skill to create a feature branch and worklog.
   ```bash
   git checkout -b feature/my-task
   bash .agentflow/skills/plan/scripts/new_worklog.sh \
     --title "My Task" \
     --prompt prompts/my_task.md \
     --plan plans/20260831-my-task.md
   ```
5. **Execute skills**: Progress through plan → implement → test → review → merge → postmortem.
6. **Monitor**: Watch the agent update `worklogs/<branch-slug>/SUMMARY.md` until the task is merged.

## Directory Layout

```text
.agentflow/
├── scripts/
│   └── worklog_path.sh   # Branch name → worklog slug helper
├── skills/
│   ├── plan/        # Creates plans and worklogs
│   ├── research/    # Explores unfamiliar codebase/API
│   ├── implement/   # Writes code and updates worklogs
│   ├── test/        # Runs tests and reports coverage
│   ├── debug/       # Investigates complex test failures
│   ├── review/      # Analyzes code for quality and style
│   ├── merge/       # Commits, pushes, and closes worklog
│   ├── document/    # Updates inline docs and docs-generated/
│   └── postmortem/  # Logs learnings after merge/escalation
├── plans/           # Where the plan skill outputs
├── prompts/         # Where users put task requests
├── worklogs/        # Where execution state is tracked (by branch slug)
├── docs-generated/  # Where the document skill outputs
└── postmortems/     # Cross-task learnings rollup
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
| `plan` | Manual (start of task) | `skills/implement/SKILL.md` | `skills/plan/scripts/` |
| `research` | Before implementation when unfamiliar | `skills/implement/SKILL.md` | `skills/research/scripts/` |
| `implement` | Triggered by `plan` or `research` | `skills/test/SKILL.md` | `skills/implement/scripts/` |
| `test` | Triggered by `implement` | `skills/review/SKILL.md` | `skills/test/scripts/` |
| `debug` | When tests fail and root cause unclear | `skills/implement/SKILL.md` | `skills/debug/scripts/` |
| `review` | Triggered by `test` | `skills/merge/SKILL.md` | `skills/review/scripts/` |
| `merge` | Triggered by `review` (approve) | `skills/postmortem/SKILL.md` | `skills/merge/scripts/` |
| `postmortem` | After merge, abandon, or escalate | `None` (terminal) | `skills/postmortem/scripts/` |
| `document` | Optional side-chain | `None` | `skills/document/scripts/` |

## Conventions

- **File Granularity**: One file per concept. Do not merge plans, prompts, and worklogs into a single mega-file.
- **Frontmatter**: Every markdown file in `.agentflow/` must begin with YAML frontmatter containing at least `type`, `status`, and `created`.
- **Attempt Naming**: When skills create artifacts, suffix them with the attempt number (e.g., `coverage_report_v2.md`).
- **Progressive Disclosure**: High-level summaries belong in `worklogs/<slug>/SUMMARY.md`. Detailed trace logs belong in `worklogs/<slug>/attempts/`.
- **Worklog Slug**: Map git branch names to directory slugs by replacing `/` with `-`. Example: `feature/add-auth` → `worklogs/feature-add-auth/`.
- **Branch Before Worklog**: Always create the feature branch before running `new_worklog.sh`. Never rename a branch after its worklog exists.
- **Bootstrap Exception**: Repository initialization may run on `main` with `ALLOW_MAIN_BRANCH=1`. All other tasks require a feature branch.
- **Test Strategy**: Mock external dependencies (database, APIs) in unit tests. Add integration tests when schema or live services are introduced.
- **Postmortem Required**: Every terminal outcome (merged, abandoned, escalated) must produce `worklogs/<slug>/postmortem.md` and a `ROLLUP.md` entry.

## Lessons Applied (from Initialize Repository postmortem)

| Lesson | Workflow Change |
| --- | --- |
| Orphaned worklog when branch renamed | `new_worklog.sh` derives slug from current branch; documented in plan skill |
| Low coverage on `database.py` | Test skill should flag modules below 60% coverage for integration test follow-up |
| Scaffold before features | Plan skill enforces plan approval before implement chains |

## Adding New Skills

1. **Create the Folder**: `mkdir -p .agentflow/skills/<new_skill>/scripts/` (Scripts can be `.sh` OR `.py` based on preference).
2. **Define the Skill**: Create `.agentflow/skills/<new_skill>/SKILL.md`. Fill out the frontmatter, including `chain_to` if it should trigger another skill automatically.
3. **Register**: Add a row to the Skill Catalog table in this file (`AGENTFLOW.md`).
