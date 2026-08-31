#!/usr/bin/env bash
# Seed PostgreSQL database with 5 tables and 200 records in largest table
set -euo pipefail

echo "Resetting schema and seeding database..."
uv run python -m src.db.seed
echo "Seeding completed successfully."
