---
type: prompt
status: in_progress
created: 2026-08-31T18:25:00Z
tags: [workflow, agentflow, optimization, speed, tokens, refactor]
---

# Optimize AgentFlow Workflow for Speed and Token Efficiency

## Task
Based upon the postmortems of all work logs and artifacts, examine the friction points and failure modes encountered during agent execution.
Modify the skills, agent workflow, and tooling to optimize for execution speed and token efficiency:
1. Merge redundant skills (`test` + `review` -> `verify`, `merge` + `postmortem` + `document` -> `ship`) to reduce state-machine ping-pong and token overhead.
2. Build an automated, robust Python workflow CLI (`flow.py`) to eliminate brittle shell scripts and manual markdown artifact boilerplate.
3. Fix path resolution errors and worklog slug derivation permanently.
4. Update `AGENTFLOW.md`, `WORKFLOW.md`, and `AGENT_CONTEXT.md` to document the streamlined 4-stage pipeline (Plan → Implement → Verify → Ship).
5. Verify with automated tests and quality checks.

## Acceptance Criteria
- [ ] Implement `.agentflow/scripts/flow.py` supporting `start`, `verify`, `ship`, `status`, and `digest`.
- [ ] Create streamlined `verify` and `ship` skills and deprecate redundant skills (`test`, `review`, `merge`, `postmortem`).
- [ ] Update `AGENTFLOW.md`, `WORKFLOW.md`, and `AGENT_CONTEXT.md` with new stage diagrams, command catalog, and performance metrics.
- [ ] Ensure all existing codebase tests and lint checks pass cleanly with 100% success rate.
- [ ] Add tests for `flow.py` ensuring automated workflow commands work reliably.
