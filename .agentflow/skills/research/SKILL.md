---
name: research
status: active
chain_to: implement
tags: [research, explore, context]
---
# Research Skill (v3 High-Speed)

## Goal
Targeted codebase, schema, and API exploration using single-shot context and subagents.

## Commands
```bash
./scripts/flow context   # Capture full DB schema, API routes, and ML state in 1 shot
```

## Guidelines
- Avoid reading entire directories or large context documentation into main memory.
- Prefer targeted `grep_search` and `./scripts/flow context` over broad tree walks.
- Deploy read-only subagents for large external documentation repositories.
