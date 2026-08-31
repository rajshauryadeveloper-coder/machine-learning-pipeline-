---
type: reference
skill: review
status: active
---

# Review Acceptance Criteria

## Standard Acceptance Criteria Checklist
- [ ] **Correctness:** Does the code correctly implement the requested feature or bug fix?
- [ ] **Tests:** Are there sufficient tests for the new code? Do the tests actually exercise the core logic?
- [ ] **Performance:** Are there any obvious performance bottlenecks? O(n^2) operations on large lists? N+1 query problems?
- [ ] **Readability:** Is the code clean, well-named, and adequately commented? Is complex logic explained?
- [ ] **Security:** Does the code handle inputs safely? (See security checklist if applicable).

## Common Review Failure Reasons
| Failure Reason | Impact | What to Ask Implement to Fix |
|----------------|--------|------------------------------|
| Unhandled edge cases | Bugs in production | Explicitly request handling of the missing scenario (e.g., null input, empty lists). |
| Missing tests | Regressions | Request specific test cases for the new logic or edge cases. |
| Hardcoded values | Poor maintainability | Request extracting hardcoded strings/magic numbers to constants or configuration. |
| Poor error handling | Silent failures | Request proper exception catching, logging, and user-facing error messages. |

## Verdict Writing Guide
When rejecting a PR/branch, your feedback must be actionable:
- **BAD:** "The code is messy and doesn't work well."
- **GOOD:** "File `src/parser.py`, line 45: The `parse_input()` function does not handle the case where the input string is empty, which causes a ValueError on line 47. Please add an early return."
Always reference specific files, line numbers (if known), and describe *why* something needs to change.

## Approval Conditions
When to approve despite imperfections (accepting technical debt):
- The flaw is minor and does not affect correctness, security, or core performance.
- Fixing it would significantly delay a critical feature, and the team agrees to address it later.
- Provide approval but leave a note to address the minor issue in a follow-up or add a `# TODO` comment.
