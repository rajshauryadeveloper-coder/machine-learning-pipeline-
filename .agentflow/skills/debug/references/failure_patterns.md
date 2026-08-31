---
type: reference
skill: debug
status: active
---

# Failure Patterns Reference

This reference catalogs common test failure patterns to help accelerate the debugging process. Always consult this before forming a root cause hypothesis.

## Failure Pattern Catalog

| Pattern | Likely Cause | First Thing to Check | Fix Strategy |
| --- | --- | --- | --- |
| Assertion Mismatch | Code logic error or outdated test data | Expected vs actual diff in the test output | Update logic if wrong, or update test expectations if requirements changed |
| Import Error / ModuleNotFound | Broken dependencies, bad pathing, or circular imports | Ensure `__init__.py` exists, check virtual environment | Fix import path or reinstall dependencies |
| Fixture Not Found | Typo in fixture name or missing import | conftest.py or test setup block | Add the fixture or correct the name |
| Timeout | Infinite loops, missing mocks, network calls | The line where the timeout occurred via stack trace | Mock the external call or fix the loop condition |
| Flaky Test | Concurrency issues, race conditions, order dependency | Run the test multiple times or check for global state | Isolate state, mock timers, remove order dependencies |
| Type Error | Incorrect types passed to functions (e.g. None instead of dict) | Variable initialization or upstream return values | Add type checking, handle None cases |
| Missing Env Variable | Code expects an env var that isn't set in the test environment | `.env.test` or test runner environment setup | Mock `os.environ` or provide default values |
| Database State Pollution | Tests are not cleaning up after themselves | What runs immediately before the failing test | Use transactional tests or robust teardown methods |
| Mock Not Called | Code path containing the mocked function wasn't reached | Conditional statements wrapping the call | Fix the conditional logic or adjust test input |
| Off-by-one | Loop conditions, array indexing bounds | Edge cases (0, len-1, len) | Adjust the boundary condition |

## Debugging Decision Tree

When diagnosing a failure, consider where the bug might live:
1. **Code Bug:** The implementation logic is fundamentally incorrect.
2. **Test Bug:** The implementation is correct, but the test expectations, mock setup, or test data are flawed.
3. **Environment Bug:** Both code and test are correct, but the execution environment (Python version, OS, env vars) is wrong.
4. **Dependency Bug:** An upstream package updated and broke a contract.

Start by assuming a Code Bug, then Test Bug. Only look to Environment/Dependency if local behavior contradicts CI behavior.

## Flaky Test Identification

Flaky tests fail intermittently without code changes. To distinguish them from deterministic failures:
- Does the test fail locally but pass in CI (or vice-versa)?
- Does it fail only when run in the full suite, but pass in isolation?
- Does it involve timers, threading, random numbers, or external network calls?

If yes, the issue is likely a flaky test rather than a pure logic error.

## Negative Constraints

- **DO NOT** assume the test is wrong before verifying the implementation code.
- **DO NOT** fix symptoms without identifying the root cause (e.g. adding `if x is None: return` just to avoid a TypeError without knowing why `x` is None).
- **DO NOT** suppress errors, bypass assertions, or use `pytest.skip` to make tests pass.
