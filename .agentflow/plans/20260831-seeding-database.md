---
type: plan
status: approved
created: 2026-08-31T18:15:00Z
tags: [database, schema, seed, api, fastapi]
---

# Plan: Seed Database and Expose APIs

## Goal
Connect to PostgreSQL, clear existing schemas/tables, construct a 5-table relational schema (with 5–10 columns each), seed realistic datasets including exactly 200 records in the largest table (`order_items`), and expose modern, paginated REST APIs with interactive frontend data viewing.

## Context
The repository was initialized with a baseline FastAPI app, but without domain models, database tables, or seeded records. The task requires a complete database schema setup, full schema reset/truncation, 5 tables with 5–10 columns, 200 records in the largest table, and production-grade REST APIs following industry best practices.

## Scope
**IS IN SCOPE:**
- Database reset routine: drop all existing tables and recreate public schema.
- Schema definition: 5 relational tables (`categories`, `customers`, `products`, `orders`, `order_items`) with 5–10 columns each, primary keys, foreign keys with ON DELETE rules, indexes, and constraints.
- Database seeding: Seed realistic data with exactly 200 rows in the largest table (`order_items`), plus matching foreign key entities across categories, customers, products, and orders.
- FastAPI REST APIs:
  - `/api/v1/categories` & `/api/v1/categories/{id}`
  - `/api/v1/customers` & `/api/v1/customers/{id}`
  - `/api/v1/products` & `/api/v1/products/{id}` (with category filter, price range, search, pagination)
  - `/api/v1/orders` & `/api/v1/orders/{id}` (with status filter, customer filter, pagination)
  - `/api/v1/order-items` & `/api/v1/order-items/{id}` (with order filter, pagination)
  - `/api/v1/analytics/overview` (high-level KPIs, top products, sales totals)
  - `/api/v1/database/reset-and-seed` (admin action to trigger reseed)
- Static Frontend: Update `html/index.html` to provide an interactive dashboard to inspect all 5 tables, paginate records, view KPIs, and trigger database reseeding.
- Automated Testing: Unit tests with mocked DB and integration tests against PostgreSQL.
- Documentation: Update `docs/api.md`, `docs/architecture.md`, and `docs/getting-started.md`.

**IS NOT IN SCOPE:**
- User authentication / JWT tokens (reserved for future auth task).
- Third-party payment gateway integration.
- Frontend build pipelines (Node.js/npm).

## Implementation Steps
1. **Database Schema & DDL (`src/db/schema.py`)**
   - Implement DDL scripts for clearing schema (`DROP SCHEMA public CASCADE; CREATE SCHEMA public;` or `DROP TABLE IF EXISTS ... CASCADE;`).
   - Create 5 tables:
     - `categories` (6 columns)
     - `customers` (9 columns)
     - `products` (10 columns)
     - `orders` (8 columns)
     - `order_items` (8 columns - 200 rows)
   - Add indices on foreign keys and frequently queried fields.

2. **Seeding Engine (`src/db/seed.py`)**
   - Implement data generator for 10 categories, 40 customers, 30 products, 60 orders, and 200 order items.
   - Calculate accurate order subtotals, order total amounts, discounts, and timestamps.
   - Provide CLI entrypoint (`python -m src.db.seed`).

3. **Pydantic Schemas (`src/schemas/`)**
   - Define request/response schemas, pagination metadata envelopes (`PaginatedResponse[T]`), and analytics models.

4. **FastAPI Endpoints (`src/api/v1/`)**
   - Create modular routers for categories, customers, products, orders, order items, analytics, and db management.
   - Implement query filtering, search parameters, pagination (`page`, `page_size`, max limit 100), and sorting.
   - Register routers on the FastAPI application in `src/main.py`.

5. **Frontend Dashboard (`html/index.html`)**
   - Add overview KPIs (revenue, order counts, product counts, largest table record count).
   - Add interactive tabs for browsing all 5 tables with search, filter, and pagination.
   - Add button to trigger database reset & reseed.

6. **Testing (`tests/`)**
   - Unit tests in `tests/test_api.py` and `tests/test_main.py`.
   - Integration tests in `tests/test_db_seed.py` validating schema reset, table row counts (verifying 200 records in `order_items`), and API responses.

7. **Documentation (`docs/`)**
   - Update `docs/api.md` with complete endpoint docs, parameters, and response formats.
   - Update `docs/architecture.md` with database ER diagram and schema descriptions.

## Files Touched

| Path | Change Type | Risk Level | Why |
| --- | --- | --- | --- |
| `src/db/__init__.py` | Add | Low | DB package init |
| `src/db/schema.py` | Add | Medium | DDL schema creation and teardown |
| `src/db/seed.py` | Add | Medium | Database seeding logic (200 records in largest table) |
| `src/schemas/__init__.py` | Add | Low | Schemas package init |
| `src/schemas/models.py` | Add | Low | Pydantic response models |
| `src/api/__init__.py` | Add | Low | API package init |
| `src/api/v1/__init__.py` | Add | Low | API v1 router init |
| `src/api/v1/router.py` | Add | Medium | Combined v1 router |
| `src/api/v1/endpoints/*.py` | Add | Medium | REST endpoints for tables & analytics |
| `src/main.py` | Modify | Low | Mount v1 API router |
| `html/index.html` | Modify | Low | Interactive data browser UI |
| `tests/test_db_seed.py` | Add | Medium | Tests for database reset & seed verification |
| `tests/test_api.py` | Add | Medium | Tests for REST API endpoints |
| `docs/api.md` | Modify | Low | Updated API documentation |
| `docs/architecture.md` | Modify | Low | Updated architecture & ER diagram |

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Schema teardown drops unintended tables | Low | High | Teardown is explicit and scoped to configured `ecommerce_database` public schema. |
| Foreign key constraint violations during seeding | Low | High | Insert in strict dependency order: categories/customers -> products -> orders -> order_items. |
| Database connection failure when Postgres is offline | Low | Medium | Graceful error handling in endpoints and DB health check. |

## Definition of Done
- [ ] Schema drop/create runs cleanly with no errors.
- [ ] 5 tables created, each with 5–10 columns.
- [ ] 200 records seeded into `order_items` (largest table).
- [ ] REST APIs available with pagination, filtering, and OpenAPI documentation.
- [ ] Interactive web UI displays table records.
- [ ] All unit and integration tests pass with pytest.
- [ ] Flake8 and black checks pass.
- [ ] Documentation updated.
- [ ] Worklog updated and merged.

## Worklog
[SUMMARY.md](../worklogs/feature-seed-database-and-apis/SUMMARY.md)
