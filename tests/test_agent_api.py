from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_agent_status_endpoint():
    response = client.get("/api/v1/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "tools" in data
    assert "model" in data
    assert "gemma" in data["model"].lower() or "gemini" in data["model"].lower()


def test_agent_schema_endpoint():
    response = client.get("/api/v1/agent/schema")
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert len(data["tables"]) >= 5


def test_agent_chat_safe_query():
    payload = {"query": "What is the total number of orders in the database?"}
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["is_safe"] is True
    assert "steps" in data
    assert "execution_time_ms" in data


def test_agent_chat_malicious_query_blocked():
    payload = {"query": "DROP TABLE categories; DELETE FROM customers;"}
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_safe"] is False
    assert (
        "refuse" in data["response"].lower()
        or "blocked" in data["response"].lower()
        or "safety" in data["response"].lower()
    )
    assert len(data["sql_queries"]) == 0


def test_agent_chat_empty_query():
    payload = {"query": "   "}
    response = client.post("/api/v1/agent/chat", json=payload)
    assert response.status_code == 422 or response.status_code == 400
