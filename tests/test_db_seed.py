from decimal import Decimal

import pytest

from src.database import check_database_connection, get_dict_connection
from src.db.schema import (
    get_table_metadata,
    reset_schema,
    truncate_all_tables,
)
from src.db.seed import seed_database


@pytest.fixture(autouse=True)
def ensure_database_available():
    if not check_database_connection():
        pytest.skip("PostgreSQL is not available for integration testing.")


def test_schema_creation_and_column_counts():
    """Verify 5 tables exist with between 5 and 10 columns each."""
    reset_schema()
    metadata = get_table_metadata()

    assert len(metadata) == 5, f"Expected 5 tables, found {len(metadata)}"

    for table in metadata:
        tbl_name = table["table_name"]
        col_count = table["column_count"]
        assert (
            5 <= col_count <= 10
        ), f"Table '{tbl_name}' has {col_count} columns; expected 5 to 10."


def test_database_seeding_and_row_counts():
    """Verify seeding populates tables & seeds 200 records in largest table."""
    counts = seed_database(reset=True)

    assert counts["categories"] == 10
    assert counts["customers"] == 40
    assert counts["products"] == 30
    assert counts["orders"] == 60
    assert counts["order_items"] == 200

    metadata = get_table_metadata()
    table_map = {m["table_name"]: m["row_count"] for m in metadata}

    assert table_map["categories"] == 10
    assert table_map["customers"] == 40
    assert table_map["products"] == 30
    assert table_map["orders"] == 60
    assert table_map["order_items"] == 200

    # Ensure order_items is strictly the largest table
    for tbl, cnt in table_map.items():
        if tbl != "order_items":
            assert cnt < 200, f"Table {tbl} has {cnt}; order_items should be largest."


def test_order_totals_consistency():
    """Verify orders total_amount matches sum of item subtotals."""
    with get_dict_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.id, o.total_amount,
                       COALESCE(SUM(oi.subtotal), 0.00) AS calculated_sum
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY o.id, o.total_amount;
                """)
            rows = cur.fetchall()

            assert len(rows) == 60
            for r in rows:
                diff = abs(
                    Decimal(str(r["total_amount"])) - Decimal(str(r["calculated_sum"]))
                )
                assert diff < Decimal("0.01"), f"Order #{r['id']} total mismatch"


def test_truncate_all_tables():
    """Verify truncate_all_tables clears records while preserving schema."""
    truncate_all_tables()
    metadata = get_table_metadata()
    for m in metadata:
        assert m["row_count"] == 0, f"{m['table_name']} should be empty."

    # Re-seed for subsequent tests
    seed_database(reset=False)
