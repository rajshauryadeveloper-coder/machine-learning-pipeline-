---
type: reference
skill: implement
status: active
---

# Code Patterns Reference

## Core Principles
- **Single Responsibility**: Classes/functions should have exactly one reason to change.
- **Open/Closed**: Software entities should be open for extension but closed for modification.
- **Dependency Inversion**: Depend on abstractions, not concretions.
- **Immutability First**: Default to immutable state unless mutability is explicitly required.
- **Fail Fast**: Validate inputs early and loudly throw specific exceptions.

## Change Discipline
Agents operate best with strict discipline:
- **Small PRs**: Limit changes to < 200 lines where possible.
- **One Concern Per Commit**: Separate refactors from feature additions.
- **Why this matters**: Small, focused changes are easier for downstream tests to validate and for humans to review.

## Error Handling Patterns
- **Never Swallow Exceptions**: Avoid generic `except Exception: pass`. 
- **Structured Errors**: Use custom error types with rich context.
- **Boundary Handling**: Catch errors at architectural boundaries, not deep within logic.

## Naming Rules

| Context | Pattern | Example |
|---|---|---|
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES_PER_STAGE` |
| Classes | PascalCase | `RequestHandler` |
| Functions | snake_case (verb) | `fetch_user_data()` |
| Interfaces | PascalCase (adjective) | `Serializable` |

## Negative Constraints
**DO NOT:**
- Write large god-classes or massive functions.
- Introduce arbitrary delays or `sleep()` calls.
- Hardcode environment-specific paths or secrets.
- Leave commented-out dead code.
- Ignore existing formatting standards in the file.
