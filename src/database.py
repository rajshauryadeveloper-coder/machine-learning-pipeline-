from contextlib import contextmanager
from typing import Any, Generator

import psycopg
from psycopg.rows import dict_row

from src.config import settings


@contextmanager
def get_connection(
    autocommit: bool = False,
) -> Generator[psycopg.Connection, None, None]:
    """Yield a standard PostgreSQL connection using application settings."""
    conn = psycopg.connect(settings.database_url, autocommit=autocommit)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_dict_connection(
    autocommit: bool = False,
) -> Generator[psycopg.Connection[dict[str, Any]], None, None]:
    """Yield a PostgreSQL connection with dict_row factory for dictionary rows."""
    conn = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
        autocommit=autocommit,
    )
    try:
        yield conn
    finally:
        conn.close()


def check_database_connection() -> bool:
    """Return True when the database is reachable."""
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
        return True
    except psycopg.Error:
        return False
