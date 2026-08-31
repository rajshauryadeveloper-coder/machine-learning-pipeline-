import math
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from src.database import get_dict_connection
from src.schemas.models import CategoryOut, PaginatedResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "",
    response_model=PaginatedResponse[CategoryOut],
    summary="List product categories",
    description=(
        "Retrieve product categories with optional search and active status filter."
    ),
)
def list_categories(
    search: str | None = Query(None, description="Search category name or description"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    conditions: list[str] = []
    params: list[Any] = []

    if search:
        conditions.append("(name ILIKE %s OR description ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM categories {where_clause};",
                params,
            )
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            cur.execute(
                f"""
                SELECT id, name, slug, description, is_active, created_at
                FROM categories
                {where_clause}
                ORDER BY id ASC
                LIMIT %s OFFSET %s;
                """,
                params + [page_size, offset],
            )
            items = cur.fetchall()

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Get single category",
    description="Retrieve a single category by its unique identifier.",
)
def get_category(category_id: int) -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, slug, description, is_active, created_at
                FROM categories
                WHERE id = %s;
                """,
                (category_id,),
            )
            item = cur.fetchone()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found.",
        )
    return item
