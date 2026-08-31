---
type: skill
name: research
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: implement
chain_on_failure: null
tags: [research, investigation, planning]
---

# Research Skill

The research skill is invoked BEFORE implementation when the agent needs to investigate an unfamiliar codebase area, external API, third-party library, or architectural pattern. It produces a structured research brief that feeds directly into the implementation plan.

## Routing & Reference Table

Load these references only when needed based on the research context:
- **Investigating unfamiliar codebase**: Read `references/codebase_mapping.md`

## When to Invoke

- Orchestrator or human explicitly requests a research pass before implementation
- Implement skill is blocked because the agent lacks critical knowledge (unknown API, unfamiliar library, ambiguous architecture)
- A new external dependency is being introduced for the first time

## Inputs

| Source | Description |
|--------|-------------|
| `prompts/<file>.md` | The task description defining what needs researching |
| `AGENT_CONTEXT.md` | Project tech stack and constraints |
| `plans/<timestamp>-<slug>.md` | Current plan (if exists) with open questions |
| External Sources | External documentation / source code / API docs (fetched by scripts) |

## Hook Scripts

| Script | Language | Run command | Purpose |
|--------|----------|-------------|---------|
| `gather_context.sh` | bash | `bash scripts/gather_context.sh` | Scans codebase for relevant patterns (grep, find, git log) |
| `fetch_docs.py` | python | `python3 scripts/fetch_docs.py --topic <topic>` | Fetches external docs or reads local files into a research buffer |
| `write_brief.py` | python | `python3 scripts/write_brief.py --output <path>` | Structures findings into a research brief markdown file |

> *Note: Scripts can be .sh or .py — swap the implementation to match your project preference.*

## Steps

1. Run pre-check: define the research question clearly (what specific gap does this research address?)
2. Run `bash scripts/gather_context.sh` to scan local codebase for existing patterns, prior art, related tests
3. Run `python3 scripts/fetch_docs.py` to retrieve external docs (API specs, library README, changelog)
4. Analyze findings against the task requirements
5. Identify: constraints, risks, recommended approach, and 2-3 implementation options
6. Run `python3 scripts/write_brief.py` to produce a structured research brief
7. Update the plan file with findings and resolved questions
8. Signal chain to **implement**

## Pre-Check

- [ ] A clear research question is defined (what are we investigating?)
- [ ] The relevant prompt or plan file is readable
- [ ] At least one of: codebase access or external doc URL is available

## Post-Complete

- `worklogs/<branch>/artifacts/research-<timestamp>.md` — the research brief is created and populated
- Plan file updated with resolved open questions and recommended approach
- `SUMMARY.md` current stage updated to `implement`

## On Failure

(When research is inconclusive)
- Document what was investigated and what remains unknown
- Escalate to human with specific questions via worklog
- DO NOT proceed to implement with unresolved blockers

## Chain

- **On success** → implement
- **On inconclusive** → escalate (write to worklog, set status: escalated)

## Outputs

- `worklogs/<branch>/artifacts/research-<timestamp>.md`
- Updated plan file
- Updated `SUMMARY.md`
