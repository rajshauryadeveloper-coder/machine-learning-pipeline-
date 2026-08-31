---
type: documentation
status: active
created: 2026-08-31T17:41:00Z
updated: 2026-08-31T18:25:00Z
---

# Project Architecture & Relational Schema

## System Overview

```
┌─────────────┐     HTTP / JSON      ┌──────────────────┐     SQL (psycopg)   ┌────────────┐
│  html/      │ ◄──────────────────► │  src/main.py     │ ──────────────────► │ PostgreSQL │
│  Dashboard  │                      │  (FastAPI + v1)  │                     │ (local)    │
└─────────────┘                      └──────────────────┘                     └────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │  src/db/schema   │
                                     │  src/db/seed     │
                                     │  src/schemas     │
                                     │  src/api/v1      │
                                     └──────────────────┘
```

## Relational Database Schema (5 Tables)

Each table is designed with 5–10 columns, standard primary keys, indices, and foreign key constraints:

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : categorizes
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--|{ ORDER_ITEMS : contains
    PRODUCTS ||--o{ ORDER_ITEMS : ordered_in

    CATEGORIES {
        int id PK
        varchar name
        varchar slug
        text description
        boolean is_active
        timestamptz created_at
    }

    CUSTOMERS {
        int id PK
        varchar first_name
        varchar last_name
        varchar email
        varchar phone
        varchar address
        varchar city
        varchar country
        timestamptz created_at
    }

    PRODUCTS {
        int id PK
        int category_id FK
        varchar name
        varchar sku
        text description
        numeric price
        int stock_quantity
        numeric rating
        boolean is_available
        timestamptz created_at
    }

    ORDERS {
        int id PK
        int customer_id FK
        varchar order_status
        numeric total_amount
        varchar shipping_address
        varchar payment_method
        varchar tracking_number
        timestamptz ordered_at
    }

    ORDER_ITEMS {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        numeric unit_price
        numeric discount_amount
        numeric subtotal
        timestamptz created_at
    }
```

## Seed Record Counts

| Table | Columns | Seed Count | Notes |
| --- | --- | --- | --- |
| `categories` | 6 | 10 | Root taxonomy |
| `customers` | 9 | 40 | Realistic buyer profiles |
| `products` | 10 | 30 | Catalog with price, rating, stock |
| `orders` | 8 | 60 | Order headers with statuses |
| `order_items` | 8 | **200** | **Largest table** (200 records) |

## Modules & Responsibilities

| Path | Responsibility |
| --- | --- |
| `src/database.py` | Connection pools, context managers (`get_dict_connection`, `get_connection`). |
| `src/db/schema.py` | DDL schema creation, table truncation, schema dropping, metadata inspection. |
| `src/db/seed.py` | Seed generator creating 200 records in `order_items` and dependent entities. |
| `src/schemas/models.py` | Pydantic response models, pagination envelopes, and analytics models. |
| `src/api/v1/` | Modular REST API routers with search, filters, pagination, and sorting. |
| `html/index.html` | Zero-dependency responsive data explorer and management dashboard. |
