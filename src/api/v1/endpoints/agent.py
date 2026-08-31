import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from src.agent.graph import run_agent_graph
from src.agent.tools import get_database_schema
from src.config import settings
from src.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agentic Analytics Chatbot"])


@router.post("/chat", response_model=AgentChatResponse)
def chat_with_agent(payload: AgentChatRequest) -> AgentChatResponse:
    """Process query through LangGraph reasoning workflow with safety guardrails."""
    try:
        result = run_agent_graph(
            query=payload.query,
            temperature=payload.temperature or 0.2,
        )
        return AgentChatResponse(**result)
    except Exception as e:
        logger.error(f"Error processing agent query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Agent workflow error: {str(e)}",
        )


@router.get("/status", response_model=AgentStatusResponse)
def get_agent_status() -> AgentStatusResponse:
    """Return operational status, model provider, and safety capabilities."""
    return AgentStatusResponse(
        status="operational",
        model=settings.gemini_model,
        provider="Google AI Studio",
        architecture="Guardrail-Gated Multi-Stage Reasoner Graph",
        guardrails={
            "prompt_injection_filter": True,
            "read_only_sql_enforcement": True,
            "blocked_mutations": [
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "ALTER",
                "TRUNCATE",
                "CREATE",
                "GRANT",
                "REVOKE",
            ],
            "transaction_mode": "READ ONLY",
            "max_rows_limit": 100,
        },
        tools=[
            "get_database_schema",
            "execute_sql_query",
            "compute_math",
        ],
    )


@router.get("/schema")
def get_agent_schema_view() -> dict[str, Any]:
    """Return the database schema metadata accessible by the agent."""
    return get_database_schema()
