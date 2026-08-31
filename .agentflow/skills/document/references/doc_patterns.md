---
type: reference
skill: document
status: active
---

# Documentation Patterns

This document provides guidance on writing high-quality documentation for technical teams.

## The Diataxis Framework

We follow the Diataxis framework, which categorizes documentation into four distinct types:

- **Tutorials**: Learning-oriented. Use when teaching a beginner how to get started.
- **How-Tos**: Task-oriented. Use when helping a user complete a specific task.
- **Explanations**: Understanding-oriented. Use when explaining concepts, architecture, or background.
- **References**: Information-oriented. Use when providing accurate, complete reference material (like API docs).

## Feature Doc Structure

Every feature document should include:
- **Title**: Clear and descriptive.
- **Overview**: What the feature is and why it exists.
- **Key Concepts**: Explanations of new terms or mental models.
- **Usage**: How to use the feature (How-Tos).
- **Configuration**: Options and settings.
- **Troubleshooting**: Common issues and their resolutions.

## Common Doc Anti-Patterns

| Anti-pattern | Consequence | Fix |
| :--- | :--- | :--- |
| **Assuming context** | Readers get lost immediately. | State prerequisites clearly; define acronyms. |
| **Mixing doc types** | Hard to find specific information. | Separate tutorials from reference material. |
| **Stale examples** | Frustrates users when code doesn't work. | Link to tested examples instead of inline blocks. |
| **Wall of text** | Readers skim and miss key points. | Use headers, lists, and bold text for scanning. |

## Code Examples

- **Inline vs Linked**: Use inline examples for very short snippets (1-5 lines). For anything longer, link to a tested file in the `examples/` directory.
- **Keeping Examples Current**: By linking to real files, we ensure examples are tested along with the rest of the codebase.

## Negative Constraints

- Do NOT write documentation that simply repeats the code. Explain *why*, not just *what*.
- Do NOT use passive voice. Use active voice and direct instructions.
- Do NOT skip the overview. Context is critical.
