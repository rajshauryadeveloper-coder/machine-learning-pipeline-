import datetime
from decimal import Decimal
import math
import re
from typing import Any

import psycopg

from src.agent.guardrails import validate_sql_safety
from src.database import get_dict_connection
from src.db.schema import get_table_metadata


def serialize_cell(val: Any) -> Any:
    """Serialize PostgreSQL datatypes (Decimal, datetime, date)."""
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.isoformat()
    return val


def get_database_schema() -> dict[str, Any]:
    """Retrieve full relational database schema for all managed tables."""
    try:
        tables = get_table_metadata()
        schema_summary = []
        for t in tables:
            cols = [
                {
                    "name": col["column_name"],
                    "type": col["data_type"],
                    "nullable": col["is_nullable"] == "YES",
                }
                for col in t["columns"]
            ]
            schema_summary.append(
                {
                    "table_name": t["table_name"],
                    "total_rows": t["row_count"],
                    "columns": cols,
                }
            )
        return {
            "database": "ecommerce_database",
            "table_count": len(schema_summary),
            "tables": schema_summary,
        }
    except Exception as e:
        return {"error": f"Failed to retrieve database schema: {str(e)}"}


def execute_sql_query(query: str, max_rows: int = 100) -> dict[str, Any]:
    """Safely execute a validated read-only SQL query and return rows."""
    is_safe, violation_reason = validate_sql_safety(query)
    if not is_safe:
        return {
            "success": False,
            "query": query,
            "error": f"Security Violation: {violation_reason}",
        }

    cleaned_query = query.strip().rstrip(";")

    # Inject LIMIT if not already present to prevent massive payloads
    if not re.search(r"\bLIMIT\b", cleaned_query, re.IGNORECASE):
        cleaned_query = f"{cleaned_query} LIMIT {max_rows}"

    try:
        with get_dict_connection(autocommit=True) as conn:
            with conn.cursor() as cur:
                # Set transaction read-only at PostgreSQL engine level
                cur.execute("SET TRANSACTION READ ONLY;")
                cur.execute(cleaned_query)
                raw_rows = cur.fetchall()

                # Serialize decimals and datetimes
                formatted_rows = [
                    {k: serialize_cell(v) for k, v in row.items()} for row in raw_rows
                ]

                return {
                    "success": True,
                    "query": cleaned_query,
                    "row_count": len(formatted_rows),
                    "rows": formatted_rows,
                }
    except psycopg.Error as pe:
        return {
            "success": False,
            "query": cleaned_query,
            "error": f"Database Error: {str(pe).strip()}",
        }
    except Exception as e:
        return {
            "success": False,
            "query": cleaned_query,
            "error": f"Execution Error: {str(e).strip()}",
        }


SAFE_MATH_GLOBALS = {
    "__builtins__": {},
    "sum": sum,
    "min": min,
    "max": max,
    "len": len,
    "abs": abs,
    "round": round,
    "pow": pow,
    "sorted": sorted,
    "float": float,
    "int": int,
    "math": math,
    "sqrt": math.sqrt,
    "log": math.log,
    "exp": math.exp,
    "floor": math.floor,
    "ceil": math.ceil,
}


def compute_math(expression: str) -> dict[str, Any]:
    """Safely evaluate mathematical expressions in a restricted sandbox."""
    cleaned = expression.strip()
    # Check for forbidden substrings
    forbidden = [
        "__",
        "import",
        "eval",
        "exec",
        "open",
        "globals",
        "locals",
        "lambda",
        "os",
        "sys",
        "subprocess",
    ]
    for word in forbidden:
        if word in cleaned:
            return {
                "success": False,
                "expression": expression,
                "error": f"Forbidden keyword or token '{word}' in expression.",
            }

    try:
        # Evaluate within strict sandbox
        result = eval(cleaned, SAFE_MATH_GLOBALS, {})  # noqa: S307
        if isinstance(result, (int, float)):
            result = round(result, 4)
        return {
            "success": True,
            "expression": expression,
            "result": result,
        }
    except ZeroDivisionError:
        return {
            "success": False,
            "expression": expression,
            "error": "ZeroDivisionError: Division by zero.",
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": f"Math Evaluation Error: {str(e)}",
        }
