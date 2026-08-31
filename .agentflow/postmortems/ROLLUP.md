---
type: rollup
status: active
created: 2026-08-31T16:23:00Z
---

# Postmortem & Learnings Rollup

*A continuous log of completed tasks, failures, and agent learnings to improve future iterations.*

## Format for Entries

```markdown
### [YYYY-MM-DD] Task Title
- **Branch/Worklog:** `branch-name` / [Worklog Link](../worklogs/task_worklog.md)
- **Outcome:** [Merged | Escalated | Abandoned]
- **Attempts:** [Number of implement/test cycles]
- **Key Lesson:** [1-2 sentences on what the agent learned, what failed, or what could be optimized next time]
```

---

### [2026-08-25] Add JWT Authentication Middleware
- **Branch/Worklog:** `feature/add-auth` / [Worklog Link](../worklogs/add_auth_middleware.md)
- **Outcome:** Merged
- **Attempts:** 3
- **Key Lesson:** The agent initially failed because it mocked the `PyJWT` decode function incorrectly in `test_middleware.py`. It learned that it must ensure test mocks align strictly with the external library's actual exception hierarchy (e.g., catching `jwt.ExpiredSignatureError` specifically rather than a generic Exception). Future authentication tasks should reference these mock structures.

<!-- 
Agents: Append new entries ABOVE this comment block, keeping the most recent entries at the top. Use the format specified above.
-->
