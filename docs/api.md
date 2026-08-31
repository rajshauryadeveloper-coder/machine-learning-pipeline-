# API Reference

Base URL (local): `http://127.0.0.1:8000`

Interactive docs are available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Endpoints

### `GET /`

Serves the static HTML landing page from `html/index.html`.

**Response:** `200 OK` — HTML document

---

### `GET /health`

Returns application and database health status.

**Response:** `200 OK`

```json
{
  "status": "ok",
  "app": "Machine Learning Pipeline",
  "database": true
}
```

| Field | Type | Description |
| --- | --- | --- |
| `status` | string | Always `"ok"` when the API is running |
| `app` | string | Application name from settings |
| `database` | boolean | `true` if PostgreSQL is reachable, `false` otherwise |

---

### `GET /static/*`

Serves static files from the `html/` directory when mounted.

## Configuration

Settings are loaded from environment variables (or `.env` file):

| Variable | Default | Description |
| --- | --- | --- |
| `APP_NAME` | `Machine Learning Pipeline` | Display name |
| `DEBUG` | `false` | Enable debug mode |
| `DB_HOST` | `127.0.0.1` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `ecommerce_database` | Database name |
| `DB_USER` | `shaurya` | Database user |
| `DB_PASSWORD` | (empty) | Database password |

See `.env.example` for the full template.
