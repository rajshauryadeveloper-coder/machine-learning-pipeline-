---
type: skill
name: test
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: review
chain_on_failure: implement
tags: [test, verification]
---

# Test Skill

Verify the implementation meets the requirements and passes all automated checks.

## Routing & Reference Table

| Condition | Reference to Load |
| :--- | :--- |
| No tests exist for a new feature | `references/testing_patterns.md` |
| Unsure how to run tests in this project | `references/test_runners.md` |

## When to Invoke
- After `implement` reports completion.
- After `review` rejects and routes back through `implement`.

## Inputs
| Input | Description |
| :--- | :--- |
| `AGENT_CONTEXT.md` | Contains the test command |
| `worklogs/<branch-slug>/attempts/` | Latest implement attempt |
| Source Files | The source files changed in the implementation |

## Coverage Gate
After tests pass, check per-module coverage in the output:
- Modules **below 60%** should be noted in the worklog for integration test follow-up.
- External dependencies (database, APIs) should be **mocked in unit tests**; live integration tests belong in `tests/integration/` when schema exists.

## Hook Scripts
| Script | Language | Description |
| :--- | :--- | :--- |
| `pre_check.sh` | Bash (Customizable) | Verify implement completed successfully |
| `run_tests.sh` | Bash (Customizable) | Discover and run the test suite |
| `capture_results.py` | Python (Customizable) | Parse output to structured log |

## Steps
1. Run `pre_check.sh` to ensure prerequisites are met.
2. Run `run_tests.sh` — capture full output.
3. Run `capture_results.py` to write a structured log.
4. If pass → run post_complete.sh then chain to review.
5. If fail → write failure details to attempt file, chain back to implement.

## Pre-Check
Before testing, ensure that:
- The implementation stage is complete.
- We are not on the main/master branch.
- A test command is available.

## Post-Complete
On test completion (pass or fail):
- Write the captured logs to the artifacts directory.
- Update the attempt log with test outcome metrics.

## On Retry
If tests fail and we re-enter `test` after another `implement` pass:
- Ensure the previous failing tests are prioritized if the runner supports it.
- Verify changes are committed before testing.

## Chain
- **Success:** Chain to `review` for human or automated code review.
- **Failure:** Chain back to `implement` with structured feedback highlighting the failed tests.

## Outputs
- Structured test result log in `worklogs/<branch-slug>/artifacts/`.
- Updated state in the current attempt file.
