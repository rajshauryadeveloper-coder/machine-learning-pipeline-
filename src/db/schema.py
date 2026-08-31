import logging
from typing import Any

import psycopg

from src.database import get_connection, get_dict_connection

logger = logging.getLogger(__name__)

# List of managed tables in dependency order
MANAGED_TABLES = [
    "order_items",
    "orders",
    "products",
    "customers",
    "categories",
]

DROP_TABLES_SQL = """
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
"""

CLEAR_SCHEMA_SQL = """
DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO PUBLIC;
"""

CREATE_SCHEMA_SQL = """
-- 1. Categories Table (6 columns)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. Customers Table (9 columns)
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(30),
    address VARCHAR(255),
    city VARCHAR(80),
    country VARCHAR(80) DEFAULT 'United States' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 3. Products Table (10 columns)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0 NOT NULL,
    rating NUMERIC(3, 2) DEFAULT 4.50 NOT NULL,
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 4. Orders Table (8 columns)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    order_status VARCHAR(30) DEFAULT 'completed' NOT NULL,
    total_amount NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    shipping_address VARCHAR(255) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100),
    ordered_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 5. Order Items Table (8 columns) - The largest table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER DEFAULT 1 NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    discount_amount NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
"""

TRUNCATE_TABLES_SQL = """
TRUNCATE TABLE order_items, orders, products, customers, categories
RESTART IDENTITY CASCADE;
"""


def clear_schema(conn: psycopg.Connection | None = None) -> None:
    """Clear and recreate the entire public schema."""
    if conn:
        with conn.cursor() as cur:
            cur.execute(CLEAR_SCHEMA_SQL)
        conn.commit()
    else:
        with get_connection() as c:
            with c.cursor() as cur:
                cur.execute(CLEAR_SCHEMA_SQL)
            c.commit()
    logger.info("Cleared public schema successfully.")


def drop_all_tables(conn: psycopg.Connection | None = None) -> None:
    """Drop all managed tables."""
    if conn:
        with conn.cursor() as cur:
            cur.execute(DROP_TABLES_SQL)
        conn.commit()
    else:
        with get_connection() as c:
            with c.cursor() as cur:
                cur.execute(DROP_TABLES_SQL)
            c.commit()
    logger.info("Dropped all managed tables successfully.")


def truncate_all_tables(conn: psycopg.Connection | None = None) -> None:
    """Truncate all managed tables."""
    if conn:
        with conn.cursor() as cur:
            cur.execute(TRUNCATE_TABLES_SQL)
        conn.commit()
    else:
        with get_connection() as c:
            with c.cursor() as cur:
                cur.execute(TRUNCATE_TABLES_SQL)
            c.commit()
    logger.info("Truncated all managed tables successfully.")


def create_schema(conn: psycopg.Connection | None = None) -> None:
    """Create all 5 tables, relationships, and indices."""
    if conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_SCHEMA_SQL)
        conn.commit()
    else:
        with get_connection() as c:
            with c.cursor() as cur:
                cur.execute(CREATE_SCHEMA_SQL)
            c.commit()
    logger.info("Created 5-table schema with indices successfully.")


def reset_schema(conn: psycopg.Connection | None = None) -> None:
    """Full database reset: clear schema and recreate 5 tables."""
    clear_schema(conn)
    create_schema(conn)
    logger.info("Reset database schema successfully.")


def get_table_metadata() -> list[dict[str, Any]]:
    """Retrieve metadata and row counts for all managed tables."""
    results = []
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            for table in reversed(MANAGED_TABLES):
                cur.execute(
                    """
                    SELECT count(*) as row_count
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                    """,
                    (table,),
                )
                exists = cur.fetchone()
                if not exists or exists["row_count"] == 0:
                    continue

                # Count rows
                cur.execute(f"SELECT COUNT(*) AS total_rows FROM {table};")
                count_res = cur.fetchone()
                total_rows = count_res["total_rows"] if count_res else 0

                # Count columns
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position;
                    """,
                    (table,),
                )
                columns = cur.fetchall()

                results.append(
                    {
                        "table_name": table,
                        "row_count": total_rows,
                        "column_count": len(columns),
                        "columns": columns,
                    }
                )
    return results
