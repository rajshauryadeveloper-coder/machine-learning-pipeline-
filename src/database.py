from contextlib import contextmanager
from typing import Generator

import psycopg

from src.config import settings


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    """Yield a PostgreSQL connection using application settings."""
    conn = psycopg.connect(settings.database_url)
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
