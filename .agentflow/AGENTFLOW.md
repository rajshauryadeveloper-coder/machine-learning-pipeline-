---
type: entrypoint
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-09-01T01:03:00Z
---

# AgentFlow Catalog & Entrypoint (v3 High-Speed & Subagent-Enabled)

*Ultra-streamlined, token-efficient agent workflow and conventions for this repository.*

## Quick-Start Lifecycle (4 Core Stages)

1. **Start Task & Snapshot Context**:
   ```bash
   ./scripts/flow start my-task --title "Task Title" --prompt prompts/my_task.md
   ./scripts/flow context   # Capture entire DB schema, routes, & ML state in 1 shot (~250 tokens)
   ```
2. **Implement (TDD + Subagent Delegation)**:
   - Write tests first in `tests/test_<feature>.py`.
   - Implement feature code in `src/`.
   - **Delegate parallel/noisy tasks to subagents** to stay in the **20–30% Context Smart Zone**.
3. **Verify (Fast-Fail Multi-Gate)**:
   ```bash
   ./scripts/flow verify   # Fast-fails lint/format in 0.2s, then runs Pytest + coverage (>=60%)
   ```
4. **Ship (Secret Shield + Commit + Push + Merge + Rollup)**:
   ```bash
   ./scripts/flow ship -m "feat(my-task): description" --lesson "Category" --details "Details"
   ```

## Directory Layout

```text
.agentflow/
├── scripts/
│   ├── flow.py           # Unified CLI (start, context, verify, ship, status)
│   └── worklog_path.sh   # Branch name → worklog slug helper
├── skills/
│   ├── plan/        # Task initiation & single-shot context snapshot
│   ├── implement/   # Code implementation & test-first development
│   ├── verify/      # Fast-fail linting + tests + coverage gate
│   ├── ship/        # Secret scan + commit, push, merge, postmortem & rollup
│   ├── subagents/   # Subagent orchestration, 20-30% smart zone & model tiering
│   └── research/    # Targeted exploration
├── plans/           # Implementation plans
├── prompts/         # Task requirements and prompts
├── worklogs/        # Branch execution tracking (<branch-slug>/SUMMARY.md)
└── postmortems/     # Cross-task learnings rollup (ROLLUP.md)
```

## Token-Saving & Subagent Optimizations

- **`flow context`**: Replaces 10+ exploratory tool calls with a single 250-token snapshot.
- **20–30% Context Smart Zone**: Keeps supervisor context under 300k tokens by delegating noisy file/doc exploration to subagents.
- **Dynamic Model Tiering**: Routes subagents to `flash_lite` (regex/scans), `flash` (code search/docs), or `pro` (architecture/math) based on task complexity.
- **Fast-Fail Linting**: Catches flake8/black issues in ~0.2s before long integration tests run.
- **Secret Safety Shield**: Automatically sanitizes prompt files and prevents GitHub push blocks.
