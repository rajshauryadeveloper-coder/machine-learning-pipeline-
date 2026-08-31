"""Integration tests for Machine Learning FastAPI endpoints."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_ml_cases():
    """Verify listing of all 5 ML business cases."""
    response = client.get("/api/v1/ml/cases")
    assert response.status_code == 200
    data = response.json()
    assert "cases" in data
    assert len(data["cases"]) == 5
    case_ids = [c["id"] for c in data["cases"]]
    assert "clv_prediction" in case_ids
    assert "demand_forecasting" in case_ids
    assert "order_status_risk" in case_ids
    assert "churn_prediction" in case_ids
    assert "product_recommendation" in case_ids


def test_get_ml_experiments():
    """Verify running and fetching experiment comparison benchmark."""
    response = client.get("/api/v1/ml/experiments")
    assert response.status_code == 200
    data = response.json()
    assert "case_1_clv" in data
    assert "case_2_demand" in data
    assert "case_3_order_status" in data
    assert "case_4_churn" in data
    assert "case_5_recommendations" in data


def test_get_ml_report():
    """Verify retrieval of ML experiment report."""
    response = client.get("/api/v1/ml/report")
    assert response.status_code == 200
    data = response.json()
    assert "markdown_report" in data
    assert "summary" in data
    assert len(data["markdown_report"]) > 100


def test_post_ml_train():
    """Verify triggering re-training of models."""
    response = client.post("/api/v1/ml/train")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "trained_models" in data
    assert len(data["trained_models"]) == 5


def test_predict_clv_endpoint():
    """Verify CLV prediction API."""
    payload = {
        "order_count": 4,
        "avg_order_value": 150.0,
        "total_items_purchased": 10,
        "avg_item_price": 60.0,
        "total_discount_received": 20.0,
        "days_since_first_order": 90,
    }
    response = client.post("/api/v1/ml/predict/clv", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_spend" in data
    assert "is_vip" in data
    assert "vip_probability" in data
    assert "model_used" in data


def test_predict_demand_endpoint():
    """Verify demand prediction API."""
    payload = {
        "category_id": 1,
        "price": 299.99,
        "stock_quantity": 85,
        "rating": 4.85,
        "order_frequency": 12,
        "avg_discount": 5.0,
    }
    response = client.post("/api/v1/ml/predict/demand", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_units_sold" in data
    assert "depletion_risk" in data
    assert "model_used" in data


def test_predict_order_status_endpoint():
    """Verify order status delay prediction API."""
    payload = {
        "total_amount": 349.0,
        "item_count": 2,
        "payment_method": "credit_card",
        "city": "San Francisco",
        "discount_amount": 15.0,
        "days_elapsed": 1,
    }
    response = client.post("/api/v1/ml/predict/order-status", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "delay_probability" in data
    assert "predicted_status" in data
    assert "risk_tier" in data


def test_predict_churn_endpoint():
    """Verify customer churn prediction API."""
    payload = {
        "days_since_last_order": 50,
        "order_count": 1,
        "days_since_signup": 120,
        "total_spend": 75.0,
        "avg_days_between_orders": 50,
        "distinct_categories_count": 1,
    }
    response = client.post("/api/v1/ml/predict/churn", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "churn_probability" in data
    assert "is_churn_risk" in data
    assert "churn_risk_tier" in data


def test_predict_recommend_endpoint():
    """Verify product recommendation API."""
    payload = {
        "customer_id": 1,
        "top_k": 4,
    }
    response = client.post("/api/v1/ml/predict/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "customer_id" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_predict_clv_validation_error():
    """Verify invalid input validation for CLV endpoint."""
    payload = {
        "order_count": -5,  # Invalid negative count
        "avg_order_value": -10.0,
        "total_items_purchased": 0,
        "avg_item_price": 0.0,
        "total_discount_received": 0.0,
        "days_since_first_order": 0,
    }
    response = client.post("/api/v1/ml/predict/clv", json=payload)
    assert response.status_code in (400, 422)
