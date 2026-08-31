---
type: reference
skill: document
status: active
---

# Architecture Templates

This document provides templates and guidance for documenting architecture decisions and system designs.

## ADR Template

Use this template for Architecture Decision Records (ADRs).

```markdown
# ADR-[Number]: [Title]

**Status**: [Draft | Proposed | Accepted | Rejected | Superseded by ADR-XXX]
**Date**: [YYYY-MM-DD]
**Author(s)**: [Names]

## Context

[What is the problem we are solving? What are the constraints? Why do we need to make a decision now?]

## Decision

[What is the change that we are making? Be specific.]

## Consequences

[What becomes easier or more difficult to do because of this change? Consider both positive and negative consequences.]
```

## System Architecture Doc Template

Based on the C4 model. Use these headers for system docs:

- **Context**: The big picture. Who uses the system and what external systems does it interact with?
- **Containers**: The high-level technical building blocks (e.g., web app, database, mobile app).
- **Components**: The major structural building blocks within a container (e.g., controllers, services, repositories).
- **Deployment**: How the system is mapped to infrastructure.

## When to Write an ADR

Write an ADR when making a decision that is hard to reverse or has significant impact, such as:
- Introducing a new external dependency (database, third-party API).
- Making a major schema change.
- Making a significant performance tradeoff.
- Establishing a new security boundary.

## ADR Anti-Patterns

- **Writing ADRs after the fact**: ADRs should be written *before* or *during* the decision process, not as an afterthought.
- **Lack of alternatives**: A good ADR discusses the options that were considered and rejected.
- **Vague consequences**: Be specific about the tradeoffs. Don't just say "better performance", say "reduces latency by X but increases memory usage by Y".
