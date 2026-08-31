from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination envelope."""

    items: list[T]
    total: int = Field(description="Total matching items across all pages")
    page: int = Field(description="Current page index (1-based)")
    page_size: int = Field(description="Maximum items per page")
    total_pages: int = Field(description="Total number of pages")


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    is_active: bool
    created_at: datetime


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    country: str
    created_at: datetime


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int | None = None
    category_name: str | None = None
    name: str
    sku: str
    description: str | None = None
    price: Decimal
    stock_quantity: int
    rating: Decimal
    is_available: bool
    created_at: datetime


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    quantity: int
    unit_price: Decimal
    discount_amount: Decimal
    subtotal: Decimal
    created_at: datetime


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    customer_name: str | None = None
    customer_email: str | None = None
    order_status: str
    total_amount: Decimal
    shipping_address: str
    payment_method: str
    tracking_number: str | None = None
    ordered_at: datetime
    items: list[OrderItemOut] = Field(default_factory=list)


class TopProduct(BaseModel):
    product_id: int
    name: str
    sku: str
    units_sold: int
    total_revenue: Decimal


class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    product_count: int
    items_sold: int
    total_revenue: Decimal


class SalesOverview(BaseModel):
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    total_products: int
    total_order_items: int
    average_order_value: Decimal


class AnalyticsOverview(BaseModel):
    overview: SalesOverview
    top_products: list[TopProduct]
    category_breakdown: list[CategoryBreakdown]


class ColumnMetadata(BaseModel):
    column_name: str
    data_type: str
    is_nullable: str


class TableMetadata(BaseModel):
    table_name: str
    row_count: int
    column_count: int
    columns: list[ColumnMetadata]


class DatabaseStatus(BaseModel):
    status: str
    connected: bool
    tables: list[TableMetadata]


class SeedResponse(BaseModel):
    message: str
    counts: dict[str, int]
