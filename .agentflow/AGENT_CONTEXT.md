---
type: context
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-08-31T17:41:00Z
---

# Agent Context

## Project Overview

This is a web application with a Python backend and a static HTML frontend. The backend is responsible for application logic, APIs, data processing, and database interaction, while all frontend code is contained within standalone HTML files with their CSS and JavaScript included directly in those files.

**Status:** Initialized and deployed to `origin/main` (commit `81deec2`).

## Repository Layout

| Path          | Role / Content                                                  |
| ------------- | --------------------------------------------------------------- |
| `src/`        | Main Python application source code                             |
| `html/`       | Static frontend HTML files containing HTML, CSS, and JavaScript |
| `tests/`      | Pytest unit and integration test suites                         |
| `docs/`       | User and developer documentation                                |
| `scripts/`    | Utility scripts and development automation                      |
| `.agentflow/` | Agent scaffolding, worklogs, skills, and workflow configuration |

## Build & Test Commands

**Python / uv / Pytest**

* **Install**: `uv sync`
* **Run**: `uv run uvicorn src.main:app --reload`
* **Test**: `uv run pytest tests/ --cov=src`
* **Lint**: `uv run flake8 src/ tests/ && uv run black --check src/ tests/`

**Project Initialization**

* **Initialize Python project**: `uv init` (completed)
* **Create `pyproject.toml`**: Managed through `uv` (completed)
* **Docker configuration**: `Dockerfile` is maintained at the repository root (completed)

## Git Setup

**Remote Configuration** (configured)

* **Remote**: `origin` → https://github.com/rajshauryadeveloper-coder/machine-learning-pipeline-.git
* **Default branch**: `main`
* **Latest init commit**: `81deec2`

## Tech Stack

* **Backend Language**: Python 3.11+
* **Backend Framework**: FastAPI
* **Frontend**: Static HTML files with inline CSS and JavaScript
* **Package Manager**: uv
* **Project Configuration**: `pyproject.toml`
* **Test Runner**: Pytest
* **Database**: Local PostgreSQL
* **Database Host**: `127.0.0.1`
* **Database Port**: `5432`
* **Database Name**: `ecommerce_database`
* **Database User**: `shaurya`
* **Database Password**: None (local trust auth)

## Agent Working Rules

1. **No Silent Failures**: If a command fails, log the exact stderr and do not pretend it succeeded.
2. **Atomic Commits**: Group logical changes together. Do not commit half-written functions.
3. **Test First**: Write or update tests before modifying core business logic.
4. **Respect Existing Style**: Match the indentation, naming conventions, architecture, and docstring formats of surrounding code.
5. **Update Documentation**: If an API or core application behavior changes, update the relevant files in `docs/`.
6. **Limit Scope**: Only edit files necessary to complete the prompt. Do not perform unrelated refactoring.
7. **Frontend Structure**: Keep all frontend HTML, CSS, and JavaScript inside the designated HTML directory. Do not introduce Node.js, npm, React, or other frontend build tooling.
8. **Python Dependency Management**: Use `uv` for Python dependency installation, environment management, project initialization, and execution.
9. **Database**: Use the local PostgreSQL server for application data. The database is available at `127.0.0.1:5432` using the configured `ecommerce_database` database.
10. **Database Activation**: The PostgreSQL server may be started or managed through terminal commands when required for development or testing.
11. **Secrets**: Do not hardcode database passwords, API keys, tokens, or other secrets into source code, documentation, or committed configuration files. Use environment variables or appropriate local configuration instead.

## External Dependencies

* PostgreSQL (Local Primary Data Store)
* No external frontend runtime or package manager
* Python dependencies managed through uv

## Active Worklog

Latest completed task: [Initialize Repository](worklogs/main/SUMMARY.md)
