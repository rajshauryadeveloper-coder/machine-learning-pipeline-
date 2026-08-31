---
type: prompt
status: completed
created: 2026-08-31T18:13:00Z
completed: 2026-08-31T18:22:00Z
tags: [database, schema, seed, api, fastapi]
---

# Seed Database and Expose APIs

## Task
I want you to:
1. Connect to the database.
2. Clear the entire schema.
3. Truncate and delete all the tables.
4. Create a new schema with five tables, with between five and ten columns for each table.
5. Insert 200 records into the largest table.

After that is done, we can expose some APIs for external users to view the contents of the table. The API should be meaningful and should return important or useful information to them. You can research the best API design practices to create it.

## Acceptance Criteria
- [x] Connect to PostgreSQL database (`ecommerce_database`).
- [x] Clear schema, drop/truncate existing tables cleanly.
- [x] Create 5 relational tables (`categories`, `customers`, `products`, `orders`, `order_items`), each with 5-10 columns.
- [x] Seed data including 200 records in the largest table (`order_items`).
- [x] Expose RESTful, paginated, searchable, and filtered FastAPI endpoints for querying and viewing data.
- [x] Provide tests covering schema migration/seeding and API routes (18 tests, 91% coverage).
- [x] Integrate API viewer with static frontend dashboard in `html/index.html`.
- [x] Update documentation in `docs/api.md`, `docs/architecture.md`, and `docs/getting-started.md`.

## Outcome
Completed and merged — see [worklog](../worklogs/feature-seed-database-and-apis/SUMMARY.md) and [plan](../plans/20260831-seeding-database.md).