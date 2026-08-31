from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok():
    with patch("src.main.check_database_connection", return_value=True):
        response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app"] == "Machine Learning Pipeline"
    assert payload["database"] is True


def test_health_endpoint_reports_database_unavailable():
    with patch("src.main.check_database_connection", return_value=False):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["database"] is False


def test_index_serves_html():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Machine Learning Pipeline" in response.text
