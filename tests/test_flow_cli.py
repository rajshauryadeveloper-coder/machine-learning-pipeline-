import importlib.util
from pathlib import Path

# Load flow.py module dynamically
flow_path = (
    Path(__file__).resolve().parent.parent / ".agentflow" / "scripts" / "flow.py"
)
spec = importlib.util.spec_from_file_location("flow", flow_path)
flow = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(flow)


def test_branch_to_slug_conversion():
    assert flow.branch_to_slug("feature/add-auth") == "feature-add-auth"
    assert flow.branch_to_slug("main") == "main"
    assert flow.branch_to_slug("feature/nested/branch") == "feature-nested-branch"
    assert flow.branch_to_slug("") == "unknown"


def test_get_current_branch():
    branch = flow.get_current_branch()
    assert isinstance(branch, str)
    assert len(branch) > 0


def test_get_active_worklog_dir():
    path = flow.get_active_worklog_dir("feature/test-branch")
    assert isinstance(path, Path)
    assert path.name == "feature-test-branch"


def test_run_cmd_success():
    code, stdout, stderr = flow.run_cmd(["echo", "hello"])
    assert code == 0
    assert stdout == "hello"
    assert stderr == ""


def test_run_cmd_failure():
    code, stdout, stderr = flow.run_cmd(["false"])
    assert code != 0
