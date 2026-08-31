---
type: skill
name: verify
version: 2.0.0
status: active
created: 2026-08-31T18:25:00Z
chain_to: ship
chain_on_failure: implement
tags: [verify, test, lint, format, quality]
---

# Verify Skill (Optimized Merged Verification)

## Goal
Execute all automated quality and correctness gates in a single, token-efficient command (`flow verify`):
- Run Pytest suite
- Enforce Coverage Threshold (>= 60%)
- Check Flake8 linting
- Check Black formatting
- Capture Git diff and structured test logs

## When to Invoke
- Immediately after `implement` finishes writing or modifying code.
- To re-verify changes after addressing review/test feedback.

## Hook Commands

| Check | Command | Automated By |
| --- | --- | --- |
| **All-In-One Verification** | `python .agentflow/scripts/flow.py verify` | `flow verify` |
| Pytest & Coverage | `uv run pytest tests/ --cov=src` | `flow.py` |
| Lint Check | `uv run flake8 src/ tests/` | `flow.py` |
| Format Check | `uv run black --check src/ tests/` | `flow.py` |

## Steps

1. **Run Verification**:
   ```bash
   ./scripts/flow verify
   ```
2. **Evaluate Output**:
   - **If PASS (Exit code 0)**: All tests passed, coverage >= 60%, lint/format clean. Automatically writes verification artifact and advances worklog stage to `ship`. Chain directly to `ship` skill.
   - **If FAIL (Non-zero exit code)**: Review the concise error summary, fix the identified code/test issues in `implement`, and re-run `./scripts/flow verify`.

## Chain
- **Success**: Chains to `ship` skill.
- **Failure**: Chains back to `implement` skill.

## Outputs
- `worklogs/<branch-slug>/artifacts/verify_result_<timestamp>.md`
- `worklogs/<branch-slug>/attempts/verify_attempt_<N>_<timestamp>.md`
- Updated `SUMMARY.md` stage status (`ship` on pass, `implement` on fail).
