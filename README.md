# Machine Learning Pipeline

Python FastAPI backend with a static HTML frontend, managed with [uv](https://docs.astral.sh/uv/).

## Quick Start

```bash
uv sync
cp .env.example .env
uv run uvicorn src.main:app --reload
```

Visit http://127.0.0.1:8000/ for the frontend and http://127.0.0.1:8000/health for the health check.

## Project Layout

| Path | Description |
| --- | --- |
| `src/` | Python application source |
| `html/` | Static frontend (HTML, CSS, JS inline) |
| `tests/` | Pytest test suite |
| `docs/` | Developer documentation |
| `scripts/` | Development automation |
| `.agentflow/` | Agent workflow scaffolding |

## Commands

| Task | Command |
| --- | --- |
| Install | `uv sync` |
| Run | `uv run uvicorn src.main:app --reload` |
| Test | `uv run pytest tests/ --cov=src` |
| Lint | `uv run flake8 src/ tests/ && uv run black --check src/ tests/` |

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api.md)
- [Architecture](docs/architecture.md)
- [AgentFlow Worklog](.agentflow/worklogs/main/SUMMARY.md)

## Repository

- **Remote**: https://github.com/rajshauryadeveloper-coder/machine-learning-pipeline-
- **Branch**: `main`
