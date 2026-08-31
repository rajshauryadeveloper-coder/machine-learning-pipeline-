import math
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from src.database import get_dict_connection
from src.schemas.models import PaginatedResponse, ProductOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=PaginatedResponse[ProductOut],
    summary="List and filter catalog products",
    description=(
        "Search and filter products by category, price bounds, availability, "
        "or keyword with sorting and pagination."
    ),
)
def list_products(
    search: str | None = Query(
        None, description="Search product name, SKU, or description"
    ),
    category_id: int | None = Query(None, description="Filter by category ID"),
    min_price: Decimal | None = Query(None, ge=0, description="Minimum price filter"),
    max_price: Decimal | None = Query(None, ge=0, description="Maximum price filter"),
    is_available: bool | None = Query(
        None, description="Filter by product availability"
    ),
    sort_by: str = Query(
        "id",
        pattern="^(id|price|rating|name|created_at)$",
        description="Field to sort by",
    ),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    conditions: list[str] = []
    params: list[Any] = []

    if search:
        conditions.append(
            "(p.name ILIKE %s OR p.sku ILIKE %s OR p.description ILIKE %s)"
        )
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if category_id is not None:
        conditions.append("p.category_id = %s")
        params.append(category_id)

    if min_price is not None:
        conditions.append("p.price >= %s")
        params.append(min_price)

    if max_price is not None:
        conditions.append("p.price <= %s")
        params.append(max_price)

    if is_available is not None:
        conditions.append("p.is_available = %s")
        params.append(is_available)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    allowed_sorts = {
        "id": "p.id",
        "price": "p.price",
        "rating": "p.rating",
        "name": "p.name",
        "created_at": "p.created_at",
    }
    sort_column = allowed_sorts.get(sort_by, "p.id")
    order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM products p {where_clause};",
                params,
            )
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            cur.execute(
                f"""
                SELECT p.id, p.category_id, c.name AS category_name,
                       p.name, p.sku, p.description, p.price,
                       p.stock_quantity, p.rating, p.is_available, p.created_at
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                {where_clause}
                ORDER BY {sort_column} {order_direction}
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
    "/{product_id}",
    response_model=ProductOut,
    summary="Get single product",
    description="Retrieve product details by product ID.",
)
def get_product(product_id: int) -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.category_id, c.name AS category_name,
                       p.name, p.sku, p.description, p.price,
                       p.stock_quantity, p.rating, p.is_available, p.created_at
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = %s;
                """,
                (product_id,),
            )
            item = cur.fetchone()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )
    return item
