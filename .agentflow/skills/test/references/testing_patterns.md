---
type: reference
skill: test
status: active
---

# Testing Patterns & Guidelines

## Testing Hierarchy
Follow the testing pyramid to ensure a reliable and fast test suite:
- **Unit Tests:** (Priority 1) Fast, isolated tests for individual functions and classes. High volume.
- **Integration Tests:** (Priority 2) Verify that modules work together. Moderate volume.
- **E2E Tests:** (Priority 3) Slow, comprehensive tests simulating user flows. Low volume.

## Test Anatomy
Use the Arrange-Act-Assert (AAA) pattern for clarity.
```python
def test_user_authentication():
    # Arrange
    user = User(username="alice", password="secure123")
    db_session.add(user)
    
    # Act
    result = authenticate_user("alice", "secure123")
    
    # Assert
    assert result.is_success == True
    assert result.token is not None
```

## Coverage Targets

| What to Test | What NOT to Test |
| :--- | :--- |
| Business logic & edge cases | Third-party library internals |
| Boundary conditions | Standard library functions |
| Error handling & recovery | Trivial getters/setters |

## Test Failure Diagnosis
When a test fails, systematically isolate the issue:
1. **Reproduce Locally:** Run the specific failing test in isolation.
2. **Check Logs/Traces:** Inspect the exact error message and stack trace.
3. **Verify State:** Ensure the database, environment, or mocked state is what you expect.
4. **Bisect Changes:** If a previously passing test fails, identify which recent change introduced the failure.

## Negative Constraints
- DO NOT hardcode absolute paths or environment-specific data in tests.
- DO NOT write tests that depend on the execution order of other tests.
- DO NOT ignore flaky tests; fix them or disable them if they cannot be fixed immediately.
- DO NOT test private methods directly; test the public interface.
