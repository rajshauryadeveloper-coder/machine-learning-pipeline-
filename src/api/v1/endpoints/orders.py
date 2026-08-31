import math
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from src.database import get_dict_connection
from src.schemas.models import OrderOut, PaginatedResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get(
    "",
    response_model=PaginatedResponse[OrderOut],
    summary="List customer orders",
    description=(
        "Retrieve orders with status filters, customer filters, "
        "payment filters, and pagination."
    ),
)
def list_orders(
    customer_id: int | None = Query(None, description="Filter by customer ID"),
    order_status: str | None = Query(
        None,
        description="Filter by order status (pending, processing, shipped, completed)",
    ),
    payment_method: str | None = Query(None, description="Filter by payment method"),
    sort_by: str = Query(
        "ordered_at",
        pattern="^(id|total_amount|ordered_at|order_status)$",
        description="Field to sort by",
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    conditions: list[str] = []
    params: list[Any] = []

    if customer_id is not None:
        conditions.append("o.customer_id = %s")
        params.append(customer_id)

    if order_status:
        conditions.append("o.order_status = %s")
        params.append(order_status.lower())

    if payment_method:
        conditions.append("o.payment_method = %s")
        params.append(payment_method.lower())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    allowed_sorts = {
        "id": "o.id",
        "total_amount": "o.total_amount",
        "ordered_at": "o.ordered_at",
        "order_status": "o.order_status",
    }
    sort_column = allowed_sorts.get(sort_by, "o.ordered_at")
    order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM orders o {where_clause};",
                params,
            )
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            cur.execute(
                f"""
                SELECT o.id, o.customer_id,
                       concat(c.first_name, ' ', c.last_name) AS customer_name,
                       c.email AS customer_email,
                       o.order_status, o.total_amount, o.shipping_address,
                       o.payment_method, o.tracking_number, o.ordered_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                {where_clause}
                ORDER BY {sort_column} {order_direction}
                LIMIT %s OFFSET %s;
                """,
                params + [page_size, offset],
            )
            orders = cur.fetchall()

            for order in orders:
                cur.execute(
                    """
                    SELECT oi.id, oi.order_id, oi.product_id,
                           p.name AS product_name, p.sku AS product_sku,
                           oi.quantity, oi.unit_price, oi.discount_amount,
                           oi.subtotal, oi.created_at
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.id
                    WHERE oi.order_id = %s
                    ORDER BY oi.id ASC;
                    """,
                    (order["id"],),
                )
                order["items"] = cur.fetchall()

    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return {
        "items": orders,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get(
    "/{order_id}",
    response_model=OrderOut,
    summary="Get single order with line items",
    description=(
        "Retrieve order details, customer contact info, and line items by " "order ID."
    ),
)
def get_order(order_id: int) -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.id, o.customer_id,
                       concat(c.first_name, ' ', c.last_name) AS customer_name,
                       c.email AS customer_email,
                       o.order_status, o.total_amount, o.shipping_address,
                       o.payment_method, o.tracking_number, o.ordered_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.id = %s;
                """,
                (order_id,),
            )
            order = cur.fetchone()

            if not order:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Order with ID {order_id} not found.",
                )

            cur.execute(
                """
                SELECT oi.id, oi.order_id, oi.product_id,
                       p.name AS product_name, p.sku AS product_sku,
                       oi.quantity, oi.unit_price, oi.discount_amount,
                       oi.subtotal, oi.created_at
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
                ORDER BY oi.id ASC;
                """,
                (order["id"],),
            )
            order["items"] = cur.fetchall()

    return order
