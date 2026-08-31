import math
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from src.database import get_dict_connection
from src.schemas.models import CustomerOut, OrderOut, PaginatedResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get(
    "",
    response_model=PaginatedResponse[CustomerOut],
    summary="List customers",
    description=(
        "Retrieve customers with pagination and optional search by name, "
        "email, or city."
    ),
)
def list_customers(
    search: str | None = Query(None, description="Search by name, email, or city"),
    city: str | None = Query(None, description="Filter by city"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    conditions: list[str] = []
    params: list[Any] = []

    if search:
        conditions.append(
            "(first_name ILIKE %s OR last_name ILIKE %s "
            "OR email ILIKE %s OR city ILIKE %s)"
        )
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    if city:
        conditions.append("city ILIKE %s")
        params.append(f"%{city}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM customers {where_clause};",
                params,
            )
            count_row = cur.fetchone()
            total = count_row["total"] if count_row else 0

            cur.execute(
                f"""
                SELECT id, first_name, last_name, email, phone,
                       address, city, country, created_at
                FROM customers
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
    "/{customer_id}",
    response_model=CustomerOut,
    summary="Get single customer",
    description="Retrieve customer profile details by ID.",
)
def get_customer(customer_id: int) -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, first_name, last_name, email, phone,
                       address, city, country, created_at
                FROM customers
                WHERE id = %s;
                """,
                (customer_id,),
            )
            item = cur.fetchone()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found.",
        )
    return item


@router.get(
    "/{customer_id}/orders",
    response_model=list[OrderOut],
    summary="Get customer order history",
    description="Retrieve all orders placed by a specific customer.",
)
def get_customer_orders(customer_id: int) -> list[dict[str, Any]]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM customers WHERE id = %s;", (customer_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer with ID {customer_id} not found.",
                )

            cur.execute(
                """
                SELECT o.id, o.customer_id,
                       concat(c.first_name, ' ', c.last_name) AS customer_name,
                       c.email AS customer_email,
                       o.order_status, o.total_amount, o.shipping_address,
                       o.payment_method, o.tracking_number, o.ordered_at
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                WHERE o.customer_id = %s
                ORDER BY o.ordered_at DESC;
                """,
                (customer_id,),
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

    return orders
