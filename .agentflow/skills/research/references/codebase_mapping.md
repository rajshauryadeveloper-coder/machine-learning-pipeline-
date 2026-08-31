---
type: reference
skill: research
status: active
---

# Codebase Mapping Guide

Use this guide when stepping into an unfamiliar codebase or a module you haven't touched before. Effective codebase mapping reduces regressions and prevents "blind spot" architectural mistakes.

## Orientation Checklist

Before proposing changes, ensure you have completed the following:
- [ ] Find the entry points (e.g., `main.py`, `index.ts`, `app.go`, or route definitions).
- [ ] Trace the core data flow for the relevant feature (from input to persistence).
- [ ] Identify where the test coverage lives and what testing framework is used.
- [ ] Read the recent git log for the files you plan to modify.
- [ ] Find the related configuration files or environment variable definitions.

## Codebase Smell Detector

Note these in your research brief if encountered:

| Smell | Implication | What to Note in Brief |
|-------|-------------|-----------------------|
| Massive God Classes | High risk of unintended side effects. | Flag for careful regression testing; suggest isolating changes. |
| Scattered Config | Hard to trace where settings originate. | List all files that control the feature's configuration. |
| Missing Tests | Changes are unsafe to make blindly. | Recommend writing a minimal test harness before implementation. |
| Dead Code | You might be studying unused logic. | Verify the code path is actually reachable before relying on it. |

## Dependency Graph Approach

To quickly map how files relate:
1. Start at the target file or function.
2. Search globally (`grep`) for all imports or invocations of that target.
3. Search the target itself to see what external services or internal modules it relies on.
4. Document this in the brief as "Upstream Dependents" (things that call this) and "Downstream Dependencies" (things this calls).

## High-Impact vs Low-Risk Change Zones

- **High-Impact Zones**: Core models, shared utilities, database migration scripts, authentication middleware. *Requires deep research and human review.*
- **Low-Risk Zones**: Isolated UI components, localized helper functions, leaf nodes in the dependency graph. *Standard research is sufficient.*

## Questions to Answer Before Implementing
- What are the existing patterns for error handling and logging in this module?
- Is state managed locally, or is there a global state management system in play?
- Are there any undocumented conventions (e.g., specific naming schemas or folder structures) that must be followed?
- Which existing tests can serve as a template for the new functionality?
