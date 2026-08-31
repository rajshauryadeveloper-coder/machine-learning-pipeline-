---
type: plan
status: approved
created: 2026-08-31T17:32:00Z
tags: [initialize, scaffold]
---

# Plan: Initialize Repository Workspace

## Goal
Bootstrap a production-ready Python/FastAPI workspace with static HTML frontend, testing, documentation, and Docker support as defined in `AGENT_CONTEXT.md`.

## Context
The repository is empty except for `.agentflow/` scaffolding. A full project skeleton is required before feature development can begin. The stack is Python 3.11+, FastAPI, uv, pytest, PostgreSQL, and static HTML (no Node.js frontend tooling).

## Scope
**IS IN SCOPE:**
- Initialize `uv` project with `pyproject.toml` and core dependencies
- Create `src/` FastAPI application with health endpoint and database config
- Create `html/` static frontend landing page
- Create `tests/` with pytest suite and coverage config
- Create `docs/` with getting-started guide
- Create `scripts/` with dev helper scripts
- Add `Dockerfile` and `.env.example`
- Add root `.gitignore` and `README.md`
- Initialize git repository on `main` branch

**IS NOT IN SCOPE:**
- Full ecommerce feature implementation
- Database migrations or ORM models
- Authentication or business logic
- CI/CD pipeline configuration

## Implementation Steps
1. **Git & Branch Setup** — `git init`, create `feature/initialize-repository` branch
2. **Python Project** — `uv init`, add FastAPI, uvicorn, pytest, psycopg, pydantic-settings
3. **Backend** — `src/main.py`, `src/config.py`, `src/database.py`
4. **Frontend** — `html/index.html` with inline CSS/JS
5. **Tests** — `tests/test_main.py` for health endpoint
6. **Docs & Scripts** — `docs/getting-started.md`, `scripts/dev.sh`
7. **Container** — `Dockerfile` for production deployment
8. **Verify** — `uv run pytest`, flake8/black checks

## Files Touched

| Path | Change Type | Risk Level | Why |
| --- | --- | --- | --- |
| `pyproject.toml` | Add | Low | Project configuration |
| `src/main.py` | Add | Low | FastAPI entrypoint |
| `src/config.py` | Add | Low | Environment settings |
| `src/database.py` | Add | Medium | PostgreSQL connection helper |
| `html/index.html` | Add | Low | Static frontend |
| `tests/test_main.py` | Add | Low | Health endpoint tests |
| `docs/getting-started.md` | Add | Low | Developer documentation |
| `scripts/dev.sh` | Add | Low | Dev server helper |
| `Dockerfile` | Add | Low | Container config |
| `.env.example` | Add | Low | Env var template |
| `.gitignore` | Add | Low | Git exclusions |
| `README.md` | Add | Low | Project overview |

## Definition of Done
- [ ] All directories (`src/`, `html/`, `tests/`, `docs/`, `scripts/`) exist
- [ ] `uv sync` installs dependencies successfully
- [ ] `uv run pytest tests/ --cov=src` passes
- [ ] `uv run flake8` and `uv run black --check` pass
- [ ] FastAPI health endpoint responds at `/health`
- [ ] Static HTML page is served or documented
