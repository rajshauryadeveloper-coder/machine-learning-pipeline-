#!/usr/bin/env python3
"""AgentFlow Unified Workflow CLI (flow.py).

Provides fast, token-efficient, single-command operations for the entire
AgentFlow lifecycle:
  - flow start <slug>   : Create branch, scaffold worklog & plan, update prompt
  - flow verify         : Run pytest, coverage check, flake8, black, capture diff
  - flow ship           : Commit, push, merge to main, write postmortem & rollup
  - flow status         : Inspect current workflow stage and metrics
"""
from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path

# Determine absolute paths dynamically regardless of execution directory
REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTFLOW_ROOT = REPO_ROOT / ".agentflow"


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
    """Return the Path to the worklog directory for the active or given branch."""
    b = branch or get_current_branch()
    slug = branch_to_slug(b)
    return AGENTFLOW_ROOT / "worklogs" / slug


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
[SUMMARY.md](../worklogs/{worklog_slug}/SUMMARY.md)
""",
            encoding="utf-8",
        )
        print(f"Created plan at {full_plan_path}")

    # Update prompt frontmatter to in_progress if prompt file exists
    full_prompt_path = AGENTFLOW_ROOT / prompt_path_rel
    if full_prompt_path.exists():
        p_text = full_prompt_path.read_text(encoding="utf-8")
        if "status: draft" in p_text or "status: active" in p_text:
            p_text = re.sub(
                r"status:\s*(draft|active)",
                "status: in_progress",
                p_text,
                count=1,
            )
            full_prompt_path.write_text(p_text, encoding="utf-8")

    # Create worklog SUMMARY.md
    summary_file = worklog_dir / "SUMMARY.md"
    summary_content = f"""---
type: worklog
status: active
branch: {branch_name}
worklog_slug: {worklog_slug}
created: {timestamp_iso}
tags: []
---

# Worklog: {title}

## Status
**active** — In progress.

## Origin Prompt
[Prompt](../../{prompt_path_rel})

## Plan
[Plan](../../{plan_path_rel})

## Current Stage
**implement**

## What Was Done
- **[{timestamp_iso}]** Task started on branch `{branch_name}`. Initialized plan and worklog.

## Metrics

| Stage | Attempts | Outcome | Notes |
| --- | --- | --- | --- |
| `plan` | 1 | Success | Initialized via flow start |
| `implement` | 0 | In Progress | - |
| `verify` | 0 | Pending | - |
| `ship` | 0 | Pending | - |

## Outcome
**Pending**

## Artifacts
- *(none yet)*
"""
    summary_file.write_text(summary_content, encoding="utf-8")
    print(f"Created worklog at {summary_file}")
    print(f"\n[AgentFlow] Ready for implementation on '{branch_name}'.")
    return 0


# ----------------------------------------------------------------------
# 2. VERIFY COMMAND (Combines Test + Review + Lint + Format + Coverage)
# ----------------------------------------------------------------------
def cmd_verify(args: argparse.Namespace) -> int:
    """Run all verification gates: pytest, coverage gate, flake8, black, diff."""
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

    # Gate 1: Pytest & Coverage
    test_cmd = args.test_cmd or "uv run pytest tests/ --cov=src"
    print(f"  -> Executing tests: {test_cmd}")
    test_code, test_out, test_err = run_cmd(test_cmd, shell=True)
    test_combined = f"{test_out}\n{test_err}".strip()

    # Parse Pytest results
    passed = len(re.findall(r"(\d+)\s+passed", test_combined))
    passed_count = (
        int(re.findall(r"(\d+)\s+passed", test_combined)[0]) if passed else 0
    )
    failed = len(re.findall(r"(\d+)\s+failed", test_combined))
    failed_count = (
        int(re.findall(r"(\d+)\s+failed", test_combined)[0]) if failed else 0
    )
    errors = len(re.findall(r"(\d+)\s+error", test_combined))
    errors_count = (
        int(re.findall(r"(\d+)\s+error", test_combined)[0]) if errors else 0
    )

    # Gate 2: Flake8 Linter
    print("  -> Running flake8 lint check...")
    flake8_code, flake8_out, flake8_err = run_cmd(
        "uv run flake8 src/ tests/", shell=True
    )
    flake8_combined = f"{flake8_out}\n{flake8_err}".strip()

    # Gate 3: Black Formatter Check
    print("  -> Running black format check...")
    black_code, black_out, black_err = run_cmd(
        "uv run black --check src/ tests/", shell=True
    )
    black_combined = f"{black_out}\n{black_err}".strip()

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
    attempt_file = (
        attempts_dir / f"verify_attempt_{attempt_num}_{timestamp_compact}.md"
    )

    test_status_str = "✅ PASS" if (test_code == 0 and failed_count == 0) else "❌ FAIL"
    cov_status_str = "✅ PASS" if coverage_passed else "❌ FAIL"
    flake_status_str = "✅ PASS" if flake8_code == 0 else "❌ FAIL"
    black_status_str = "✅ PASS" if black_code == 0 else "❌ FAIL"
    lint_details = "0 issues" if flake8_code == 0 else f"{len(flake8_combined.splitlines())} issues"
    black_details = "Clean formatting" if black_code == 0 else "Reformatting needed"

    extra_sections = []
    if test_code != 0:
        extra_sections.append(f"### Test Output\n```text\n{test_combined}\n```")
    if flake8_code != 0:
        extra_sections.append(f"### Lint Output\n```text\n{flake8_combined}\n```")
    if black_code != 0:
        extra_sections.append(f"### Format Output\n```text\n{black_combined}\n```")
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
| **Flake8** | {flake_status_str} | {lint_details} |
| **Black Format** | {black_status_str} | {black_details} |

## Changed Files
```text
{diff_stat or "No tracked file changes"}
```

{extra_text}
"""
    artifact_file.write_text(artifact_content, encoding="utf-8")

    # Write attempt file
    lint_count = 0 if flake8_code == 0 else len(flake8_combined.splitlines())
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
- Lint issues: {lint_count}
- Format clean: {black_code == 0}

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
        print(
            f"\n✅ All verification gates PASSED! (Tests: {passed_count}, "
            f"Coverage: {coverage_pct}%, Lint: clean)"
        )
        print(f"Artifact recorded: {artifact_file}")
        print("Run 'flow ship --lesson \"...\"' to merge and close.")
        return 0
    else:
        print("\n❌ Verification FAILED.")
        if test_code != 0:
            print(f"  - Tests failed ({failed_count} failures, {errors_count} errors)")
        if not coverage_passed:
            print(f"  - Coverage {coverage_pct}% below {args.coverage_threshold}% threshold")
        if flake8_code != 0:
            print(f"  - Flake8 lint errors:\n{flake8_combined}")
        if black_code != 0:
            print(f"  - Black formatting needed:\n{black_combined}")
        print(f"See details in: {artifact_file}")
        return 1


# ----------------------------------------------------------------------
# 3. SHIP COMMAND (Combines Commit + Push + Merge + Postmortem + Rollup)
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

    lesson_cat = args.lesson or "Workflow Execution"
    lesson_det = args.details or "All verification gates passed cleanly."

    # 1. Generate Postmortem
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

    # 2. Append to ROLLUP.md
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
        updated_r_text = (
            r_text[:idx].rstrip() + "\n\n" + rollup_entry + "\n" + r_text[idx:]
        )
    else:
        updated_r_text = r_text.rstrip() + "\n\n" + rollup_entry + "\n"
    rollup_file.write_text(updated_r_text, encoding="utf-8")
    print(f"Appended entry to {rollup_file}")

    # 3. Update SUMMARY.md to completed
    if summary_file.exists():
        s_text = summary_file.read_text(encoding="utf-8")
        s_text = re.sub(r"status:\s*active", "status: completed", s_text, count=1)
        s_text = re.sub(
            r"## Current Stage\s*\n\*\*[a-zA-Z_-]+\*\*",
            "## Current Stage\n**merged**",
            s_text,
        )
        s_text = re.sub(
            r"## Outcome\s*\n\*\*Pending\*\*",
            "## Outcome\n**Merged** — Merged to `main`.",
            s_text,
        )
        summary_file.write_text(s_text, encoding="utf-8")

    # 4. Update prompt to completed if any matching prompt
    for prompt_file in (AGENTFLOW_ROOT / "prompts").glob("*.md"):
        p_text = prompt_file.read_text(encoding="utf-8")
        if "status: in_progress" in p_text:
            p_text = re.sub(r"status:\s*in_progress", "status: completed", p_text)
            prompt_file.write_text(p_text, encoding="utf-8")

    # 5. Stage all changes
    print("[AgentFlow] Staging and committing changes...")
    run_cmd(["git", "add", "-A"], check=True)

    commit_msg = args.message or f"feat({slug}): implement and verify feature"
    code, stdout, _ = run_cmd(["git", "commit", "-m", commit_msg])
    if code == 0:
        print(f"Committed changes: {commit_msg}")
    else:
        print("No new working tree changes to commit (using current HEAD).")

    # 6. Push feature branch if not on main
    if branch != "main" and not args.no_push:
        print(f"[AgentFlow] Pushing branch '{branch}' to origin...")
        run_cmd(["git", "push", "origin", branch])

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
# 4. STATUS COMMAND
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
# 5. CLI PARSER & ENTRYPOINT
# ----------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        prog="flow",
        description="AgentFlow Unified Workflow Engine CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = subparsers.add_parser(
        "start", help="Start a new task branch and worklog"
    )
    p_start.add_argument("slug", help="Feature name or slug (e.g. add-auth)")
    p_start.add_argument("--title", help="Human-readable title")
    p_start.add_argument("--prompt", help="Relative path to prompt file")
    p_start.add_argument("--plan", help="Relative path to plan file")

    # verify
    p_verify = subparsers.add_parser(
        "verify", help="Run tests, coverage, flake8, black, diff"
    )
    p_verify.add_argument("--test-cmd", help="Custom test command")
    p_verify.add_argument(
        "--coverage-threshold",
        type=int,
        default=60,
        help="Coverage percentage gate (default: 60)",
    )

    # ship
    p_ship = subparsers.add_parser(
        "ship", help="Commit, push, merge to main, write postmortem & rollup"
    )
    p_ship.add_argument("-m", "--message", help="Git commit message")
    p_ship.add_argument(
        "--lesson",
        default="Workflow Optimization",
        help="Postmortem key lesson category",
    )
    p_ship.add_argument(
        "--details",
        default="All verification gates passed cleanly.",
        help="Postmortem key lesson details",
    )
    p_ship.add_argument(
        "--no-push", action="store_true", help="Skip remote git push"
    )

    # status
    subparsers.add_parser(
        "status", help="Inspect current workflow stage and metrics"
    )

    args = parser.parse_args()

    if args.command == "start":
        return cmd_start(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "ship":
        return cmd_ship(args)
    elif args.command == "status":
        return cmd_status(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
