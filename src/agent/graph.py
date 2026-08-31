import datetime
import json
import logging
import os
import re
import time
from typing import Any, Optional

from google import genai
from langgraph.graph import END, StateGraph

from src.agent.guardrails import is_malicious_prompt
from src.agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    SQL_GENERATION_PROMPT,
    SYNTHESIS_PROMPT,
)
from src.agent.state import AgentState
from src.agent.tools import compute_math, execute_sql_query, get_database_schema
from src.config import settings

logger = logging.getLogger(__name__)


def get_genai_client() -> Optional[genai.Client]:
    """Initialize Google GenAI client using settings or environment variable."""
    api_key = settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("No GEMINI_API_KEY found in settings or environment.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        return None


def extract_sql_from_text(text: str) -> str:
    """Extract clean SQL statement from model text or code markdown block."""
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        if candidate.upper().startswith("SELECT") or candidate.upper().startswith(
            "WITH"
        ):
            return candidate
    # If raw query is returned directly
    cleaned = text.strip()
    for line in cleaned.splitlines():
        if line.strip().upper().startswith("SELECT") or line.strip().upper().startswith(
            "WITH"
        ):
            return cleaned
    return cleaned


def guardrail_node(state: AgentState) -> dict[str, Any]:
    """Gate 1: Verify prompt for injections, jailbreaks, and destructive intent."""
    query = state.get("query", "")
    safety_check = is_malicious_prompt(query)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    steps = list(state.get("steps", []))
    if not safety_check.is_safe:
        steps.append(
            {
                "step": "guardrail_check",
                "status": "blocked",
                "detail": safety_check.reason,
                "timestamp": timestamp,
            }
        )
        return {
            "is_safe": False,
            "violation_reason": safety_check.reason,
            "response": (
                "Safety Violation Refusal: I cannot fulfill this request. "
                "The system enforces strict safety guardrails and prohibits "
                "destructive database operations, credential extraction, "
                "or security bypass instructions."
            ),
            "steps": steps,
            "sql_queries": [],
            "calculations": [],
        }

    steps.append(
        {
            "step": "guardrail_check",
            "status": "passed",
            "detail": "Input verified safe.",
            "timestamp": timestamp,
        }
    )
    return {
        "is_safe": True,
        "violation_reason": None,
        "steps": steps,
    }


def schema_analyzer_node(state: AgentState) -> dict[str, Any]:
    """Gate 2: Retrieve relational schema metadata to ground SQL reasoning."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    schema = get_database_schema()
    steps = list(state.get("steps", []))
    tbl_cnt = schema.get("table_count", 5)
    steps.append(
        {
            "step": "schema_analysis",
            "status": "completed",
            "detail": f"Analyzed schema across {tbl_cnt} managed tables.",
            "timestamp": timestamp,
        }
    )
    return {
        "schema_context": schema,
        "steps": steps,
    }


def fallback_sql_generator(query: str) -> str:
    """Heuristic fallback for common business queries during outage."""
    q = query.lower()
    if "top" in q and ("product" in q or "selling" in q):
        return (
            "SELECT p.id, p.name, p.price, sum(oi.quantity) as units_sold, "
            "sum(oi.subtotal) as total_revenue "
            "FROM products p "
            "JOIN order_items oi ON oi.product_id = p.id "
            "GROUP BY p.id, p.name, p.price "
            "ORDER BY total_revenue DESC LIMIT 5;"
        )
    if "category" in q or "categories" in q:
        return (
            "SELECT c.name as category_name, count(DISTINCT p.id) as product_count, "
            "coalesce(sum(oi.subtotal), 0) as category_revenue "
            "FROM categories c "
            "LEFT JOIN products p ON p.category_id = c.id "
            "LEFT JOIN order_items oi ON oi.product_id = p.id "
            "GROUP BY c.name ORDER BY category_revenue DESC;"
        )
    if "customer" in q and ("top" in q or "spending" in q or "vip" in q):
        return (
            "SELECT c.id, c.first_name, c.last_name, c.email, "
            "count(o.id) as total_orders, sum(o.total_amount) as total_spent "
            "FROM customers c "
            "JOIN orders o ON o.customer_id = c.id "
            "GROUP BY c.id, c.first_name, c.last_name, c.email "
            "ORDER BY total_spent DESC LIMIT 5;"
        )
    if "order" in q or "revenue" in q or "sales" in q:
        return (
            "SELECT count(*) as total_orders, sum(total_amount) as total_revenue, "
            "avg(total_amount) as avg_order_value "
            "FROM orders;"
        )
    # Default product count / overview query
    return (
        "SELECT count(*) as total_products, avg(price) as avg_price, "
        "sum(stock_quantity) as total_inventory FROM products;"
    )


def agent_reasoning_node(state: AgentState) -> dict[str, Any]:
    """Gate 3: Generate and execute safe read-only SQL queries and math."""
    query = state.get("query", "")
    steps = list(state.get("steps", []))
    sql_queries = list(state.get("sql_queries", []))
    calculations = list(state.get("calculations", []))
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    client = get_genai_client()
    generated_sql = ""

    if client:
        try:
            prompt_content = (
                f"{AGENT_SYSTEM_PROMPT}\n\n"
                f"{SQL_GENERATION_PROMPT.format(query=query)}"
            )
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt_content,
            )
            if response and response.text:
                generated_sql = extract_sql_from_text(response.text)
        except Exception as e:
            logger.warning(f"GenAI call failed, using heuristic engine: {e}")

    if not generated_sql or not generated_sql.upper().startswith(("SELECT", "WITH")):
        generated_sql = fallback_sql_generator(query)

    # Execute SQL via read-only tool
    exec_result = execute_sql_query(generated_sql)
    sql_queries.append(exec_result)

    # Self-correction check if SQL failed
    if not exec_result.get("success") and client:
        err_msg = exec_result.get("error")
        retry_prompt = (
            f"The SQL query produced error: {err_msg}.\n"
            f"Original user query: {query}\n"
            f"Fix SQL for PostgreSQL. Return ONLY SELECT query in ```sql ... ``` block."
        )
        try:
            retry_res = client.models.generate_content(
                model=settings.gemini_model,
                contents=retry_prompt,
            )
            if retry_res and retry_res.text:
                fixed_sql = extract_sql_from_text(retry_res.text)
                retry_exec = execute_sql_query(fixed_sql)
                sql_queries.append(retry_exec)
                if retry_exec.get("success"):
                    exec_result = retry_exec
        except Exception as e:
            logger.warning(f"Self-correction retry failed: {e}")

    row_cnt = exec_result.get("row_count", 0)
    steps.append(
        {
            "step": "sql_execution",
            "status": "success" if exec_result.get("success") else "error",
            "detail": f"Executed query with {row_cnt} rows returned.",
            "query": exec_result.get("query"),
            "timestamp": timestamp,
        }
    )

    # If rows returned, perform relevant calculation checks (e.g. totals or averages)
    if exec_result.get("success") and exec_result.get("rows"):
        rows = exec_result.get("rows", [])
        # Perform aggregate checks if numeric fields exist
        if len(rows) > 1 and "total_spent" in rows[0]:
            spends = [float(r["total_spent"]) for r in rows if r.get("total_spent")]
            if spends:
                calc_res = compute_math(f"sum({spends}) / len({spends})")
                calculations.append(
                    {
                        "description": "Average spend across top records",
                        "result": calc_res.get("result"),
                        "expression": f"Average({len(spends)} items)",
                    }
                )

    return {
        "steps": steps,
        "sql_queries": sql_queries,
        "calculations": calculations,
    }


def response_synthesizer_node(state: AgentState) -> dict[str, Any]:
    """Gate 4: Synthesize retrieved data into formatted answer."""
    query = state.get("query", "")
    steps = list(state.get("steps", []))
    sql_queries = state.get("sql_queries", [])
    calculations = state.get("calculations", [])
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    last_sql = sql_queries[-1] if sql_queries else {}
    rows = last_sql.get("rows", [])
    sql_error = last_sql.get("error")

    data_summary = (
        json.dumps(rows[:10], indent=2)
        if rows
        else (
            f"No data returned or error: {sql_error}" if sql_error else "0 rows found."
        )
    )
    calc_summary = json.dumps(calculations, indent=2) if calculations else "None"

    client = get_genai_client()
    final_text = ""

    if client and not sql_error:
        try:
            synth_prompt = SYNTHESIS_PROMPT.format(
                query=query,
                data_summary=data_summary,
                calc_summary=calc_summary,
            )
            res = client.models.generate_content(
                model=settings.gemini_model,
                contents=synth_prompt,
            )
            if res and res.text:
                final_text = res.text.strip()
        except Exception as e:
            logger.warning(f"Synthesis call failed, using formatted fallback: {e}")

    if not final_text:
        if sql_error:
            final_text = f"I encountered an error querying the database: {sql_error}"
        elif rows:
            final_text = (
                f"Based on your query, here are the results from the database:\n\n"
                f"- **Records Found**: {len(rows)}\n"
            )
            for idx, r in enumerate(rows[:5], 1):
                details = ", ".join(f"{k}: {v}" for k, v in r.items())
                final_text += f"{idx}. {details}\n"
        else:
            final_text = (
                "No matching records were found in the database for your query."
            )

    steps.append(
        {
            "step": "response_synthesis",
            "status": "completed",
            "detail": "Synthesized final answer for user.",
            "timestamp": timestamp,
        }
    )

    return {
        "response": final_text,
        "steps": steps,
    }


def route_guardrail(state: AgentState) -> str:
    """Route based on safety check result."""
    return "blocked" if not state.get("is_safe", False) else "safe"


def create_agent_graph() -> StateGraph:
    """Construct and compile the LangGraph workflow for Option 1 Reasoner Graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("schema_analyzer", schema_analyzer_node)
    workflow.add_node("agent_reasoning", agent_reasoning_node)
    workflow.add_node("response_synthesizer", response_synthesizer_node)

    workflow.set_entry_point("guardrail")

    workflow.add_conditional_edges(
        "guardrail",
        route_guardrail,
        {
            "blocked": END,
            "safe": "schema_analyzer",
        },
    )

    workflow.add_edge("schema_analyzer", "agent_reasoning")
    workflow.add_edge("agent_reasoning", "response_synthesizer")
    workflow.add_edge("response_synthesizer", END)

    return workflow.compile()


# Global compiled graph instance
compiled_agent_graph = create_agent_graph()


def run_agent_graph(query: str, temperature: float = 0.2) -> dict[str, Any]:
    """Execute the full compiled agent workflow for a single query."""
    start_time = time.time()
    initial_state: AgentState = {
        "query": query,
        "is_safe": True,
        "steps": [],
        "sql_queries": [],
        "calculations": [],
        "response": "",
        "iteration_count": 0,
    }

    final_state = compiled_agent_graph.invoke(initial_state)
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "query": query,
        "is_safe": final_state.get("is_safe", False),
        "violation_reason": final_state.get("violation_reason"),
        "response": final_state.get("response", ""),
        "steps": final_state.get("steps", []),
        "sql_queries": final_state.get("sql_queries", []),
        "calculations": final_state.get("calculations", []),
        "execution_time_ms": elapsed_ms,
    }
