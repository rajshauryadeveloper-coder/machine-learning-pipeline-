from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.v1.router import api_router
from src.config import settings
from src.database import check_database_connection

HTML_DIR = Path(__file__).resolve().parent.parent / "html"

app = FastAPI(
    title=settings.app_name,
    description=(
        "Machine Learning Pipeline & eCommerce REST API with PostgreSQL backend"
    ),
    version="1.0.0",
    debug=settings.debug,
)

if HTML_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=HTML_DIR), name="static")

# Mount API v1 endpoints
app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": check_database_connection(),
    }


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(HTML_DIR / "index.html")
