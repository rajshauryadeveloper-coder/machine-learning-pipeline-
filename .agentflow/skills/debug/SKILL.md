---
type: skill
name: debug
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: implement
chain_on_failure: null
tags: [debug, diagnosis, failure-analysis]
---

# Debug Skill

The `debug` skill is invoked when test failures have non-obvious root causes. It produces a structured diagnosis that feeds back into implement with a specific fix plan.

## Routing & Reference Table

| Topic | Read |
| --- | --- |
| Diagnosing test failures | `references/failure_patterns.md` |
| Debugging environment/tooling issues | `references/environment_debug.md` |

## When to Invoke

- Test skill reports failures that are not self-evident from the output
- Implement skill is looping (2+ failed retries) without making progress
- Human escalates a confusing failure
- A flaky test pattern is suspected

## Inputs

| Source | Description |
| --- | --- |
| `worklogs/<branch>/artifacts/test-*.log` | raw test output from the latest test run |
| `worklogs/<branch>/attempts/` | full attempt history showing what was already tried |
| Source Files | The source files changed in the latest implement attempt |
| `AGENT_CONTEXT.md` | build and test commands, tech stack |

## Hook Scripts

| Script | Language | Run command | Purpose |
| --- | --- | --- | --- |
| `extract_failures.sh` | bash | `bash scripts/extract_failures.sh --log <path>` | Extracts and deduplicates failure snippets from test logs |
| `trace_callstack.py` | python | `python3 scripts/trace_callstack.py --log <path>` | Parses stack traces and maps to source files |
| `write_diagnosis.py` | python | `python3 scripts/write_diagnosis.py --output <path>` | Produces structured diagnosis markdown |
> Note: Scripts can be .sh or .py — replace with your preferred language

## Steps

1. Run `bash scripts/extract_failures.sh --log <latest-test-log>` to isolate failure signatures
2. Run `python3 scripts/trace_callstack.py` to map stack traces to source files
3. Read the failing source files and the tests that target them
4. Check attempt history — what was already tried? What made it worse?
5. Form a hypothesis: one specific root cause (not a list — commit to one)
6. Run `python3 scripts/write_diagnosis.py` to produce structured diagnosis
7. Update the plan with a targeted fix strategy (narrow scope: touch only files implicated by the hypothesis)
8. Chain to **implement** with the diagnosis as input

## Pre-Check

- At least one test log file exists in `worklogs/<branch>/artifacts/`
- The failing test names are identifiable from the log
- DO NOT run debug if the test log is empty or missing

## Post-Complete

- `worklogs/<branch>/artifacts/diagnosis-<timestamp>.md` — structured diagnosis
- Plan updated with targeted fix strategy
- `SUMMARY.md` stage set back to `implement` with a note referencing the diagnosis file

## On Retry

- Broaden the hypothesis — consider environment issues, dependency conflicts
- Read `references/environment_debug.md`
- If still unresolved after second debug pass: escalate to human with full diagnosis trail

## Chain

- On diagnosis found → implement (with diagnosis file as additional input)
- On inconclusive → escalate

## Outputs

- `worklogs/<branch>/artifacts/diagnosis-<timestamp>.md`
- Updated plan
- Updated `SUMMARY.md`
