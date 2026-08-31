"""Pydantic schemas for Machine Learning endpoints, predictions, and reports."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Business Case 1: CLV Schemas
# ---------------------------------------------------------------------------
class CLVPredictRequest(BaseModel):
    order_count: int = Field(
        ..., ge=0, description="Total historical orders placed by customer"
    )
    avg_order_value: float = Field(
        ..., ge=0.0, description="Average monetary value per order ($)"
    )
    total_items_purchased: int = Field(
        ..., ge=0, description="Total number of items purchased"
    )
    avg_item_price: float = Field(
        ..., ge=0.0, description="Average unit price of items purchased ($)"
    )
    total_discount_received: float = Field(
        0.0, ge=0.0, description="Total discounts availed ($)"
    )
    days_since_first_order: int = Field(
        30, ge=0, description="Days elapsed since customer's first purchase"
    )


class CLVPredictResponse(BaseModel):
    predicted_spend: float = Field(
        ..., description="Predicted prospective lifetime expenditure ($)"
    )
    is_vip: bool = Field(..., description="Whether customer qualifies for VIP status")
    vip_probability: float = Field(
        ..., description="Calibrated probability of VIP classification"
    )
    spending_tier: str = Field(
        ..., description="Tier: Standard, Gold VIP, or Platinum VIP"
    )
    model_used: str = Field(..., description="ML architecture used for inference")


# ---------------------------------------------------------------------------
# Business Case 2: Demand Schemas
# ---------------------------------------------------------------------------
class DemandPredictRequest(BaseModel):
    category_id: int = Field(1, ge=1, description="Category identifier (1-10)")
    price: float = Field(..., ge=0.01, description="Unit product price ($)")
    stock_quantity: int = Field(..., ge=0, description="Current inventory level")
    rating: float = Field(4.5, ge=1.0, le=5.0, description="Product star rating (1-5)")
    order_frequency: int = Field(
        5, ge=0, description="Historical monthly order frequency"
    )
    avg_discount: float = Field(0.0, ge=0.0, description="Average discount amount ($)")


class DemandPredictResponse(BaseModel):
    predicted_units_sold: int = Field(..., description="Forecasted unit sales demand")
    depletion_risk: str = Field(
        ..., description="Inventory depletion risk: Low, Medium, or High"
    )
    depletion_ratio: float = Field(
        ..., description="Ratio of forecasted demand to on-hand inventory"
    )
    recommended_action: str = Field(..., description="Procurement / Restock advice")
    model_used: str = Field(..., description="Model architecture used")


# ---------------------------------------------------------------------------
# Business Case 3: Order Status Schemas
# ---------------------------------------------------------------------------
class OrderStatusPredictRequest(BaseModel):
    total_amount: float = Field(..., ge=0.0, description="Total order amount ($)")
    item_count: int = Field(1, ge=1, description="Number of items in order")
    payment_method: str = Field(
        "credit_card", description="Payment method: credit_card, paypal, etc."
    )
    city: str = Field("San Francisco", description="Destination city")
    discount_amount: float = Field(0.0, ge=0.0, description="Discount applied ($)")
    days_elapsed: int = Field(1, ge=0, description="Days elapsed since order placed")


class OrderStatusPredictResponse(BaseModel):
    delay_probability: float = Field(
        ..., description="Probability of shipping or fulfillment delay"
    )
    predicted_status: str = Field(..., description="Expected fulfillment status")
    risk_tier: str = Field(
        ..., description="Risk tier: On Time, Moderate Delay Risk, High Delay Risk"
    )
    model_used: str = Field(..., description="Model architecture used")


# ---------------------------------------------------------------------------
# Business Case 4: Churn Schemas
# ---------------------------------------------------------------------------
class ChurnPredictRequest(BaseModel):
    days_since_last_order: int = Field(
        ..., ge=0, description="Days elapsed since the customer's most recent order"
    )
    order_count: int = Field(..., ge=0, description="Total orders lifetime")
    days_since_signup: int = Field(
        ..., ge=0, description="Total days since customer registered"
    )
    total_spend: float = Field(..., ge=0.0, description="Total historical spending ($)")
    avg_days_between_orders: float = Field(
        30.0, ge=0.0, description="Average cadence between orders (days)"
    )
    distinct_categories_count: int = Field(
        1, ge=0, description="Number of unique categories purchased from"
    )


class ChurnPredictResponse(BaseModel):
    churn_probability: float = Field(
        ..., description="Estimated probability of customer churn"
    )
    is_churn_risk: bool = Field(
        ..., description="Flag indicating if customer is in churn territory"
    )
    churn_risk_tier: str = Field(
        ..., description="Risk categorization: Low (Loyal), Medium, or High (Critical)"
    )
    retention_strategy: str = Field(
        ..., description="Prescribed marketing retention action"
    )
    model_used: str = Field(..., description="Model architecture used")


# ---------------------------------------------------------------------------
# Business Case 5: Recommendation Schemas
# ---------------------------------------------------------------------------
class RecommendationPredictRequest(BaseModel):
    customer_id: int = Field(1, ge=1, description="Customer ID for personalization")
    top_k: int = Field(
        5, ge=1, le=15, description="Number of recommendations to return"
    )


class RecommendedProduct(BaseModel):
    rank: int
    product_id: int
    name: str
    category_name: str
    price: float
    rating: float
    affinity_score: float


class RecommendationPredictResponse(BaseModel):
    customer_id: int
    top_k: int
    recommendations: list[RecommendedProduct]
    model_used: str


# ---------------------------------------------------------------------------
# Overview & Metadata Schemas
# ---------------------------------------------------------------------------
class MLCaseSummary(BaseModel):
    id: str
    title: str
    category: str
    target: str
    primary_metric: str
    description: str


class MLCasesResponse(BaseModel):
    total_cases: int
    cases: list[MLCaseSummary]


class MLReportResponse(BaseModel):
    markdown_report: str
    summary: dict[str, Any]


class MLTrainResponse(BaseModel):
    status: str
    message: str
    trained_models: dict[str, str]
