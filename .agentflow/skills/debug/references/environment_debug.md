---
type: reference
skill: debug
status: active
---

# Environment Debugging Reference

Use this reference when test failures seem unrelated to the code logic, or when failures happen in CI but not locally (or vice versa).

## Environment Checklist

When debugging an environment issue, verify:
- [ ] Python/Node version matches the `AGENT_CONTEXT.md` specification
- [ ] Virtual environment is active and isolated
- [ ] All dependencies are installed and up-to-date
- [ ] Environment variables (.env files, CI secrets) are correctly set
- [ ] Required background services (databases, redis) are running
- [ ] Ports required by tests are available and not blocked

## Common Environment Failures

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError` | Virtual environment inactive or package missing | Activate venv, run `pip install -r requirements.txt` or equivalent |
| SyntaxError on valid code | Wrong Python/Node version (e.g. using new features on old runtime) | Check `python --version` and align with project specs |
| Missing `.env` / Config | Setup script wasn't run or file is gitignored | Copy `.env.example` to `.env` or set mock vars in tests |
| "Address already in use" | Port is bound by a zombie process or another app | Find the PID using `lsof -i:<port>` and kill it, or use dynamic ports |
| SSL Certificate Error | Outdated system certificates or proxy interference | Update certificates (`certifi`), bypass proxies for localhost |
| Wrong Working Directory | Test runner is executing from the wrong root | Ensure commands are run from the project root |

## Isolation Test

To confirm an environment issue, run an isolation test:
1. Create a minimal script outside the test suite that just imports the failing module.
2. Run it in a completely clean environment (e.g., a fresh docker container or a new virtual environment).
3. If it fails there too, the problem is likely missing dependencies or global state assumptions.

## Dependency Conflict Detection

Run these commands to verify dependency health:
- Python: `pip check` (detects broken requirements)
- Python: `pip freeze` (compare with known good state)
- Node: `npm ls` or `yarn why` (finds conflicting peer dependencies)

## When to Escalate Environment Issues

Escalate to the user (via `SUMMARY.md` or directly) if:
- A required port is consistently blocked by a system service you cannot kill.
- A required database/service image fails to pull or start due to Docker permission issues.
- The project requires an explicit CI secret or token that is not documented or available.
- After running `pip check` or `npm ls`, there is an unresolvable version conflict that requires architectural decisions.
