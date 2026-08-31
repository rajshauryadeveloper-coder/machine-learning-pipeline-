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

The default `.env.example` uses local PostgreSQL with user `shaurya` and no password. Edit `.env` only if your local setup differs. Do not commit `.env` to version control.

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
| Password | (none — local trust auth) |

Create the database if it does not exist:

```bash
createdb -h 127.0.0.1 -U shaurya ecommerce_database
```

Verify connectivity:

```bash
psql -h 127.0.0.1 -U shaurya -d ecommerce_database -c "SELECT 1"
```

When the database is reachable, the `/health` endpoint returns `"database": true`.

## Docker

Build and run the container:

```bash
docker build -t machine-learning-pipeline .
docker run -p 8000:8000 --env-file .env machine-learning-pipeline
```

## Further Reading

- [API Reference](api.md)
