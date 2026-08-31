from src.agent.tools import (
    compute_math,
    execute_sql_query,
    get_database_schema,
)


def test_get_database_schema():
    schema = get_database_schema()
    assert isinstance(schema, dict)
    assert "tables" in schema
    table_names = [t["table_name"] for t in schema["tables"]]
    for expected in ["categories", "customers", "products", "orders", "order_items"]:
        assert expected in table_names


def test_compute_math_basic():
    res = compute_math("100 * 1.2 + 50 / 2")
    assert res["success"] is True
    assert res["result"] == 145.0


def test_compute_math_aggregations():
    res = compute_math("sum([10, 20, 30, 40]) / len([10, 20, 30, 40])")
    assert res["success"] is True
    assert res["result"] == 25.0


def test_compute_math_disallows_dangerous_builtins():
    res = compute_math("__import__('os').system('ls')")
    assert res["success"] is False
    assert "error" in res


def test_execute_sql_query_valid_select():
    res = execute_sql_query("SELECT count(*) as count FROM products;")
    assert res["success"] is True
    assert "rows" in res
    assert len(res["rows"]) >= 1
    assert "count" in res["rows"][0]


def test_execute_sql_query_blocks_write_attempt():
    res = execute_sql_query("DROP TABLE products;")
    assert res["success"] is False
    assert "Disallowed SQL" in res["error"] or "Safety" in res["error"]


def test_execute_sql_query_handles_syntax_error():
    res = execute_sql_query("SELECT non_existing_col_xyz FROM fake_table_123;")
    assert res["success"] is False
    assert "error" in res
