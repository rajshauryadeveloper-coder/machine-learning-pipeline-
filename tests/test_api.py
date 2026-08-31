import pytest
from fastapi.testclient import TestClient

from src.database import check_database_connection
from src.db.seed import seed_database
from src.main import app

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if not check_database_connection():
        pytest.skip("PostgreSQL database is not available for integration testing.")
    seed_database(reset=True)


def test_list_categories():
    response = client.get("/api/v1/categories?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["items"][0]["name"] == "Consumer Electronics"


def test_get_single_category():
    response = client.get("/api/v1/categories/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data

    # 404 test
    not_found = client.get("/api/v1/categories/9999")
    assert not_found.status_code == 404


def test_list_customers():
    response = client.get("/api/v1/customers?page=1&page_size=15")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 40
    assert len(data["items"]) == 15
    assert "email" in data["items"][0]


def test_get_customer_and_orders():
    response = client.get("/api/v1/customers/1")
    assert response.status_code == 200
    customer = response.json()
    assert customer["id"] == 1

    orders_res = client.get("/api/v1/customers/1/orders")
    assert orders_res.status_code == 200
    orders = orders_res.json()
    assert isinstance(orders, list)

    not_found = client.get("/api/v1/customers/9999")
    assert not_found.status_code == 404


def test_list_products_with_filters():
    # Basic list
    res = client.get("/api/v1/products?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 30
    assert len(data["items"]) == 10

    # Search filter
    search_res = client.get("/api/v1/products?search=Headphones")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total"] >= 1
    assert "Headphones" in search_data["items"][0]["name"]

    # Price range filter
    price_res = client.get("/api/v1/products?min_price=100&max_price=300")
    assert price_res.status_code == 200
    for p in price_res.json()["items"]:
        assert float(p["price"]) >= 100.0
        assert float(p["price"]) <= 300.0


def test_get_single_product():
    res = client.get("/api/v1/products/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert "sku" in data

    not_found = client.get("/api/v1/products/9999")
    assert not_found.status_code == 404


def test_list_orders():
    res = client.get("/api/v1/orders?page=1&page_size=20")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 60
    assert len(data["items"]) == 20
    assert "customer_name" in data["items"][0]
    assert "items" in data["items"][0]


def test_get_single_order():
    res = client.get("/api/v1/orders/1")
    assert res.status_code == 200
    order = res.json()
    assert order["id"] == 1
    assert len(order["items"]) >= 2
    assert "subtotal" in order["items"][0]

    not_found = client.get("/api/v1/orders/9999")
    assert not_found.status_code == 404


def test_list_order_items_largest_table():
    res = client.get("/api/v1/order-items?page=1&page_size=50")
    assert res.status_code == 200
    data = res.json()
    assert (
        data["total"] == 200
    ), "Largest table (order_items) must contain exactly 200 records"
    assert len(data["items"]) == 50
    assert data["total_pages"] == 4

    # Single order item
    item_res = client.get("/api/v1/order-items/1")
    assert item_res.status_code == 200
    assert item_res.json()["id"] == 1

    not_found = client.get("/api/v1/order-items/9999")
    assert not_found.status_code == 404


def test_analytics_overview():
    res = client.get("/api/v1/analytics/overview")
    assert res.status_code == 200
    data = res.json()

    overview = data["overview"]
    assert overview["total_orders"] == 60
    assert overview["total_customers"] == 40
    assert overview["total_products"] == 30
    assert overview["total_order_items"] == 200
    assert float(overview["total_revenue"]) > 0

    assert len(data["top_products"]) == 5
    assert len(data["category_breakdown"]) == 10


def test_database_status():
    res = client.get("/api/v1/database/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["connected"] is True
    assert len(data["tables"]) == 5

    # Check largest table
    table_dict = {t["table_name"]: t for t in data["tables"]}
    assert table_dict["order_items"]["row_count"] == 200
    assert table_dict["order_items"]["column_count"] == 8
