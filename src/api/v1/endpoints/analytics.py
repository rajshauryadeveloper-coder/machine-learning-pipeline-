from decimal import Decimal
from typing import Any

from fastapi import APIRouter

from src.database import get_dict_connection
from src.schemas.models import AnalyticsOverview

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])


@router.get(
    "/overview",
    response_model=AnalyticsOverview,
    summary="Get business analytics and table metrics",
    description=(
        "Retrieve high-level KPIs including revenue, AOV, top-selling products, "
        "and category sales performance."
    ),
)
def get_analytics_overview() -> dict[str, Any]:
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            # 1. Overview KPIs
            cur.execute("""
                SELECT
                    COALESCE(SUM(total_amount), 0.00) AS total_revenue,
                    COUNT(id) AS total_orders,
                    COALESCE(AVG(total_amount), 0.00) AS average_order_value
                FROM orders;
                """)
            orders_summary = cur.fetchone() or {
                "total_revenue": Decimal("0.00"),
                "total_orders": 0,
                "average_order_value": Decimal("0.00"),
            }

            cur.execute("SELECT COUNT(*) AS total_customers FROM customers;")
            cust_row = cur.fetchone()
            total_customers = cust_row["total_customers"] if cust_row else 0

            cur.execute("SELECT COUNT(*) AS total_products FROM products;")
            prod_row = cur.fetchone()
            total_products = prod_row["total_products"] if prod_row else 0

            cur.execute("SELECT COUNT(*) AS total_order_items FROM order_items;")
            items_row = cur.fetchone()
            total_order_items = items_row["total_order_items"] if items_row else 0

            # 2. Top Products by units sold and revenue
            cur.execute("""
                SELECT
                    p.id AS product_id,
                    p.name,
                    p.sku,
                    COALESCE(SUM(oi.quantity), 0) AS units_sold,
                    COALESCE(SUM(oi.subtotal), 0.00) AS total_revenue
                FROM products p
                JOIN order_items oi ON p.id = oi.product_id
                GROUP BY p.id, p.name, p.sku
                ORDER BY total_revenue DESC
                LIMIT 5;
                """)
            top_products = cur.fetchall()

            # 3. Category Breakdown
            cur.execute("""
                SELECT
                    c.id AS category_id,
                    c.name AS category_name,
                    COUNT(DISTINCT p.id) AS product_count,
                    COALESCE(SUM(oi.quantity), 0) AS items_sold,
                    COALESCE(SUM(oi.subtotal), 0.00) AS total_revenue
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                LEFT JOIN order_items oi ON p.id = oi.product_id
                GROUP BY c.id, c.name
                ORDER BY total_revenue DESC;
                """)
            category_breakdown = cur.fetchall()

    return {
        "overview": {
            "total_revenue": orders_summary["total_revenue"],
            "total_orders": orders_summary["total_orders"],
            "total_customers": total_customers,
            "total_products": total_products,
            "total_order_items": total_order_items,
            "average_order_value": orders_summary["average_order_value"],
        },
        "top_products": top_products,
        "category_breakdown": category_breakdown,
    }
