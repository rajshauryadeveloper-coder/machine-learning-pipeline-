"""Subagent Orchestration & Model Tiering Subsystem (src/agent/subagents.py).

Enforces the 20-30% Context Smart Zone rule, parallel non-dependent task
isolation, and dynamic model tier routing for subagent delegation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class ModelTier(str, Enum):
    """Model sizing tiers for subagents based on task complexity."""

    PRO = "pro"  # Frontier/deep reasoning, architectural refactor, complex math
    FLASH = "flash"  # Standard research, documentation lookup, code search
    FLASH_LITE = "flash_lite"  # Lightweight string regex, keyword checks
    INHERIT = "inherit"  # Default to parent supervisor model


class SubagentTask(BaseModel):
    """Structured definition for an isolated subagent task."""

    task_id: str
    description: str
    model_tier: ModelTier = ModelTier.FLASH
    role: str = "Codebase Researcher"
    workspace: str = "inherit"
    timeout_seconds: int = 120


class SubagentTaskResult(BaseModel):
    """Distilled summary returned across the subagent context boundary."""

    task_id: str
    status: str = "completed"
    distilled_summary: str
    structured_data: dict[str, Any] = Field(default_factory=dict)
    tokens_saved_estimate: int = 0


def route_subagent_model_tier(task_description: str) -> ModelTier:
    """Classify task complexity and return optimal model tier for cost/performance."""
    desc = task_description.lower()

    # High complexity / reasoning keywords -> PRO
    pro_indicators = [
        "refactor",
        "architecture",
        "synthesizer",
        "multi-tier",
        "complex math",
        "security audit",
        "algorithm",
    ]
    for ind in pro_indicators:
        if ind in desc:
            return ModelTier.PRO

    # Ultra-lightweight keywords -> FLASH_LITE
    lite_indicators = [
        "regex",
        "keyword",
        "health check",
        "string check",
        "ping",
        "exists",
    ]
    for ind in lite_indicators:
        if ind in desc:
            return ModelTier.FLASH_LITE

    # Standard research / file search / documentation -> FLASH
    return ModelTier.FLASH


def is_within_smart_zone(
    current_tokens: int,
    max_tokens: int = 1_000_000,
    target_ratio: float = 0.30,
) -> bool:
    """Check if the agent is operating within the 20-30% optimal context smart zone."""
    if max_tokens <= 0:
        return True
    ratio = current_tokens / max_tokens
    return ratio <= target_ratio


def distill_subagent_output(
    task_id: str,
    raw_output: str,
    summary: str,
    structured_data: Optional[dict[str, Any]] = None,
) -> SubagentTaskResult:
    """Compress raw subagent execution logs into a compact summary for the parent."""
    # Compute estimated tokens saved by discarding the raw scratchpad
    raw_tokens = max(1, len(raw_output.split()))
    summary_tokens = max(1, len(summary.split()))
    tokens_saved = max(0, raw_tokens - summary_tokens)

    return SubagentTaskResult(
        task_id=task_id,
        status="completed",
        distilled_summary=summary.strip(),
        structured_data=structured_data or {},
        tokens_saved_estimate=tokens_saved,
    )
