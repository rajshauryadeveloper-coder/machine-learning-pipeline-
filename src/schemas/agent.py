from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class AgentChatRequest(BaseModel):
    query: str = Field(
        ...,
        description="The natural language question for analytics chatbot.",
        min_length=1,
        max_length=2000,
        examples=["What are the top 5 highest selling products?"],
    )
    temperature: Optional[float] = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for response generation.",
    )

    @field_validator("query")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty or only whitespace.")
        return cleaned


class AgentChatResponse(BaseModel):
    query: str
    is_safe: bool
    violation_reason: Optional[str] = None
    response: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    sql_queries: list[dict[str, Any]] = Field(default_factory=list)
    calculations: list[dict[str, Any]] = Field(default_factory=list)
    execution_time_ms: float


class AgentStatusResponse(BaseModel):
    status: str
    model: str
    provider: str
    architecture: str
    guardrails: dict[str, Any]
    tools: list[str]
