---
type: reference
skill: postmortem
status: active
---

# Lessons Taxonomy

This reference helps categorize postmortem lessons to identify systemic patterns.

## Lesson Categories

| Category | Description | Example |
| :--- | :--- | :--- |
| **scope-creep** | The task expanded beyond its original intent. | "Added refactoring unrelated to feature." |
| **missing-tests** | Failure caused by insufficient test coverage. | "Edge case in parser not tested." |
| **environment-mismatch** | Worked locally but failed in CI/prod. | "Hardcoded absolute path." |
| **unclear-requirements** | Ambiguity in the spec led to wrong implementation. | "Spec didn't define behavior for empty lists." |
| **tool-failure** | Underlying tool/dependency caused failure. | "Upstream API change broke integration." |
| **design-mismatch** | Implementation conflicted with existing architecture. | "Bypassed service layer." |

## Pattern Detection

When writing a postmortem, review `ROLLUP.md` to spot recurring issues:
- Are we seeing the same category (e.g., `environment-mismatch`) frequently?
- Is a specific module consistently problematic?
- Mention recurring patterns in the postmortem details (e.g., "This is the 3rd time we hit tool-failure on this API.").

## Actionable vs Vague Lessons

| Vague (Bad) | Actionable (Good) |
| :--- | :--- |
| "Be more careful with strings." | "Always sanitize user input before passing to the shell." |
| "Tests failed." | "Integration tests need independent mocked databases to avoid race conditions." |
| "The requirements were bad." | "Add a pre-check step to ensure all edge cases are defined in the spec." |

## When to Update the Workflow

Recurring patterns should drive changes to the `AGENTFLOW.md` workflow or specific skills. Consider updating the workflow if:
- A pattern occurs 3 or more times.
- The failure could be prevented by a mechanical check (e.g., a linter).
- A skill is consistently misinterpreting its inputs.
