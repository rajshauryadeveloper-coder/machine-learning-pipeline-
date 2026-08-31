import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SafetyCheckResult:
    is_safe: bool
    violation_type: Optional[str] = None
    reason: str = ""


# Malicious prompt injection / jailbreak patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+"
    r"(instructions|prompts|rules|guidelines)",
    r"disregard\s+(all\s+)?(previous|prior|above)\s+"
    r"(instructions|prompts|rules|guidelines)",
    r"override\s+(system|safety|security)\s+(prompts|guardrails|rules|filters)",
    r"system\s+prompt\s+override",
    r"you\s+are\s+now\s+(in\s+)?(evil|dan|jailbreak|unfiltered|god)\s+mode",
    r"developer\s+mode\s+(enabled|activated|on)",
    r"bypass\s+(all\s+)?(security|guardrails|safety|filters)",
    r"reveal\s+(secret|hidden|admin|database)?\s*"
    r"(passwords?|keys?|credentials?|tokens?)",
    r"exploit\s+(sql|vulnerability|backdoor)",
    r"dump\s+(private|secret|all)?\s*(keys?|passwords?|hashes)",
    r"rm\s+-rf",
    r"drop\s+database",
    r"drop\s+table",
    r"truncate\s+table",
    r"delete\s+all\s+(records|users|customers|orders)",
]

# Forbidden SQL statements / keywords that perform state mutation or DDL
DISALLOWED_SQL_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCALL\b",
    r"\bCOPY\b",
    r"\bRENAME\b",
    r"\bREINDEX\b",
    r"\bVACUUM\b",
    r"\bLOCK\b",
    r"\bMERGE\b",
    r"\bDO\b\s*\$\$",
]


def is_malicious_prompt(prompt: str) -> SafetyCheckResult:
    """Analyze input prompt for jailbreaks, prompt injection, or malicious intents."""
    cleaned = prompt.strip().lower()
    if not cleaned:
        return SafetyCheckResult(
            is_safe=False,
            violation_type="empty_query",
            reason="Query cannot be empty.",
        )

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return SafetyCheckResult(
                is_safe=False,
                violation_type="prompt_injection",
                reason=(
                    "Refusal: The query contains disallowed directives, "
                    "prompt injection, or malicious intent."
                ),
            )

    return SafetyCheckResult(is_safe=True, violation_type=None, reason="")


def validate_sql_safety(sql: str) -> tuple[bool, Optional[str]]:
    """Strictly validate that an SQL query is 100% read-only (SELECT / WITH)."""
    cleaned_sql = sql.strip().rstrip(";")
    if not cleaned_sql:
        return False, "SQL query cannot be empty."

    # Strip inline and block comments to prevent bypass via comment hiding
    sql_no_comments = re.sub(r"--.*?\n", "\n", cleaned_sql)
    sql_no_comments = re.sub(r"/\*.*?\*/", "", sql_no_comments, flags=re.DOTALL)
    normalized = " ".join(sql_no_comments.strip().split()).upper()

    # Must start with SELECT, WITH, or EXPLAIN
    if not (
        normalized.startswith("SELECT")
        or normalized.startswith("WITH")
        or normalized.startswith("EXPLAIN")
    ):
        return (
            False,
            "Disallowed SQL: Only SELECT, WITH (CTE), and EXPLAIN queries are allowed.",
        )

    # Check for any disallowed mutation keyword across the entire statement
    for pattern in DISALLOWED_SQL_KEYWORDS:
        if re.search(pattern, normalized, re.IGNORECASE):
            match = re.search(pattern, normalized, re.IGNORECASE).group(0)
            return (
                False,
                f"Disallowed SQL: Mutation '{match}' is strictly prohibited.",
            )

    # Check if multiple queries are chained with semicolon and any non-select exists
    parts = [p.strip() for p in sql_no_comments.split(";") if p.strip()]
    if len(parts) > 1:
        for part in parts:
            part_norm = " ".join(part.split()).upper()
            if not (
                part_norm.startswith("SELECT")
                or part_norm.startswith("WITH")
                or part_norm.startswith("EXPLAIN")
            ):
                return (
                    False,
                    "Disallowed SQL: Chained non-SELECT statements are prohibited.",
                )
            for pattern in DISALLOWED_SQL_KEYWORDS:
                if re.search(pattern, part_norm, re.IGNORECASE):
                    return (
                        False,
                        "Disallowed SQL: Chained mutation statements are prohibited.",
                    )

    return True, None
