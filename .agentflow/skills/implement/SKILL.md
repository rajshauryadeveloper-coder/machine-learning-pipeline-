---
name: implement
status: active
chain_to: verify
tags: [implement, code, test-first]
---
# Implement Skill (v3 High-Speed)

## Goal
Implement feature code and unit tests following TDD principles.

## Guidelines
1. **Tests First**: Write test cases in `tests/test_<feature>.py` before writing application logic.
2. **Deterministic & Safe**: Follow read-only database guidelines for agents, enforce Pydantic schemas, and handle error edge cases.
3. **No Unrelated Changes**: Only modify files within the approved plan scope.
4. **Chain**: Proceed immediately to `verify` once implementation is complete.
