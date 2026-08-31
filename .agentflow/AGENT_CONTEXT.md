---
type: context
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T18:35:00Z
---

# Agent Context

## Project Overview

This is a web application with a Python backend and a static HTML frontend. The backend is responsible for application logic, APIs, data processing, and database interaction, while all frontend code is contained within standalone HTML files with their CSS and JavaScript included directly in those files.

**Status:** Relational 5-table schema implemented, seeded (200 records in largest table), and deployed to `origin/main`.

## Repository Layout

| Path | Role / Content |
| --- | --- |
| `src/` | Main Python application source code (FastAPI, database, schemas, API routers) |
| `html/` | Static frontend HTML files containing HTML, CSS, and JavaScript |
| `tests/` | Pytest unit and integration test suites |
| `docs/` | User and developer documentation |
| `scripts/` | Utility scripts, dev helpers, and `flow` CLI |
| `.agentflow/` | Agent scaffolding, worklogs, skills, and workflow configuration |

## Fast Workflow Commands (`flow` CLI)

* **Start Task (Plan)**: `./scripts/flow start <slug> --title "Title" --prompt prompts/<file>.md`
* **Verify (Tests + Lint + Black + Coverage)**: `./scripts/flow verify`
* **Ship (Commit + Push + Merge + Postmortem + Rollup)**: `./scripts/flow ship --lesson "<Cat>" --details "<Details>"`
* **Status**: `./scripts/flow status`

## Build & Test Commands

**Python / uv / Pytest**

* **Install**: `uv sync`
* **Run**: `uv run uvicorn src.main:app --reload`
* **Test**: `uv run pytest tests/ --cov=src`
* **Lint & Format**: `uv run flake8 src/ tests/ && uv run black --check src/ tests/`
* **Seed Database**: `uv run python -m src.db.seed` (or `./scripts/seed.sh`)

## Tech Stack

* **Backend Language**: Python 3.11+
* **Backend Framework**: FastAPI
* **Frontend**: Static HTML files with inline CSS and JavaScript
* **Package Manager**: uv
* **Project Configuration**: `pyproject.toml`
* **Test Runner**: Pytest
* **Database**: Local PostgreSQL (`127.0.0.1:5432`, `ecommerce_database`, user `shaurya`)

## Agent Working Rules

1. **No Silent Failures**: If a command fails, log the exact stderr and do not pretend it succeeded.
2. **Atomic Operations**: Use `./scripts/flow` commands for fast, token-efficient transitions.
3. **Verify Everything**: Always run `./scripts/flow verify` before shipping.
4. **Respect Existing Style**: Match the indentation, naming conventions, architecture, and docstring formats of surrounding code.
5. **Update Documentation**: If an API or core application behavior changes, update the relevant files in `docs/`.
6. **Limit Scope**: Only edit files necessary to complete the prompt. Do not perform unrelated refactoring.
7. **Frontend Structure**: Keep all frontend HTML, CSS, and JavaScript inside the designated HTML directory. Do not introduce Node.js, npm, React, or other frontend build tooling.
8. **Python Dependency Management**: Use `uv` for Python dependency management and execution.
9. **Secrets**: Do not hardcode database passwords, API keys, tokens, or other secrets into source code or committed configuration files.

## Workflow

Agent execution follows `.agentflow/AGENTFLOW.md` and `.agentflow/WORKFLOW.md`:
- Streamlined 4-stage pipeline: **Plan** → **Implement** → **Verify** → **Ship**
- All gates automated via `./scripts/flow` CLI
