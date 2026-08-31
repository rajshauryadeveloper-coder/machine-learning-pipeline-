from typing import Any, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    query: str
    is_safe: bool
    violation_reason: Optional[str]
    schema_context: Optional[dict[str, Any]]
    steps: list[dict[str, Any]]
    sql_queries: list[dict[str, Any]]
    calculations: list[dict[str, Any]]
    response: str
    error: Optional[str]
    iteration_count: int
    execution_time_ms: float
