---
type: skill
name: document
version: 1.0.0
status: active
created: 2026-08-31T16:23:00Z
chain_to: null
chain_on_failure: null
tags: [document, docs]
---

# Document Skill

This skill handles the creation and updating of documentation for features, architecture decisions, and external resources.

## Routing & Reference Table

| Reference | When to Use |
| :--- | :--- |
| `references/doc_patterns.md` | When structuring new docs. |
| `references/architecture_templates.md` | When documenting system-level decisions. |

## When to Invoke

This is an **ON-DEMAND** skill. Invoke it when:
- A feature is complete and needs user-facing docs.
- An architectural decision needs recording.
- External docs need summarizing for the team.

## Inputs

| Input | Description |
| :--- | :--- |
| Feature worklog | What was built and why. |
| Source code | The code changes made. |
| `docs-generated/_TEMPLATE.md` | The template for new documentation. |
| `sources.yaml` | For external doc references. |

## Hook Scripts

| Script | Purpose | Language |
| :--- | :--- | :--- |
| `scaffold_doc.sh` | Creates a doc stub from the template. | Bash (swappable) |
| `link_doc.py` | Updates the worklog with doc links. | Python (swappable) |

## Steps

1. **Scaffold Doc**: Run `scaffold_doc.sh` with `TOPIC_SLUG` to create a stub at `docs-generated/<topic-slug>/README.md`.
2. **Review Material**: Read the feature worklog and source code to understand the changes.
3. **Write Documentation**: Write the documentation in the newly created stub, following the structure in `docs-generated/_TEMPLATE.md`. Use `references/doc_patterns.md` for guidance.
4. **Architecture Decisions**: For architecture decisions, add an ADR section (see `references/architecture_templates.md`).
5. **Link Doc**: Run `link_doc.py` to update the worklog `SUMMARY.md` with the new doc link.

## Pre-Check

- Target feature/topic exists and has source material.
- `docs-generated/_TEMPLATE.md` is readable.

## Post-Complete

- Documentation is filed under `docs-generated/`.
- A link to the new documentation is added to the worklog.

## Chain

This skill is **standalone**. There is no automatic next skill.

## Outputs

- A new documentation file under `docs-generated/<topic-slug>/README.md`.
- Updated worklog `SUMMARY.md` with a link to the documentation.
