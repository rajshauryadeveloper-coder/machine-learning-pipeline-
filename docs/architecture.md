---
type: documentation
status: active
created: 2026-08-31T17:41:00Z
---

# Project Architecture

## Overview

```
┌─────────────┐     HTTP      ┌──────────────────┐     SQL      ┌────────────┐
│  html/      │ ◄──────────── │  src/main.py     │ ───────────► │ PostgreSQL │
│  (browser)  │               │  (FastAPI)       │              │ (local)    │
└─────────────┘               └──────────────────┘              └────────────┘
                                      │
                                      ▼
                              ┌──────────────────┐
                              │  src/config.py   │
                              │  src/database.py │
                              └──────────────────┘
```

## Layers

| Layer | Path | Responsibility |
| --- | --- | --- |
| Frontend | `html/` | Static pages with inline CSS/JS |
| API | `src/main.py` | HTTP routes, request/response handling |
| Config | `src/config.py` | Environment-based settings via pydantic-settings |
| Data | `src/database.py` | PostgreSQL connection management |
| Tests | `tests/` | Unit tests with mocked database in health checks |

## Conventions

- No frontend build tooling (no npm, webpack, React).
- All Python dependencies managed via `uv` and `pyproject.toml`.
- Secrets loaded from environment variables, never committed.
- Agent workflows tracked in `.agentflow/worklogs/`.

## Initialization Status

Repository initialized on 2026-08-31. See [worklog](../.agentflow/worklogs/main/SUMMARY.md) for details.
