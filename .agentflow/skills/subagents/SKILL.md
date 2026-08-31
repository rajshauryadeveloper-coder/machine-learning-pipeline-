---
name: subagents
status: active
chain_to: null
tags: [subagents, context-isolation, model-tiering, parallel-execution]
---
# Subagent Orchestration Skill (v3 High-Speed)

## Goal
Manage hierarchical supervisor-subagent delegation to maintain the 20–30% Context Smart Zone, isolate non-dependent parallel exploratory work, and route model tiers dynamically for maximum token efficiency.

## 1. The 20–30% Context "Smart Zone" Rule
- **Threshold**: Never allow the supervisor/parent context to exceed **20% to 30%** of max capacity (e.g. max 200k–300k tokens in a 1M token window).
- **Enforcement**: If an exploratory task requires reading multiple large files, extensive web pages, or multi-turn test debugging, **delegate immediately to a subagent**.
- **Discard Scratchpad**: All noisy intermediate outputs (raw tool responses, failed trial iterations) remain isolated inside the subagent context and are discarded upon termination.

## 2. When to Invoke Subagents
| Trigger | Example Scenario | Concurrency |
| :--- | :--- | :--- |
| **Parallel Non-Dependent Tasks** | Subagent A researches external docs while Subagent B audits DB schema | Concurrent (`invoke_subagent`) |
| **Noisy File / Log Exploration** | Searching through hundreds of log lines or multi-MB source files | Isolated Subagent |
| **External Documentation Crawling** | Traversing extensive GitHub markdown doc repositories | Read-only Subagent |
| **Isolated Experimentation** | Benchmarking 5 model hyperparameters without polluting main context | Sandboxed Subagent |

## 3. Dynamic Model Tiering Strategy
When invoking subagents with `invoke_subagent`, choose the model tier according to task complexity:

| Tier | Model Parameter | Ideal Use Case | Token Cost Efficiency |
| :--- | :--- | :--- | :--- |
| **`flash_lite`** | `Model: 'flash_lite'` | String regex, keyword scans, ping/health checks | 95% token savings |
| **`flash`** | `Model: 'flash'` | Codebase exploration, file lookups, doc reading, API audits | 85% token savings |
| **`pro`** | `Model: 'pro'` | Complex mathematical modeling, multi-file refactoring | Deep reasoning |
| **`inherit`** | `Model: 'inherit'` | Exact continuation of parent supervisor | Default |

## 4. Invocation & Boundary Distillation
1. **Launch**:
   ```json
   {
     "Subagents": [
       {
         "TypeName": "research",
         "Role": "Documentation Specialist",
         "Model": "flash",
         "Prompt": "Extract the specific LCEL routing syntax from langchain-docs without conversational filler."
       }
     ]
   }
   ```
2. **Summarize at Boundary**: Subagents return only distilled findings or structured JSON across the context boundary.
