"""Data extraction and feature engineering pipelines for the 5 ML business cases."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from src.database import get_dict_connection

logger = logging.getLogger(__name__)


def load_clv_dataset() -> tuple[pd.DataFrame, list[str]]:
    """Extract and engineer features for Customer Lifetime Value & VIP Tier.

    Business Case 1:
    - Target (Regression): total_spend (Float)
    - Target (Classification): is_vip (0 or 1, spend >= $500)
    - Features: order_count, avg_order_value, total_items_purchased,
      avg_item_price, total_discount_received, days_since_first_order
    """
    feature_cols = [
        "order_count",
        "avg_order_value",
        "total_items_purchased",
        "avg_item_price",
        "total_discount_received",
        "days_since_first_order",
    ]

    query = """
    SELECT
        c.id AS customer_id,
        COALESCE(COUNT(DISTINCT o.id), 0) AS order_count,
        COALESCE(AVG(o.total_amount), 0.0) AS avg_order_value,
        COALESCE(SUM(oi.quantity), 0) AS total_items_purchased,
        COALESCE(AVG(oi.unit_price), 0.0) AS avg_item_price,
        COALESCE(SUM(oi.discount_amount), 0.0) AS total_discount_received,
        COALESCE(
            EXTRACT(DAY FROM (NOW() - MIN(o.ordered_at))), 30
        ) AS days_since_first_order,
        COALESCE(SUM(o.total_amount), 0.0) AS total_spend
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    LEFT JOIN order_items oi ON o.id = oi.order_id
    GROUP BY c.id;
    """
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    df = pd.DataFrame(rows)
    if df.empty:
        # Synthesize fallback data for cold start / offline test runs
        df = pd.DataFrame(
            {
                "customer_id": range(1, 41),
                "order_count": [random_val % 4 + 1 for random_val in range(40)],
                "avg_order_value": [float(50 + (i * 12) % 200) for i in range(40)],
                "total_items_purchased": [(i % 5 + 1) * 2 for i in range(40)],
                "avg_item_price": [float(30 + (i * 7) % 150) for i in range(40)],
                "total_discount_received": [float((i % 4) * 10) for i in range(40)],
                "days_since_first_order": [float(20 + i * 2) for i in range(40)],
                "total_spend": [float(100 + i * 35) for i in range(40)],
            }
        )

    # Cast numeric columns
    for col in feature_cols + ["total_spend"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Define VIP classification threshold (Total spend >= 500 or 75th percentile)
    spend_threshold = 450.0
    df["is_vip"] = (df["total_spend"] >= spend_threshold).astype(int)

    return df, feature_cols


def load_demand_dataset() -> tuple[pd.DataFrame, list[str]]:
    """Extract and engineer features for Product Demand & Inventory Depletion.

    Business Case 2:
    - Target (Regression): units_sold (Integer)
    - Target (Classification): depletion_risk (0: Low, 1: Medium, 2: High)
    - Features: category_id, price, stock_quantity, rating,
      order_frequency, avg_discount
    """
    feature_cols = [
        "category_id",
        "price",
        "stock_quantity",
        "rating",
        "order_frequency",
        "avg_discount",
    ]

    query = """
    SELECT
        p.id AS product_id,
        COALESCE(p.category_id, 1) AS category_id,
        p.price,
        p.stock_quantity,
        p.rating,
        COALESCE(COUNT(DISTINCT oi.order_id), 0) AS order_frequency,
        COALESCE(AVG(oi.discount_amount), 0.0) AS avg_discount,
        COALESCE(SUM(oi.quantity), 0) AS units_sold
    FROM products p
    LEFT JOIN order_items oi ON p.id = oi.product_id
    GROUP BY p.id, p.category_id, p.price, p.stock_quantity, p.rating;
    """
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            {
                "product_id": range(1, 31),
                "category_id": [(i % 10) + 1 for i in range(30)],
                "price": [float(25 + i * 10) for i in range(30)],
                "stock_quantity": [50 + (i * 7) % 100 for i in range(30)],
                "rating": [4.0 + (i % 10) * 0.1 for i in range(30)],
                "order_frequency": [(i % 8) + 2 for i in range(30)],
                "avg_discount": [float(i % 5) for i in range(30)],
                "units_sold": [(i % 7 + 1) * 3 for i in range(30)],
            }
        )

    for col in feature_cols + ["units_sold"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Depletion risk calculation (Stock vs Sales velocity ratio)
    ratio = df["units_sold"] / (df["stock_quantity"] + 1)
    df["depletion_risk"] = pd.qcut(
        ratio.rank(method="first"), q=3, labels=[0, 1, 2]
    ).astype(int)

    return df, feature_cols


def load_order_status_dataset() -> tuple[pd.DataFrame, list[str]]:
    """Extract and engineer features for Order Fulfillment Status & Delay Risk.

    Business Case 3:
    - Target (Classification): is_delayed (0: Delivered/Completed, 1: Pending/Delayed)
    - Features: total_amount, item_count, payment_method_code,
      city_code, discount_amount, days_elapsed
    """
    feature_cols = [
        "total_amount",
        "item_count",
        "payment_method_code",
        "city_code",
        "discount_amount",
        "days_elapsed",
    ]

    query = """
    SELECT
        o.id AS order_id,
        o.order_status,
        o.total_amount,
        COALESCE(COUNT(oi.id), 1) AS item_count,
        o.payment_method,
        COALESCE(c.city, 'San Francisco') AS city,
        COALESCE(SUM(oi.discount_amount), 0.0) AS discount_amount,
        COALESCE(EXTRACT(DAY FROM (NOW() - o.ordered_at)), 1) AS days_elapsed
    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.id
    LEFT JOIN order_items oi ON o.id = oi.order_id
    GROUP BY
        o.id,
        o.order_status,
        o.total_amount,
        o.payment_method,
        c.city,
        o.ordered_at;
    """
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            {
                "order_id": range(1, 61),
                "order_status": [
                    "completed" if i % 2 == 0 else "pending" for i in range(60)
                ],
                "total_amount": [float(50 + i * 15) for i in range(60)],
                "item_count": [(i % 4) + 1 for i in range(60)],
                "payment_method": [
                    "credit_card" if i % 2 == 0 else "paypal" for i in range(60)
                ],
                "city": ["New York" if i % 2 == 0 else "Austin" for i in range(60)],
                "discount_amount": [float(i % 5) for i in range(60)],
                "days_elapsed": [float((i % 10) + 1) for i in range(60)],
            }
        )

    # Encode categorical features deterministically
    payment_map = {"credit_card": 0, "paypal": 1, "apple_pay": 2, "bank_transfer": 3}
    df["payment_method_code"] = (
        df["payment_method"].str.lower().map(payment_map).fillna(0).astype(int)
    )

    cities = sorted(df["city"].dropna().unique().tolist())
    city_map = {city: idx for idx, city in enumerate(cities)}
    df["city_code"] = df["city"].map(city_map).fillna(0).astype(int)

    for col in ["total_amount", "item_count", "discount_amount", "days_elapsed"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Target: 0 for completed, 1 for delayed/shipped/processing/pending
    df["is_delayed"] = (df["order_status"].str.lower() != "completed").astype(int)

    return df, feature_cols


def load_churn_dataset() -> tuple[pd.DataFrame, list[str]]:
    """Extract and engineer features for Customer Churn Risk Scoring.

    Business Case 4:
    - Target (Classification): is_churned (0: Active, 1: Churned/Inactive)
    - Features: days_since_last_order, order_count, days_since_signup,
      total_spend, avg_days_between_orders, distinct_categories_count
    """
    feature_cols = [
        "days_since_last_order",
        "order_count",
        "days_since_signup",
        "total_spend",
        "avg_days_between_orders",
        "distinct_categories_count",
    ]

    query = """
    SELECT
        c.id AS customer_id,
        COALESCE(
            EXTRACT(DAY FROM (NOW() - MAX(o.ordered_at))), 90
        ) AS days_since_last_order,
        COALESCE(COUNT(DISTINCT o.id), 0) AS order_count,
        COALESCE(
            EXTRACT(DAY FROM (NOW() - c.created_at)), 120
        ) AS days_since_signup,
        COALESCE(SUM(o.total_amount), 0.0) AS total_spend,
        COALESCE(COUNT(DISTINCT p.category_id), 0) AS distinct_categories_count
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    LEFT JOIN order_items oi ON o.id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.id
    GROUP BY c.id, c.created_at;
    """
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            {
                "customer_id": range(1, 41),
                "days_since_last_order": [float((i * 4) % 80) for i in range(40)],
                "order_count": [(i % 5) + 1 for i in range(40)],
                "days_since_signup": [float(60 + i * 2) for i in range(40)],
                "total_spend": [float(100 + i * 25) for i in range(40)],
                "distinct_categories_count": [(i % 4) + 1 for i in range(40)],
            }
        )

    for col in [
        "days_since_last_order",
        "order_count",
        "days_since_signup",
        "total_spend",
        "distinct_categories_count",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Derived feature: Average days between orders
    df["avg_days_between_orders"] = (
        df["days_since_signup"] / (df["order_count"] + 1)
    ).round(1)

    # Churn definition: No order in > 35 days and low cadence
    df["is_churned"] = (
        (df["days_since_last_order"] > 35.0) | (df["order_count"] <= 1)
    ).astype(int)

    return df, feature_cols


def load_recommendation_dataset() -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    """Extract Customer-Product interaction matrix and Product metadata.

    Business Case 5:
    - User-Item Matrix: Customer purchase count / weight per product
    - Product Metadata: product_id, name, category_id, price, rating
    """
    query_products = """
    SELECT
        p.id AS product_id,
        p.name,
        p.category_id,
        c.name AS category_name,
        p.price,
        p.rating
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    ORDER BY p.id;
    """

    query_interactions = """
    SELECT
        o.customer_id,
        oi.product_id,
        COALESCE(SUM(oi.quantity), 1) AS purchase_count
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    GROUP BY o.customer_id, oi.product_id;
    """

    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query_products)
            products = cur.fetchall()

            cur.execute(query_interactions)
            interactions = cur.fetchall()

    if not interactions:
        # Fallback synthetic interactions
        interactions = [
            {
                "customer_id": (i % 40) + 1,
                "product_id": (i % 30) + 1,
                "purchase_count": (i % 3) + 1,
            }
            for i in range(120)
        ]

    df_interactions = pd.DataFrame(interactions)
    # Pivot to user-item matrix
    user_item_matrix = df_interactions.pivot_table(
        index="customer_id",
        columns="product_id",
        values="purchase_count",
        fill_value=0,
    )

    # Ensure all 30 product columns exist
    product_ids = [p["product_id"] for p in products]
    for pid in product_ids:
        if pid not in user_item_matrix.columns:
            user_item_matrix[pid] = 0

    return user_item_matrix, products
