import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.database import check_database_connection
from src.db.schema import get_table_metadata
from src.db.seed import seed_database
from src.schemas.models import DatabaseStatus, SeedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/database", tags=["Database Management"])


@router.get(
    "/status",
    response_model=DatabaseStatus,
    summary="Get database status and table metrics",
    description=(
        "Inspect database connectivity and view row counts and column schemas "
        "for all managed tables."
    ),
)
def get_db_status() -> dict[str, Any]:
    connected = check_database_connection()
    if not connected:
        return {
            "status": "disconnected",
            "connected": False,
            "tables": [],
        }

    try:
        tables = get_table_metadata()
        return {
            "status": "healthy",
            "connected": True,
            "tables": tables,
        }
    except Exception as e:
        logger.error(f"Error fetching database metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to inspect database: {str(e)}",
        )


@router.post(
    "/reset-and-seed",
    response_model=SeedResponse,
    summary="Reset database and re-seed tables",
    description=(
        "Drop all tables, recreate the 5-table schema, and insert 200 records "
        "into the largest table (order_items)."
    ),
)
def reset_and_seed_database() -> dict[str, Any]:
    try:
        counts = seed_database(reset=True)
        return {
            "message": (
                "Database successfully reset and seeded with 200 records "
                "in largest table."
            ),
            "counts": counts,
        }
    except Exception as e:
        logger.error(f"Error resetting and seeding database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset and seed failed: {str(e)}",
        )
