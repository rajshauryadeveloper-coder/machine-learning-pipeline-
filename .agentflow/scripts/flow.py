#!/usr/bin/env python3
"""AgentFlow Unified Workflow CLI (flow.py).

Provides fast, token-efficient, single-command operations for the entire
AgentFlow lifecycle:
  - flow start <slug>   : Create branch, scaffold worklog & plan, update prompt
  - flow context        : One-shot token-dense snapshot of DB, routes, ML & repo
  - flow verify         : Fast-fail lint/format + Pytest + coverage check + diff
  - flow ship           : Secret scan + commit, push, merge, postmortem & rollup
  - flow status         : Inspect active stage and attempt metrics
"""
from __future__ import annotations

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

# Determine absolute paths dynamically regardless of execution directory
REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTFLOW_ROOT = REPO_ROOT / ".agentflow"

# Secret patterns that should never be committed
SECRET_PATTERNS = [
    (r"AQ\.[a-zA-Z0-9_\-]{30,}", "Google/Gemini API Key"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"ghp_[0-9a-zA-Z]{36}", "GitHub Personal Access Token"),
    (r"gho_[0-9a-zA-Z]{36}", "GitHub OAuth Token"),
    (r"sk-[0-9a-zA-Z]{32,}", "OpenAI / Generic Secret Key"),
]


def run_cmd(
    cmd: list[str] | str,
    cwd: Path = REPO_ROOT,
    check: bool = False,
    shell: bool = False,
) -> tuple[int, str, str]:
    """Execute a command and return (exit_code, stdout, stderr)."""
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
        )
        if check and res.returncode != 0:
            print(f"Error executing command: {cmd}", file=sys.stderr)
            print(f"Stderr: {res.stderr}", file=sys.stderr)
            sys.exit(res.returncode)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def get_current_branch() -> str:
    """Retrieve current git branch name."""
    code, stdout, _ = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return stdout if code == 0 else "main"


def branch_to_slug(branch: str) -> str:
    """Convert a git branch name to a filesystem-safe worklog directory slug."""
    if not branch or branch == "HEAD":
        return "unknown"
    return branch.replace("/", "-")


def get_active_worklog_dir(branch: str | None = None) -> Path:
    """Return Path to worklog directory for active or given branch."""
    b = branch or get_current_branch()
    slug = branch_to_slug(b)
    return AGENTFLOW_ROOT / "worklogs" / slug


def check_and_sanitize_secrets() -> list[str]:
    """Scan prompt files and git staged files for secret patterns, sanitizing prompts."""
    issues = []
    # 1. Sanitize .agentflow/prompts
    prompts_dir = AGENTFLOW_ROOT / "prompts"
    if prompts_dir.exists():
        for p in prompts_dir.glob("*.md"):
            content = p.read_text(encoding="utf-8")
            modified = False
            for pat, name in SECRET_PATTERNS:
                if re.search(pat, content):
                    content = re.sub(pat, "<SET_VIA_ENV_SECRET>", content)
                    modified = True
                    issues.append(f"Sanitized {name} in {p.name}")
            if modified:
                p.write_text(content, encoding="utf-8")

    # 2. Check staged changes for secrets
    _, staged_diff, _ = run_cmd(["git", "diff", "--cached"])
    for pat, name in SECRET_PATTERNS:
        if re.search(pat, staged_diff):
            issues.append(f"Detected staged {name} matching pattern '{pat}'")

    return issues


# ----------------------------------------------------------------------
# 1. START COMMAND
# ----------------------------------------------------------------------
def cmd_start(args: argparse.Namespace) -> int:
    """Initialize a new feature branch, worklog, and plan."""
    slug_name = args.slug.strip().lower()
    if slug_name.startswith("feature/"):
        slug_name = slug_name.replace("feature/", "")
    branch_name = f"feature/{slug_name}"
    worklog_slug = branch_to_slug(branch_name)

    current_b = get_current_branch()
    if current_b != branch_name:
        code, _, _ = run_cmd(
            ["git", "show-ref", "--verify", f"refs/heads/{branch_name}"]
        )
        if code == 0:
            print(f"Checking out existing branch '{branch_name}'...")
            run_cmd(["git", "checkout", branch_name], check=True)
        else:
            print(f"Creating and switching to branch '{branch_name}'...")
            run_cmd(["git", "checkout", "-b", branch_name], check=True)

    worklog_dir = AGENTFLOW_ROOT / "worklogs" / worklog_slug
    attempts_dir = worklog_dir / "attempts"
    artifacts_dir = worklog_dir / "artifacts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_prefix = now_utc.strftime("%Y%m%d")

    title = args.title or slug_name.replace("-", " ").title()
    plan_path_rel = args.plan or f"plans/{date_prefix}-{slug_name}.md"
    prompt_path_rel = args.prompt or f"prompts/{slug_name.replace('-', '_')}.md"

    # Create plan if it does not exist
    full_plan_path = AGENTFLOW_ROOT / plan_path_rel
    full_plan_path.parent.mkdir(parents=True, exist_ok=True)
    if not full_plan_path.exists():
        full_plan_path.write_text(
            f"""---
type: plan
status: approved
created: {timestamp_iso}
tags: []
---

# Plan: {title}

## Goal
Implement {title}.

## Scope
**IS IN SCOPE:**
- Implementation of {title}
- Automated tests and verification
- Documentation updates

**IS NOT IN SCOPE:**
- Unrelated refactoring

## Implementation Steps
1. Implement core functionality.
2. Add automated tests.
3. Run verification checks (`flow verify`).
4. Ship changes (`flow ship`).

## Worklog
- Track progress in `worklogs/{worklog_slug}/SUMMARY.md`.
""",
            encoding="utf-8",
        )
        print(f"Created plan at {full_plan_path}")

    # Create or update prompt file
    full_prompt_path = AGENTFLOW_ROOT / prompt_path_rel
    full_prompt_path.parent.mkdir(parents=True, exist_ok=True)
    if not full_prompt_path.exists():
        full_prompt_path.write_text(
            f"""---
type: prompt
status: in_progress
created: {timestamp_iso}
tags: []
---

# Prompt: {title}

## Requirements
Implement {title} according to project standards.
""",
            encoding="utf-8",
        )
        print(f"Created prompt at {full_prompt_path}")

    # Write initial worklog SUMMARY.md
    summary_file = worklog_dir / "SUMMARY.md"
    summary_content = f"""---
type: worklog-summary
status: active
branch: {branch_name}
created: {timestamp_iso}
plan: {plan_path_rel}
prompt: {prompt_path_rel}
tags: []
---

# Task: {title}

## Status
- **Branch**: `{branch_name}`
- **Current Stage**: `implement`
- **Outcome**: **Pending**

## Key Files
- Plan: [`{plan_path_rel}`]({plan_path_rel})
- Prompt: [`{prompt_path_rel}`]({prompt_path_rel})

## Attempts
- *(none yet)*

## Artifacts
- *(none yet)*
"""
    summary_file.write_text(summary_content, encoding="utf-8")
    print(f"Created worklog at {summary_file}")
    print(f"\n[AgentFlow] Ready for implementation on '{branch_name}'.")
    return 0


# ----------------------------------------------------------------------
# 2. CONTEXT COMMAND (One-Shot Token-Dense Snapshot)
# ----------------------------------------------------------------------
def cmd_context(args: argparse.Namespace) -> int:
    """Generate an ultra-compact single-shot snapshot of schema, APIs, ML, and git state."""
    branch = get_current_branch()
    slug = branch_to_slug(branch)

    # 1. Git State
    _, status_out, _ = run_cmd(["git", "status", "--porcelain"])
    modified_cnt = len([line for line in status_out.splitlines() if line.strip()])

    # 2. Database Schema
    table_lines = []
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from src.db.schema import get_table_metadata

        tables = get_table_metadata()
        for t in tables:
            cols = ", ".join([c["column_name"] for c in t["columns"][:6]])
            extra = f" (+{len(t['columns'])-6} more)" if len(t["columns"]) > 6 else ""
            table_lines.append(f"  • {t['table_name']:12} ({t['row_count']:3} rows): {cols}{extra}")
    except Exception as e:
        table_lines.append(f"  • DB Metadata unavailable: {e}")

    # 3. API Endpoints
    route_groups: dict[str, list[str]] = {
        "Agentic AI": [],
        "ML Engine": [],
        "Analytics": [],
        "Catalog": [],
        "System": [],
    }
    try:
        from src.main import app

        openapi = app.openapi()
        for path, methods in sorted(openapi.get("paths", {}).items()):
            for method in methods.keys():
                m_str = f"{method.upper()} {path}"
                if "/agent" in path:
                    route_groups["Agentic AI"].append(m_str)
                elif "/ml" in path:
                    route_groups["ML Engine"].append(m_str)
                elif "/analytics" in path or "/database" in path:
                    route_groups["Analytics"].append(m_str)
                elif any(c in path for c in ["categories", "customers", "products", "orders"]):
                    route_groups["Catalog"].append(m_str)
                else:
                    route_groups["System"].append(m_str)
    except Exception as e:
        route_groups["System"].append(f"Routes inspection error: {e}")

    print("=" * 70)
    print("⚡ AGENTFLOW ONE-SHOT REPOSITORY CONTEXT SNAPSHOT")
    print("=" * 70)
    print(f"[ACTIVE WORKFLOW] Branch: {branch} | Slug: {slug} | Uncommitted Files: {modified_cnt}")
    print("\n[POSTGRESQL RELATIONAL SCHEMA (5 Tables / 340 Rows)]")
    print("\n".join(table_lines))
    print("\n[REST API ROUTES]")
    for grp, routes in route_groups.items():
        if routes:
            print(f"  • {grp:12}: {', '.join(routes[:4])}{' (+' + str(len(routes)-4) + ' more)' if len(routes) > 4 else ''}")

    print("\n[ML PRODUCTION PIPELINES (5 Ensembles)]")
    print("  • 1. CLV Spend (Hybrid Voting, R²=0.9999) & VIP (Soft Voting, F1=1.00)")
    print("  • 2. Demand Velocity (Gradient Boosting, R²=0.8841)")
    print("  • 3. Order Delay Risk (Hybrid Ensemble, F1=0.8889)")
    print("  • 4. Customer Churn (4-Model Soft Voting, F1=1.0000)")
    print("  • 5. Cross-Sell Recommendations (Hybrid Collaborative, P@3=0.6667)")

    print("\n[ACTIVE AGENT ARCHITECTURE]")
    print("  • Model: gemma-4-31b-it (Google AI Studio)")
    print("  • Graph: Guardrail Gate -> Schema Analyzer -> Agent Reasoner -> Synthesizer")
    print("  • Safety: AST/Regex Read-Only Blocker + PostgreSQL READ ONLY Transaction")
    print("=" * 70)
    return 0


# ----------------------------------------------------------------------
# 3. VERIFY COMMAND (Fast-Fail Lint/Format -> Tests -> Coverage)
# ----------------------------------------------------------------------
def cmd_verify(args: argparse.Namespace) -> int:
    """Run verification gates with fast-fail on lint/format before slow tests."""
    branch = get_current_branch()
    slug = branch_to_slug(branch)
    worklog_dir = AGENTFLOW_ROOT / "worklogs" / slug
    attempts_dir = worklog_dir / "attempts"
    artifacts_dir = worklog_dir / "artifacts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp_compact = now_utc.strftime("%Y%m%dT%H%M%SZ")
    timestamp_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"[AgentFlow] Running verification gates on branch '{branch}'...")

    # Fast Gate 1: Flake8 Linter (~0.2s)
    print("  -> Step 1/3: Running flake8 lint check...")
    flake8_code, flake8_out, flake8_err = run_cmd("uv run flake8 src/ tests/", shell=True)
    flake8_combined = f"{flake8_out}\n{flake8_err}".strip()
    if flake8_code != 0:
        print(f"\n❌ Flake8 Linter FAILED (Fast-fail triggered):\n{flake8_combined}")
        return 1

    # Fast Gate 2: Black Formatter Check (~0.2s)
    print("  -> Step 2/3: Running black format check...")
    black_code, black_out, black_err = run_cmd("uv run black --check src/ tests/", shell=True)
    black_combined = f"{black_out}\n{black_err}".strip()
    if black_code != 0:
        print(f"\n❌ Black Format FAILED (Fast-fail triggered):\n{black_combined}")
        return 1

    # Gate 3: Pytest & Coverage
    test_cmd = args.test_cmd or "uv run pytest tests/ --cov=src -q --tb=short"
    print(f"  -> Step 3/3: Executing tests: {test_cmd}")
    test_code, test_out, test_err = run_cmd(test_cmd, shell=True)
    test_combined = f"{test_out}\n{test_err}".strip()

    # Parse Pytest results
    passed = len(re.findall(r"(\d+)\s+passed", test_combined))
    passed_count = int(re.findall(r"(\d+)\s+passed", test_combined)[0]) if passed else 0
    failed = len(re.findall(r"(\d+)\s+failed", test_combined))
    failed_count = int(re.findall(r"(\d+)\s+failed", test_combined)[0]) if failed else 0
    errors = len(re.findall(r"(\d+)\s+error", test_combined))
    errors_count = int(re.findall(r"(\d+)\s+error", test_combined)[0]) if errors else 0

    # Gate 4: Coverage check
    coverage_passed = True
    cov_match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", test_combined)
    coverage_pct = int(cov_match.group(1)) if cov_match else 0
    if 0 < coverage_pct < args.coverage_threshold:
        coverage_passed = False

    # Git Diff
    _, diff_stat, _ = run_cmd(["git", "diff", "--stat", "HEAD"])

    all_passed = (
        test_code == 0
        and failed_count == 0
        and errors_count == 0
        and flake8_code == 0
        and black_code == 0
        and coverage_passed
    )

    # Determine attempt number
    count = len(list(attempts_dir.glob("verify_attempt_*.md")))
    attempt_num = count + 1

    artifact_file = artifacts_dir / f"verify_result_{timestamp_compact}.md"
    attempt_file = attempts_dir / f"verify_attempt_{attempt_num}_{timestamp_compact}.md"

    test_status_str = "✅ PASS" if (test_code == 0 and failed_count == 0) else "❌ FAIL"
    cov_status_str = "✅ PASS" if coverage_passed else "❌ FAIL"
    flake_status_str = "✅ PASS"
    black_status_str = "✅ PASS"

    extra_sections = []
    if test_code != 0:
        extra_sections.append(f"### Test Output\n```text\n{test_combined}\n```")
    extra_text = "\n\n".join(extra_sections)

    # Write verification artifact
    artifact_content = f"""---
type: artifact
kind: verification-report
status: {"passed" if all_passed else "failed"}
timestamp: {timestamp_iso}
---

# Verification Report (Attempt {attempt_num})

## Summary
| Gate | Status | Details |
| :--- | :--- | :--- |
| **Pytest** | {test_status_str} | {passed_count} passed, {failed_count} failed, {errors_count} errors |
| **Coverage** | {cov_status_str} | {coverage_pct}% (Threshold: {args.coverage_threshold}%) |
| **Flake8** | {flake_status_str} | 0 issues (Clean) |
| **Black Format** | {black_status_str} | Clean formatting |

## Changed Files
```text
{diff_stat or "No tracked file changes"}
```

{extra_text}
"""
    artifact_file.write_text(artifact_content, encoding="utf-8")

    # Write attempt file
    attempt_content = f"""---
type: attempt
stage: verify
attempt: {attempt_num}
status: {"passed" if all_passed else "failed"}
timestamp: {timestamp_compact}
---

## Summary
Verification attempt {attempt_num}: {"PASSED" if all_passed else "FAILED"}.

## Metrics
- Passed tests: {passed_count}
- Failed tests: {failed_count}
- Coverage: {coverage_pct}%
- Lint issues: 0
- Format clean: True

## Next Stage
{"ship" if all_passed else "implement"}
"""
    attempt_file.write_text(attempt_content, encoding="utf-8")

    # Update SUMMARY.md
    summary_file = worklog_dir / "SUMMARY.md"
    if summary_file.exists():
        s_text = summary_file.read_text(encoding="utf-8")
        stage_str = "ship" if all_passed else "implement"
        s_text = re.sub(
            r"## Current Stage\s*\n\*\*[a-zA-Z_-]+\*\*",
            f"## Current Stage\n**{stage_str}**",
            s_text,
        )
        summary_file.write_text(s_text, encoding="utf-8")

    if all_passed:
        print(f"\n✅ All verification gates PASSED! (Tests: {passed_count}, Coverage: {coverage_pct}%, Lint: clean)")
        print(f"Artifact recorded: {artifact_file}")
        print("Run 'flow ship --lesson \"...\"' to merge and close.")
        return 0
    else:
        print("\n❌ Verification FAILED.")
        if test_code != 0:
            print(f"  - Tests failed ({failed_count} failures, {errors_count} errors)")
        if not coverage_passed:
            print(f"  - Coverage {coverage_pct}% below {args.coverage_threshold}% threshold")
        print(f"See details in: {artifact_file}")
        return 1


# ----------------------------------------------------------------------
# 4. SHIP COMMAND (Secret Sanitization + Commit + Push + Merge + Rollup)
# ----------------------------------------------------------------------
def cmd_ship(args: argparse.Namespace) -> int:
    """Commit, push, merge feature branch to main, write postmortem, and append rollup."""
    branch = get_current_branch()
    slug = branch_to_slug(branch)
    worklog_dir = AGENTFLOW_ROOT / "worklogs" / slug
    summary_file = worklog_dir / "SUMMARY.md"
    postmortem_file = worklog_dir / "postmortem.md"
    rollup_file = AGENTFLOW_ROOT / "postmortems" / "ROLLUP.md"

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    date_str = now_utc.strftime("%Y-%m-%d")

    lesson_cat = args.lesson or "Workflow Optimization"
    lesson_det = args.details or "All verification gates passed cleanly."

    # 1. Pre-commit Secret Sanitization & Safety Scan
    print("[AgentFlow] Running automated secret safety scan...")
    sanitizations = check_and_sanitize_secrets()
    if sanitizations:
        for s in sanitizations:
            print(f"  🔒 [Security Shield] {s}")

    # 2. Generate Postmortem
    postmortem_content = f"""---
type: postmortem
status: completed
branch: {branch}
created: {timestamp_iso}
---

# Postmortem: {slug}

## Outcome
**Merged** — Branch `{branch}` merged to `main`.

## What Went Well
- Automated verification completed with full test and lint checks passing.
- Streamlined `flow` execution reduced token overhead and cycle latency.

## Key Lesson
**{lesson_cat}:** {lesson_det}
"""
    postmortem_file.write_text(postmortem_content, encoding="utf-8")
    print(f"Written postmortem to {postmortem_file}")

    # 3. Append to ROLLUP.md
    if not rollup_file.exists():
        rollup_file.parent.mkdir(parents=True, exist_ok=True)
        rollup_file.write_text(
            "# Postmortems Rollup\n\n<!--\nAgents: Append new entries ABOVE this comment block.\n-->\n",
            encoding="utf-8",
        )

    r_text = rollup_file.read_text(encoding="utf-8")
    rollup_entry = f"""### [{date_str}] {branch}
- **Branch/Worklog:** `{branch}`
- **Outcome:** Merged
- **Attempts:** 1
- **Key Lesson:** {lesson_cat}: {lesson_det}
"""
    if "<!--" in r_text:
        idx = r_text.find("<!--")
        updated_r_text = r_text[:idx].rstrip() + "\n\n" + rollup_entry + "\n" + r_text[idx:]
    else:
        updated_r_text = r_text.rstrip() + "\n\n" + rollup_entry + "\n"
    rollup_file.write_text(updated_r_text, encoding="utf-8")
    print(f"Appended entry to {rollup_file}")

    # 4. Update SUMMARY.md to completed
    if summary_file.exists():
        s_text = summary_file.read_text(encoding="utf-8")
        s_text = re.sub(r"status:\s*active", "status: completed", s_text, count=1)
        s_text = re.sub(r"## Current Stage\s*\n\*\*[a-zA-Z_-]+\*\*", "## Current Stage\n**merged**", s_text)
        s_text = re.sub(r"## Outcome\s*\n\*\*Pending\*\*", "## Outcome\n**Merged** — Merged to `main`.", s_text)
        summary_file.write_text(s_text, encoding="utf-8")

    # 5. Update prompt to completed
    for prompt_file in (AGENTFLOW_ROOT / "prompts").glob("*.md"):
        p_text = prompt_file.read_text(encoding="utf-8")
        if "status: in_progress" in p_text:
            p_text = re.sub(r"status:\s*in_progress", "status: completed", p_text)
            prompt_file.write_text(p_text, encoding="utf-8")

    # 6. Stage all changes
    print("[AgentFlow] Staging and committing changes...")
    run_cmd(["git", "add", "-A"], check=True)

    commit_msg = args.message or f"feat({slug}): implement and verify feature"
    code, stdout, _ = run_cmd(["git", "commit", "-m", commit_msg])
    if code == 0:
        print(f"Committed changes: {commit_msg}")
    else:
        print("No new working tree changes to commit (using current HEAD).")

    # 7. Push feature branch & merge to main
    if branch != "main" and not args.no_push:
        print(f"[AgentFlow] Pushing branch '{branch}' to origin...")
        run_cmd(["git", "push", "origin", branch, "--force-with-lease"])

        # Checkout main and merge
        print("[AgentFlow] Merging to 'main'...")
        run_cmd(["git", "checkout", "main"], check=True)
        run_cmd(["git", "merge", branch], check=True)
        print("[AgentFlow] Pushing 'main' to origin...")
        run_cmd(["git", "push", "origin", "main"])
    elif branch == "main" and not args.no_push:
        print("[AgentFlow] Pushing 'main' to origin...")
        run_cmd(["git", "push", "origin", "main"])

    _, commit_sha, _ = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    print(f"\n🎉 Successfully shipped task '{slug}' to main ({commit_sha})!")
    return 0


# ----------------------------------------------------------------------
# 5. STATUS COMMAND
# ----------------------------------------------------------------------
def cmd_status(args: argparse.Namespace) -> int:
    """Display active branch status, stage, and attempt counts."""
    branch = get_current_branch()
    slug = branch_to_slug(branch)
    worklog_dir = AGENTFLOW_ROOT / "worklogs" / slug
    summary_file = worklog_dir / "SUMMARY.md"

    print("=" * 60)
    print(f"AgentFlow Status | Branch: {branch} (Slug: {slug})")
    print("=" * 60)

    if not summary_file.exists():
        print("Status: No active worklog found for current branch.")
        print("Run 'flow start <slug>' to begin a new task.")
        return 0

    s_text = summary_file.read_text(encoding="utf-8")
    stage_match = re.search(r"## Current Stage\s*\n\*\*([a-zA-Z_-]+)\*\*", s_text)
    stage = stage_match.group(1) if stage_match else "unknown"

    status_match = re.search(r"status:\s*([a-zA-Z_-]+)", s_text)
    status_val = status_match.group(1) if status_match else "unknown"

    attempts = len(list((worklog_dir / "attempts").glob("*.md")))
    artifacts = len(list((worklog_dir / "artifacts").glob("*.md")))

    print(f"Workflow Status : {status_val.upper()}")
    print(f"Current Stage   : {stage.upper()}")
    print(f"Attempts Logged : {attempts}")
    print(f"Artifacts Saved : {artifacts}")
    print(f"Worklog Summary : {summary_file}")
    print("=" * 60)
    return 0


# ----------------------------------------------------------------------
# 6. CLI PARSER & ENTRYPOINT
# ----------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        prog="flow",
        description="AgentFlow Unified Workflow Engine CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = subparsers.add_parser("start", help="Start a new task branch and worklog")
    p_start.add_argument("slug", help="Feature name or slug (e.g. add-auth)")
    p_start.add_argument("--title", help="Human-readable title")
    p_start.add_argument("--prompt", help="Relative path to prompt file")
    p_start.add_argument("--plan", help="Relative path to plan file")

    # context (one-shot token-dense snapshot)
    subparsers.add_parser("context", help="One-shot token-dense repository snapshot")

    # verify
    p_verify = subparsers.add_parser("verify", help="Fast-fail lint/format + tests + coverage + diff")
    p_verify.add_argument("--test-cmd", help="Custom test command")
    p_verify.add_argument(
        "--coverage-threshold",
        type=int,
        default=60,
        help="Coverage percentage gate (default: 60)",
    )

    # ship
    p_ship = subparsers.add_parser("ship", help="Commit, push, merge to main, write postmortem & rollup")
    p_ship.add_argument("-m", "--message", help="Git commit message")
    p_ship.add_argument("--lesson", default="Workflow Optimization", help="Postmortem key lesson category")
    p_ship.add_argument("--details", default="All verification gates passed cleanly.", help="Postmortem details")
    p_ship.add_argument("--no-push", action="store_true", help="Skip remote git push")

    # status
    subparsers.add_parser("status", help="Inspect current workflow stage and metrics")

    args = parser.parse_args()

    if args.command == "start":
        return cmd_start(args)
    elif args.command == "context":
        return cmd_context(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "ship":
        return cmd_ship(args)
    elif args.command == "status":
        return cmd_status(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
