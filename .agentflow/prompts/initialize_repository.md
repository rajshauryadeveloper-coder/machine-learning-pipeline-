---
type: prompt
status: completed
created: 2026-08-31T16:23:00Z
completed: 2026-08-31T17:41:00Z
tags: [initialize, scaffold]
---

# Initialize Repository

## Task
Initialize a workspace using the provided details and requirements in `AGENT_CONTEXT.md`.

## Requirements
- Python 3.11+ FastAPI backend in `src/`
- Static HTML frontend in `html/`
- Pytest test suite in `tests/`
- Developer documentation in `docs/`
- Dev scripts in `scripts/`
- Docker configuration at repository root
- uv for dependency management
- PostgreSQL configuration via environment variables

## Acceptance Criteria
- [x] Project structure matches `AGENT_CONTEXT.md` layout
- [x] `uv sync` installs all dependencies
- [x] Health endpoint available at `/health`
- [x] Static frontend served at `/`
- [x] Tests pass with pytest
- [x] Lint and format checks pass
- [x] Committed and pushed to GitHub

## Outcome
Completed — see [worklog](../worklogs/main/SUMMARY.md) and [plan](../plans/20260831-initialize-repository.md).
