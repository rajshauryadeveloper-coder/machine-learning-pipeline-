from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import check_database_connection

HTML_DIR = Path(__file__).resolve().parent.parent / "html"

app = FastAPI(title=settings.app_name, debug=settings.debug)

if HTML_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=HTML_DIR), name="static")


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": check_database_connection(),
    }


@app.get("/")
def index() -> FileResponse:
    return FileResponse(HTML_DIR / "index.html")
