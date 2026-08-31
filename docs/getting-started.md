# Getting Started

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- PostgreSQL running locally (optional for basic API startup)

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` with your local database credentials. Do not commit `.env` to version control.

## Run the Application

```bash
uv run uvicorn src.main:app --reload
```

Or use the helper script:

```bash
./scripts/dev.sh
```

- API docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Frontend: http://127.0.0.1:8000/

## Run Tests

```bash
uv run pytest tests/ --cov=src
```

## Lint and Format

```bash
uv run flake8 src/ tests/
uv run black --check src/ tests/
```

## Database

The application expects a local PostgreSQL instance:

| Setting | Default |
| --- | --- |
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `ecommerce_database` |
| User | `shaurya` |

Create the database if it does not exist:

```bash
createdb ecommerce_database
```
