---
name: ship
status: active
chain_to: null
tags: [ship, commit, push, merge, postmortem, secret-shield]
---
# Ship Skill (v3 High-Speed)

## Goal
Atomically scan for secrets, commit, push branch, merge to `main`, and log postmortem rollup.

## Command
```bash
./scripts/flow ship -m "feat(slug): description" --lesson "Category" --details "Details"
```

## Automated Operations
1. **Secret Scanning**: Scans staged changes and sanitizes `.agentflow/prompts` to prevent GitHub Push Protection blocks.
2. **Commit & Push**: Commits working tree and pushes feature branch.
3. **Merge & Sync**: Switches to `main`, merges feature branch, and pushes `main` to origin.
4. **Postmortem & Rollup**: Generates `worklogs/<slug>/postmortem.md` and appends to `postmortems/ROLLUP.md`.
