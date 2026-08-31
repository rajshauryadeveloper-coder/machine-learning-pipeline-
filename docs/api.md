# API Reference

Base URL (local): `http://127.0.0.1:8000`

Interactive OpenAPI documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Health & System

### `GET /health`
Returns application and database connectivity status.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "app": "Machine Learning Pipeline",
  "database": true
}
```

### `GET /`
Serves the interactive Data Explorer and Management Dashboard from `html/index.html`.

---

## Database Management API

### `GET /api/v1/database/status`
Returns connection status and structural metadata (row count, column count, column names and types) for all 5 relational tables.

### `POST /api/v1/database/reset-and-seed`
Resets the PostgreSQL schema, recreates all 5 tables with constraints and indices, and seeds realistic data including **200 records in the largest table (`order_items`)**.

**Response:** `200 OK`
```json
{
  "message": "Database successfully reset and seeded with 200 records in largest table.",
  "counts": {
    "categories": 10,
    "customers": 40,
    "products": 30,
    "orders": 60,
    "order_items": 200
  }
}
```

---

## Catalog & Store APIs

### 1. Categories (`/api/v1/categories`)

| Method | Endpoint | Query Parameters | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/categories` | `search`, `is_active`, `page`, `page_size` | List categories with pagination envelope |
| `GET` | `/api/v1/categories/{id}` | - | Retrieve category details by ID |

### 2. Customers (`/api/v1/customers`)

| Method | Endpoint | Query Parameters | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/customers` | `search`, `city`, `page`, `page_size` | List customers with contact and address details |
| `GET` | `/api/v1/customers/{id}` | - | Get customer profile |
| `GET` | `/api/v1/customers/{id}/orders` | - | Get complete purchase and order history for customer |

### 3. Products (`/api/v1/products`)

| Method | Endpoint | Query Parameters | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/products` | `search`, `category_id`, `min_price`, `max_price`, `is_available`, `sort_by`, `sort_order`, `page`, `page_size` | Filter catalog by price bounds, availability, category |
| `GET` | `/api/v1/products/{id}` | - | Get single product with category name |

### 4. Orders (`/api/v1/orders`)

| Method | Endpoint | Query Parameters | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/orders` | `customer_id`, `order_status`, `payment_method`, `sort_by`, `sort_order`, `page`, `page_size` | List orders with line item summary |
| `GET` | `/api/v1/orders/{id}` | - | Get order details with all nested item records |

### 5. Order Items — Largest Table (`/api/v1/order-items`)

| Method | Endpoint | Query Parameters | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/order-items` | `order_id`, `product_id`, `page`, `page_size` | Query items from largest table (200 records) |
| `GET` | `/api/v1/order-items/{id}` | - | Retrieve single line item |

---

## Analytics & Insights API

### `GET /api/v1/analytics/overview`
Aggregates sales performance, KPI metrics, top 5 selling products by revenue, and revenue breakdown by category.

**Response:** `200 OK`
```json
{
  "overview": {
    "total_revenue": "14285.50",
    "total_orders": 60,
    "total_customers": 40,
    "total_products": 30,
    "total_order_items": 200,
    "average_order_value": "238.09"
  },
  "top_products": [
    {
      "product_id": 2,
      "name": "PixelView 27-inch 4K UHD Monitor",
      "sku": "CMP-MN-002",
      "units_sold": 18,
      "total_revenue": "8091.00"
    }
  ],
  "category_breakdown": [...]
}
```

---

## Pagination Envelope

All collection endpoints return responses in standard pagination format:

```json
{
  "items": [...],
  "total": 200,
  "page": 1,
  "page_size": 20,
  "total_pages": 10
}
```

---

## Machine Learning & Predictive Analytics APIs (`/api/v1/ml`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/ml/cases` | List all 5 business cases, target variables, and metrics |
| `GET` | `/api/v1/ml/experiments` | Run and retrieve complete benchmark comparison results |
| `GET` | `/api/v1/ml/report` | Retrieve Markdown and JSON experiment evaluation report |
| `POST` | `/api/v1/ml/train` | Retrain all 5 ML models on latest PostgreSQL database |
| `POST` | `/api/v1/ml/predict/clv` | Predict Customer Lifetime Value ($) and VIP status |
| `POST` | `/api/v1/ml/predict/demand` | Forecast product unit demand and stock depletion risk |
| `POST` | `/api/v1/ml/predict/order-status` | Predict order delay risk and delivery schedule status |
| `POST` | `/api/v1/ml/predict/churn` | Predict customer churn probability and retention strategy |
| `POST` | `/api/v1/ml/predict/recommend` | Generate Top-K personalized product recommendations |

---

## Agentic Analytics Chatbot APIs (`/api/v1/agent`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/agent/chat` | Natural language analytics query with graph reasoning, read-only SQL, and safety guardrails |
| `GET` | `/api/v1/agent/status` | Operational status, active model provider, guardrail policies, and registered tools |
| `GET` | `/api/v1/agent/schema` | Schema catalog and table metadata exposed to the agent |

