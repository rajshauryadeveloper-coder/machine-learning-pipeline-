---
type: reference
skill: review
status: active
---

# Security Review Checklist

## Input Validation
- [ ] Sanitize all external input (user data, headers, query params).
- [ ] Validate data types, lengths, and formats strictly (allow-list approach).
- [ ] Never trust client data; assume all input is malicious until validated.

## Authentication & Authorization
- [ ] Check authentication on every protected route or handler.
- [ ] Verify Role-Based Access Control (RBAC) constraints (does the user have permission to do this specific action?).
- [ ] Never expose internal IDs or sensitive tokens to unauthorized users. Ensure proper scoping of resources (e.g., user can only edit their own profile).

## Data Exposure
- [ ] Never return raw database errors or stack traces to the client in production.
- [ ] Scrub Personally Identifiable Information (PII) and credentials from all logs.
- [ ] Ensure sensitive data in storage or transit is properly encrypted.

## Dependency Risk
When introducing new dependencies, verify:
- Are there known vulnerabilities for this specific version?
- Is the dependency actively maintained?
- Are we importing only what we need to minimize attack surface?

## Negative Constraints
- **NEVER** use `eval()`, `exec()`, or equivalent unsafe reflection on untrusted input.
- **NEVER** construct SQL queries using string concatenation (always use parameterized queries or an ORM).
- **NEVER** hardcode secrets, passwords, or API keys in the source code.
