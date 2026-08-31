---
type: context
status: active
created: 2026-08-31T16:23:00Z
updated: 2026-09-01T00:58:00Z
---

# Agent Context (v3 Token-Optimized)

## Quick Project Snapshot

- **Stack**: Python FastAPI + Static HTML Dashboard + PostgreSQL (`127.0.0.1:5432`)
- **Database**: 5 Relational Tables (`categories`, `customers`, `products`, `orders`, `order_items`), 340 total rows
- **ML Pipelines**: 5 scikit-learn hybrid ensembles (CLV spend/VIP, Demand velocity, Order delay risk, Churn, Top-K cross-sell)
- **Agentic AI**: LangGraph 4-stage reasoning graph + Google AI Studio (`gemma-4-31b-it`) with strict read-only AST/token guardrails

## Fast Workflow Commands (`flow` CLI)

- **Start Task (Plan)**: `./scripts/flow start <slug> --title "Title" --prompt prompts/<file>.md`
- **One-Shot Context**: `./scripts/flow context` (dumps entire DB, routes, and ML state in 1 shot)
- **Verify (Lint + Black + Pytest + Coverage)**: `./scripts/flow verify`
- **Ship (Secret Shield + Commit + Push + Merge + Postmortem)**: `./scripts/flow ship --lesson "<Cat>" --details "<Details>"`
- **Status**: `./scripts/flow status`

## Build & Test Commands

- **Run Dev Server**: `uv run uvicorn src.main:app --reload`
- **Run Tests**: `uv run pytest tests/ --cov=src`
- **Lint & Format**: `uv run flake8 src/ tests/ && uv run black --check src/ tests/`

## Agent Rules for Zero-Waste Token Efficiency

1. **Use `flow context` first**: Avoid multi-turn file exploratory walks. Run `./scripts/flow context` to obtain full DB and API metadata in 1 shot.
2. **Never hardcode secrets**: Do not write raw API keys or passwords in `.md` or `.py` files.
3. **Atomic Operations**: Run `./scripts/flow verify` and `./scripts/flow ship` for single-command transitions.
4. **Scope Control**: Modify only files relevant to the active prompt.
