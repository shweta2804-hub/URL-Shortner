"""
Database module for PostgreSQL connection management.

Uses psycopg2's ThreadedConnectionPool for efficient connection reuse
in production, with fallback to direct connections in development.
"""

import contextlib
import psycopg2
import psycopg2.extras
from psycopg2 import pool as psycopg2_pool
from config import Config

# Module-level connection pool (lazily initialized)
_connection_pool = None


def get_pool():
    """Get or create the connection pool singleton."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = psycopg2_pool.ThreadedConnectionPool(
            Config.DB_POOL_MIN,
            Config.DB_POOL_MAX,
            Config.DATABASE_URL
        )
    return _connection_pool


@contextlib.contextmanager
def get_db():
    """
    Context manager providing a database connection.

    Yields a connection from the pool (or a new one if pool fails).
    Automatically commits on success, rolls back on error.
    Usage:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(...)
    """
    conn = None
    try:
        conn = get_pool().getconn()
        conn.autocommit = False
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            get_pool().putconn(conn)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Helper to execute a query with automatic connection management.

    Returns fetched rows or None. Handles commit/rollback.
    """
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(query, params or ())
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetchall:
            result = cur.fetchall()
        cur.close()
        return result


def init_db():
    """Create all required tables and indexes if they don't exist."""
    with get_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS materials (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL
                    REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT DEFAULT '',
                subject VARCHAR(100) DEFAULT '',
                category VARCHAR(100) DEFAULT '',
                resource_link TEXT NOT NULL,
                resource_code VARCHAR(10) UNIQUE NOT NULL,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_resource_code
            ON materials(resource_code);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_user_id
            ON materials(user_id);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_category
            ON materials(category);
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_materials_subject
            ON materials(subject);
        """)

        cur.close()

    print("Database tables initialized successfully (pool).")


if __name__ == "__main__":
    init_db()