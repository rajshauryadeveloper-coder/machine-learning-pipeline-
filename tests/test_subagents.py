from src.agent.subagents import (
    ModelTier,
    SubagentTask,
    SubagentTaskResult,
    route_subagent_model_tier,
    is_within_smart_zone,
    distill_subagent_output,
)


def test_route_subagent_model_tier_research():
    tier = route_subagent_model_tier("search documentation for LangChain LCEL syntax")
    assert tier == ModelTier.FLASH


def test_route_subagent_model_tier_lightweight():
    tier = route_subagent_model_tier("check if string contains keyword regex")
    assert tier == ModelTier.FLASH_LITE


def test_route_subagent_model_tier_complex():
    tier = route_subagent_model_tier(
        "refactor entire multi-tier graph state and synthesizer reasoning"
    )
    assert tier == ModelTier.PRO


def test_is_within_smart_zone():
    # 250k tokens in a 1M token window (25%) -> In smart zone
    assert is_within_smart_zone(current_tokens=250_000, max_tokens=1_000_000) is True

    # 350k tokens in a 1M token window (35%) -> Exceeds smart zone
    assert is_within_smart_zone(current_tokens=350_000, max_tokens=1_000_000) is False


def test_subagent_task_creation():
    task = SubagentTask(
        task_id="task-001",
        description="Explore foreign key constraints in ecommerce schema",
        model_tier=ModelTier.FLASH,
        role="Database Researcher",
    )
    assert task.task_id == "task-001"
    assert task.model_tier == ModelTier.FLASH
    assert task.role == "Database Researcher"


def test_distill_subagent_output():
    raw_logs = (
        "Starting test execution...\n"
        "Loading 50 files...\n"
        "Ran 65 tests in 2.3 seconds.\n"
        "All passed.\n"
        "Final conclusion: All database fixtures are valid."
    )
    result = distill_subagent_output(
        task_id="task-001",
        raw_output=raw_logs,
        summary="All database fixtures are valid. 65 tests passed.",
    )
    assert isinstance(result, SubagentTaskResult)
    assert result.task_id == "task-001"
    assert "All database fixtures are valid" in result.distilled_summary
    assert len(result.distilled_summary) < len(raw_logs)
