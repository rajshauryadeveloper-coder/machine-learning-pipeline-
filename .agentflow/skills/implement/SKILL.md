---
type: skill
name: implement
version: 2.0.0
status: active
created: 2026-08-31T18:25:00Z
chain_to: verify
chain_on_failure: null
tags: [implement, code]
---

# Implement Skill (Optimized)

## Goal
Implement features and write corresponding unit/integration tests with minimal round-trip friction.

## When to Invoke
- **New Task**: Triggered following `plan` stage.
- **Retry**: Triggered when `verify` fails and returns execution context to implementation.

## Steps
1. **Read Plan**: Review target files and acceptance criteria in `plans/`.
2. **Implement Code & Tests**: Make focused, targeted modifications to application code and test suites.
3. **Verify**: Trigger the `verify` skill (`./scripts/flow verify`) to validate tests, coverage, lint, and formatting.

## Chain
- **Success**: Chains to `verify` skill.

## Outputs
- Modified and new application source files
- Test suite files in `tests/`
