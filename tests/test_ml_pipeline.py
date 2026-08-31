"""Unit and integration tests for Machine Learning Pipeline, models, and experiments."""

from src.ml.datasets import (
    load_churn_dataset,
    load_clv_dataset,
    load_demand_dataset,
    load_order_status_dataset,
    load_recommendation_dataset,
)
from src.ml.experiments import (
    run_all_experiments,
    run_churn_experiments,
    run_clv_experiments,
    run_demand_experiments,
    run_order_status_experiments,
    run_recommendation_experiments,
)
from src.ml.models import MLModelManager
from src.ml.report import generate_markdown_report, generate_summary_dict


def test_clv_dataset_loading():
    """Verify CLV dataset extraction and feature integrity."""
    df, feature_cols = load_clv_dataset()
    assert not df.empty
    assert "total_spend" in df.columns
    assert "is_vip" in df.columns
    for col in feature_cols:
        assert col in df.columns
    assert len(df) >= 20


def test_demand_dataset_loading():
    """Verify product demand dataset extraction."""
    df, feature_cols = load_demand_dataset()
    assert not df.empty
    assert "units_sold" in df.columns
    assert "depletion_risk" in df.columns
    for col in feature_cols:
        assert col in df.columns
    assert len(df) >= 20


def test_order_status_dataset_loading():
    """Verify order status fulfillment dataset extraction."""
    df, feature_cols = load_order_status_dataset()
    assert not df.empty
    assert "is_delayed" in df.columns
    for col in feature_cols:
        assert col in df.columns
    assert len(df) >= 30


def test_churn_dataset_loading():
    """Verify customer churn dataset extraction."""
    df, feature_cols = load_churn_dataset()
    assert not df.empty
    assert "is_churned" in df.columns
    for col in feature_cols:
        assert col in df.columns
    assert len(df) >= 20


def test_recommendation_dataset_loading():
    """Verify product recommendation affinity dataset extraction."""
    df_matrix, product_metadata = load_recommendation_dataset()
    assert not df_matrix.empty
    assert len(product_metadata) > 0


def test_clv_experiments():
    """Test CLV model configurations and hybrid setup comparison."""
    results = run_clv_experiments()
    assert "regression" in results
    assert "classification" in results
    assert len(results["regression"]) >= 3
    assert len(results["classification"]) >= 3
    assert "best_regressor" in results
    assert "best_classifier" in results


def test_demand_experiments():
    """Test product demand forecasting experiments."""
    results = run_demand_experiments()
    assert "models" in results
    assert len(results["models"]) >= 3
    assert "best_model" in results
    assert results["best_model"]["r2_score"] is not None


def test_order_status_experiments():
    """Test order status delay risk experiments."""
    results = run_order_status_experiments()
    assert "models" in results
    assert len(results["models"]) >= 3
    assert "best_model" in results
    assert "f1_score" in results["best_model"]


def test_churn_experiments():
    """Test customer churn prediction experiments."""
    results = run_churn_experiments()
    assert "models" in results
    assert len(results["models"]) >= 3
    assert "best_model" in results
    assert "accuracy" in results["best_model"]


def test_recommendation_experiments():
    """Test cross-sell recommendation hybrid experiments."""
    results = run_recommendation_experiments()
    assert "models" in results
    assert len(results["models"]) >= 2
    assert "best_model" in results


def test_run_all_experiments():
    """Test running the full suite of experiments across 5 cases."""
    all_results = run_all_experiments()
    assert len(all_results) == 5
    assert "case_1_clv" in all_results
    assert "case_2_demand" in all_results
    assert "case_3_order_status" in all_results
    assert "case_4_churn" in all_results
    assert "case_5_recommendations" in all_results


def test_model_manager_training_and_inference():
    """Test MLModelManager lifecycle and prediction methods."""
    manager = MLModelManager()
    manager.train_all()
    assert manager.is_trained

    # Test Case 1: CLV
    clv_pred = manager.predict_clv(
        order_count=5,
        avg_order_value=120.50,
        total_items_purchased=12,
        avg_item_price=50.0,
        total_discount_received=15.0,
        days_since_first_order=60,
    )
    assert "predicted_spend" in clv_pred
    assert "is_vip" in clv_pred
    assert "vip_probability" in clv_pred
    assert clv_pred["predicted_spend"] >= 0

    # Test Case 2: Demand
    demand_pred = manager.predict_demand(
        category_id=1,
        price=199.99,
        stock_quantity=50,
        rating=4.8,
        order_frequency=10,
        avg_discount=5.0,
    )
    assert "predicted_units_sold" in demand_pred
    assert "depletion_risk" in demand_pred
    assert demand_pred["predicted_units_sold"] >= 0

    # Test Case 3: Order Status
    order_pred = manager.predict_order_status(
        total_amount=250.0,
        item_count=3,
        payment_method="credit_card",
        city="San Francisco",
        discount_amount=10.0,
        days_elapsed=2,
    )
    assert "delay_probability" in order_pred
    assert "predicted_status" in order_pred

    # Test Case 4: Churn
    churn_pred = manager.predict_churn(
        days_since_last_order=45,
        order_count=2,
        days_since_signup=100,
        total_spend=150.0,
        avg_days_between_orders=30,
        distinct_categories_count=2,
    )
    assert "churn_probability" in churn_pred
    assert "churn_risk_tier" in churn_pred

    # Test Case 5: Recommendation
    rec_pred = manager.predict_recommendations(
        customer_id=1,
        top_k=3,
    )
    assert "recommendations" in rec_pred
    assert len(rec_pred["recommendations"]) <= 3


def test_report_generation():
    """Verify markdown and summary generation for ML report."""
    md_report = generate_markdown_report()
    assert "# Machine Learning Analytics Experiment Report" in md_report
    assert "Business Case 1" in md_report
    assert "Business Case 5" in md_report

    summary = generate_summary_dict()
    assert "total_business_cases" in summary
    assert summary["total_business_cases"] == 5
    assert len(summary["cases"]) == 5
