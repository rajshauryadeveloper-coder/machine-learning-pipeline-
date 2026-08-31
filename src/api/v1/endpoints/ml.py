"""FastAPI endpoints for Machine Learning Analytics & Inference."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.ml.experiments import run_all_experiments
from src.ml.models import get_model_manager
from src.ml.report import generate_markdown_report, generate_summary_dict
from src.schemas.ml import (
    ChurnPredictRequest,
    ChurnPredictResponse,
    CLVPredictRequest,
    CLVPredictResponse,
    DemandPredictRequest,
    DemandPredictResponse,
    MLCasesResponse,
    MLCaseSummary,
    MLReportResponse,
    MLTrainResponse,
    OrderStatusPredictRequest,
    OrderStatusPredictResponse,
    RecommendationPredictRequest,
    RecommendationPredictResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning & Analytics"])


@router.get(
    "/cases",
    response_model=MLCasesResponse,
    summary="List the 5 ML business cases",
    description="Retrieve metadata for all 5 ML analytics cases.",
)
def get_ml_cases() -> dict[str, Any]:
    cases = [
        MLCaseSummary(
            id="clv_prediction",
            title="Customer Lifetime Value & VIP Tier Prediction",
            category="Revenue Optimization & Segmentation",
            target="total_spend (Regression) & is_vip (Classification)",
            primary_metric="R2 Score, RMSE, F1-Score",
            description=(
                "Predict prospective customer spending and classify "
                "high-value VIP accounts."
            ),
        ),
        MLCaseSummary(
            id="demand_forecasting",
            title="Product Demand & Inventory Depletion Velocity",
            category="Supply Chain & Procurement",
            target="units_sold (Regression) & depletion_risk (Classification)",
            primary_metric="R2 Score, RMSE, Accuracy",
            description=(
                "Forecast catalog unit sales demand and identify "
                "immediate restock priorities."
            ),
        ),
        MLCaseSummary(
            id="order_status_risk",
            title="Order Fulfillment & Delivery Delay Risk",
            category="Operations & Logistics",
            target="is_delayed (Binary Classification)",
            primary_metric="F1-Score, Precision, ROC-AUC",
            description=(
                "Predict probability of order processing delay to prevent "
                "logistics bottlenecks."
            ),
        ),
        MLCaseSummary(
            id="churn_prediction",
            title="Customer Churn & Inactivity Prediction",
            category="Customer Retention",
            target="is_churned (Binary Classification)",
            primary_metric="F1-Score, ROC-AUC, Recall",
            description=(
                "Identify accounts at risk of churning to automate targeted "
                "re-engagement campaigns."
            ),
        ),
        MLCaseSummary(
            id="product_recommendation",
            title="Cross-Sell & Basket Affinity Recommendation",
            category="Personalization & Merchandising",
            target="Product Affinity Score & Next-Best Item Ranking",
            primary_metric="Precision@k, Cosine Affinity",
            description=(
                "Generate personalized product recommendations via hybrid "
                "collaborative and content scoring."
            ),
        ),
    ]
    return {"total_cases": len(cases), "cases": cases}


@router.get(
    "/experiments",
    summary="Run and retrieve all ML model experiment benchmarks",
    description=(
        "Execute full battery of standalone and hybrid scikit-learn "
        "experiments across the 5 business cases."
    ),
)
def get_ml_experiments() -> dict[str, Any]:
    try:
        return run_all_experiments()
    except Exception as e:
        logger.error("Error executing ML experiments: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Experiment battery execution failed: {str(e)}",
        )


@router.get(
    "/report",
    response_model=MLReportResponse,
    summary="Get comprehensive ML evaluation report",
    description=(
        "Generate complete Markdown & JSON report highlighting best "
        "configurations and comparison tables."
    ),
)
def get_ml_report() -> dict[str, Any]:
    try:
        md = generate_markdown_report()
        summary = generate_summary_dict()
        return {"markdown_report": md, "summary": summary}
    except Exception as e:
        logger.error("Error generating report: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}",
        )


@router.post(
    "/train",
    response_model=MLTrainResponse,
    summary="Retrain all production ML pipelines",
    description=(
        "Trigger fresh model training on the latest PostgreSQL " "database records."
    ),
)
def train_models() -> dict[str, Any]:
    try:
        manager = get_model_manager()
        results = manager.train_all()
        return {
            "status": "success",
            "message": (
                "All 5 ML pipelines retrained successfully on latest "
                "database records."
            ),
            "trained_models": results,
        }
    except Exception as e:
        logger.error("Error retraining ML models: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model retraining failed: {str(e)}",
        )


@router.post(
    "/predict/clv",
    response_model=CLVPredictResponse,
    summary="Predict Customer Lifetime Value & VIP Status",
    description="Inference for Business Case 1.",
)
def predict_clv(payload: CLVPredictRequest) -> dict[str, Any]:
    try:
        manager = get_model_manager()
        return manager.predict_clv(
            order_count=payload.order_count,
            avg_order_value=payload.avg_order_value,
            total_items_purchased=payload.total_items_purchased,
            avg_item_price=payload.avg_item_price,
            total_discount_received=payload.total_discount_received,
            days_since_first_order=payload.days_since_first_order,
        )
    except Exception as e:
        logger.error("CLV prediction error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CLV inference failed: {str(e)}",
        )


@router.post(
    "/predict/demand",
    response_model=DemandPredictResponse,
    summary="Predict Product Demand & Depletion Risk",
    description="Inference for Business Case 2.",
)
def predict_demand(payload: DemandPredictRequest) -> dict[str, Any]:
    try:
        manager = get_model_manager()
        return manager.predict_demand(
            category_id=payload.category_id,
            price=payload.price,
            stock_quantity=payload.stock_quantity,
            rating=payload.rating,
            order_frequency=payload.order_frequency,
            avg_discount=payload.avg_discount,
        )
    except Exception as e:
        logger.error("Demand prediction error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Demand inference failed: {str(e)}",
        )


@router.post(
    "/predict/order-status",
    response_model=OrderStatusPredictResponse,
    summary="Predict Order Fulfillment Delay Risk",
    description="Inference for Business Case 3.",
)
def predict_order_status(payload: OrderStatusPredictRequest) -> dict[str, Any]:
    try:
        manager = get_model_manager()
        return manager.predict_order_status(
            total_amount=payload.total_amount,
            item_count=payload.item_count,
            payment_method=payload.payment_method,
            city=payload.city,
            discount_amount=payload.discount_amount,
            days_elapsed=payload.days_elapsed,
        )
    except Exception as e:
        logger.error("Order status prediction error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order status inference failed: {str(e)}",
        )


@router.post(
    "/predict/churn",
    response_model=ChurnPredictResponse,
    summary="Predict Customer Churn Probability",
    description="Inference for Business Case 4.",
)
def predict_churn(payload: ChurnPredictRequest) -> dict[str, Any]:
    try:
        manager = get_model_manager()
        return manager.predict_churn(
            days_since_last_order=payload.days_since_last_order,
            order_count=payload.order_count,
            days_since_signup=payload.days_since_signup,
            total_spend=payload.total_spend,
            avg_days_between_orders=payload.avg_days_between_orders,
            distinct_categories_count=payload.distinct_categories_count,
        )
    except Exception as e:
        logger.error("Churn prediction error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Churn inference failed: {str(e)}",
        )


@router.post(
    "/predict/recommend",
    response_model=RecommendationPredictResponse,
    summary="Predict Top-K Product Recommendations",
    description="Inference for Business Case 5.",
)
def predict_recommendations(
    payload: RecommendationPredictRequest,
) -> dict[str, Any]:
    try:
        manager = get_model_manager()
        return manager.predict_recommendations(
            customer_id=payload.customer_id,
            top_k=payload.top_k,
        )
    except Exception as e:
        logger.error("Recommendation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recommendation inference failed: {str(e)}",
        )
