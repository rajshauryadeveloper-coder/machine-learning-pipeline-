---
type: prompt
status: pending
created: 2026-08-31T16:23:00Z
tags: [example, auth]
---

# Add JWT Authentication Middleware

## Task
Implement a custom JWT authentication middleware for our FastAPI application. This middleware should intercept incoming requests, validate the JWT token in the `Authorization` header, and inject the authenticated user's context into the request state for downstream handlers to use.

## Constraints
1. **No breaking changes**: Must not break existing open (unauthenticated) routes.
2. **Tech Stack**: Must strictly use `PyJWT` for token validation, matching the `AGENT_CONTEXT.md` stack.
3. **Test Coverage**: Must add comprehensive unit tests for both valid and invalid token scenarios.
4. **Performance**: Token decoding should be fast; avoid unnecessary database lookups within the middleware if possible.
5. **Style**: Follow existing `flake8` and `black` formatting rules.

## Starting Points
- `src/middleware/auth.py`: This file doesn't exist yet, create it here.
- `src/main.py`: You will need to attach the new middleware to the FastAPI app instance here.
- `tests/test_middleware.py`: Add your test cases here.
- `requirements.txt`: Ensure `PyJWT` is listed.

## Acceptance Criteria
- [ ] Middleware extracts the token from the `Authorization: Bearer <token>` header.
- [ ] Requests missing the header on protected routes return a `401 Unauthorized`.
- [ ] Requests with expired or invalid tokens return a `401 Unauthorized` with a specific error message.
- [ ] Requests with valid tokens have `request.state.user` populated with the decoded token payload.
- [ ] Unauthenticated routes (like `/health` or `/docs`) still function normally.
- [ ] At least 4 unit tests are added covering happy path, missing token, expired token, and invalid signature.
- [ ] `docs/auth.md` is updated to describe how to generate and use the token in local development.

## Out of Scope
- Implementing the login endpoint that *generates* the JWT (assume another service or endpoint handles this).
- Adding role-based access control (RBAC) or granular permissions (just authentication, not authorization).
- Database schema changes.
