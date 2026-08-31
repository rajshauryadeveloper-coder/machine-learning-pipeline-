---
type: entrypoint
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T18:30:00Z
---

# AgentFlow Catalog & Entrypoint (v2 Optimized)

*The streamlined, high-speed directory of all agent behaviors, context, and conventions for this repository.*

## Quick-Start

To kick off an agentic workflow using the unified `flow` CLI:

1. **Pick or Write a Prompt**: Place task requirements in `prompts/<task_name>.md`.
2. **Start Task (Plan)**:
   ```bash
   ./scripts/flow start my-task \
     --title "My Task Title" \
     --prompt prompts/my_task.md \
     --plan plans/20260831-my-task.md
   ```
3. **Implement**: Write code and unit/integration tests in `src/` and `tests/`.
4. **Verify**: Run automated quality and verification gates in one command:
   ```bash
   ./scripts/flow verify
   ```
5. **Ship (Merge & Postmortem)**: Atomically commit, push, merge, and record learnings:
   ```bash
   ./scripts/flow ship \
     -m "feat(my-task): implement core functionality" \
     --lesson "Domain Architecture" \
     --details "Summary of key technical insight gained."
   ```

## Directory Layout

```text
.agentflow/
├── scripts/
│   ├── flow.py           # Unified workflow CLI engine (start, verify, ship, status)
│   └── worklog_path.sh   # Branch name → worklog slug helper
├── skills/
│   ├── plan/        # Initializes feature branches and worklog scaffolding
│   ├── implement/   # Writes business logic and tests
│   ├── verify/      # Runs tests, coverage gate (>=60%), flake8, black, diff
│   ├── ship/        # Commits, pushes, merges to main, logs postmortem & rollup
│   └── research/    # Explores unfamiliar codebase/API (optional)
├── plans/           # Implementation plans
├── prompts/         # Task requirements and prompts
├── worklogs/        # Branch execution tracking (<branch-slug>/SUMMARY.md)
└── postmortems/     # Cross-task learnings rollup (ROLLUP.md)
```

## Skill Catalog (v2 Streamlined)

| Skill | Trigger | Next (chain_to) | Command / Automation |
| --- | --- | --- | --- |
| **`plan`** | Manual (task start) | `implement` | `./scripts/flow start <slug>` |
| **`implement`** | Follows `plan` or `verify` retry | `verify` | Direct coding |
| **`verify`** | Follows `implement` | `ship` (or `implement` on fail) | `./scripts/flow verify` |
| **`ship`** | Follows `verify` pass | `None` (terminal) | `./scripts/flow ship` |
| **`research`** | Optional exploration | `implement` | Exploration notes |

## Key Conventions

- **Atomic Lifecycle**: The workflow is optimized to 4 core stages (`plan` → `implement` → `verify` → `ship`).
- **Single-Command Verification**: `flow verify` tests code with pytest, checks coverage threshold (60%), and enforces flake8 and black in a single pass.
- **Atomic Shipping**: `flow ship` handles feature commit, remote branch push, main merge, postmortem generation, and `ROLLUP.md` updates without manual roundtrips.
- **Worklog Slug**: Map git branch names to directory slugs by replacing `/` with `-` (e.g. `feature/add-auth` → `worklogs/feature-add-auth/`).
- **Terminal Rollup**: Every shipped task appends an entry to `.agentflow/postmortems/ROLLUP.md`.
