---
type: reference
skill: implement
status: active
---

# Implementation Planning Reference

## What Makes a Good Plan
- **One Goal Per Plan**: Focus on a single outcome or feature to prevent scope creep.
- **Explicit File Listing**: List every file intended for modification before executing changes.
- **Risk Assessment**: Estimate the risk level for each touched file or architectural seam.

## Plan Anti-Patterns

| Anti-pattern | Consequence | Fix |
|---|---|---|
| "Rewrite module" | High regression risk, massive diffs | Target specific functions, leave rest intact |
| Vague dependencies | Unexpected breaks during execution | Map out call graphs in the plan explicitly |
| No rollback strategy | Stuck agents, corrupted state | Define checkpoints and specific git revert commands |

## Risk Matrix Template

| File/Component | Change Type | Risk Level | Mitigation |
|---|---|---|---|
| `auth/login.py` | Add OAuth scope | High | Write unit tests first, mock provider |
| `ui/button.tsx` | Styling update | Low | Visual verification only |

## Definition of Done

- [ ] All target files modified according to plan
- [ ] No unrelated files or formatting touched
- [ ] Commit history is logical and cleanly separated
- [ ] Tests pass (if applicable in this stage)
- [ ] Next steps clearly identified for the `test` or `review` stage

## Plan Review Questions
- Is the scope strictly limited to the required feature?
- Are negative constraints explicitly handled?
- Are the target file paths absolutely correct?
- Do we have enough context to implement without guessing?
