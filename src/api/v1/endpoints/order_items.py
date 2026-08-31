import math
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from src.database import get_dict_connection
from src.schemas.models import OrderItemOut, PaginatedResponse

router = APIRouter(prefix="/order-items", tags=["Order Items"])


@router.get(
    "",
    response_model=PaginatedResponse[OrderItemOut],
    summary="List order items (Largest Table - 200 Records)",
    description=(
        "Query items from the largest table (order_items) with order or "
        "product filters and pagination."
    ),
)
def list_order_items(
    order_id: int | None = Query(None, description="Filter by order ID"),
    product_id: int | None = Query(None, description="Filter by product ID"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(25, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    conditions: list[str] = []
    params: list[Any] = []

    if order_id is not None:
        conditions.append("oi.order_id = %s")
        params.append(order_id)

    if product_id is not None:
        conditions.append("oi.product_id = %s")
        params.append(product_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM order_items oi {where_clause};",
                params,
            )
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            cur.execute(
                f"""
                SELECT oi.id, oi.order_id, oi.product_id,
                       p.name AS product_name, p.sku AS product_sku,
                       oi.quantity, oi.unit_price, oi.discount_amount,
                       oi.subtotal, oi.created_at
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                {where_clause}
                ORDER BY oi.id ASC
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
    "/{item_id}",
    response_model=OrderItemOut,
    summary="Get single order item",
    description="Retrieve a single order item by its ID.",
)
def get_order_item(item_id: int) -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT oi.id, oi.order_id, oi.product_id,
                       p.name AS product_name, p.sku AS product_sku,
                       oi.quantity, oi.unit_price, oi.discount_amount,
                       oi.subtotal, oi.created_at
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.id = %s;
                """,
                (item_id,),
            )
            item = cur.fetchone()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order item with ID {item_id} not found.",
        )
    return item
