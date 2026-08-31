---
name: verify
status: active
chain_to: ship
chain_on_failure: implement
tags: [verify, test, lint, format, coverage]
---
# Verify Skill (v3 High-Speed)

## Goal
Execute all automated quality gates with fast-fail linting in 1 single command.

## Command
```bash
./scripts/flow verify
```

## Gates Automated
1. **Flake8 Linter** (Fast-fail, ~0.2s)
2. **Black Formatter Check** (Fast-fail, ~0.2s)
3. **Pytest Suite** (Compact output)
4. **Coverage Threshold** (>= 60%)
5. **Git Diff Capture**

## Outcome
- **Pass (Exit 0)**: Records verification artifact and chains to `ship`.
- **Fail (Exit 1)**: Prints exact failures and chains back to `implement`.
