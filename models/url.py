import os
import random
import string
from database import get_db
from config import Config

# Base URL for constructing short URLs (configurable for production)
_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


def _url_from_row(row):
    """Convert a database row to a URL dict."""
    return {
        "id": row[0],
        "user_id": row[1],
        "original_url": row[2],
        "short_code": row[3],
        "short_url": f"{_BASE_URL}/{row[3]}",
        "clicks": row[4],
        "created_at": row[5].isoformat()
    }


def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_url(user_id, original_url):
    """Insert a new shortened URL and return the record."""
    with get_db() as conn:
        cur = conn.cursor()

        # Generate a unique short code (retry on collision up to 5 times)
        code = None
        for _ in range(5):
            code = generate_short_code()
            cur.execute(
                "SELECT id FROM urls WHERE short_code = %s", (code,)
            )
            if not cur.fetchone():
                break
        else:
            cur.close()
            raise RuntimeError(
                "Could not generate a unique short code after 5 attempts"
            )

        cur.execute(
            """
            INSERT INTO urls (user_id, original_url, short_code)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, original_url, short_code, clicks, created_at
            """,
            (user_id, original_url, code)
        )
        row = cur.fetchone()
        cur.close()
    return _url_from_row(row)


def get_url_by_code(short_code):
    """Return a URL record by short code, or None if not found."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, original_url, short_code, clicks, created_at
            FROM urls WHERE short_code = %s
            """,
            (short_code,)
        )
        row = cur.fetchone()
        cur.close()
    return _url_from_row(row) if row else None


def get_urls_by_user(user_id):
    """Return all URLs created by a specific user, ordered newest first."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, original_url, short_code, clicks, created_at
            FROM urls
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = cur.fetchall()
        cur.close()
    return [_url_from_row(row) for row in rows]


def increment_clicks(short_code):
    """Increment the click count for a short code."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_code = %s",
            (short_code,)
        )
        cur.close()


def get_user_stats(user_id):
    """
    Return lightweight aggregate stats for a user's URLs.

    This is a lighter version of analytics for quick profile display.
    """
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*)::int,
                COALESCE(SUM(clicks), 0)::int
            FROM urls
            WHERE user_id = %s
            """,
            (user_id,)
        )
        row = cur.fetchone()
        cur.close()
    return {"total_urls": row[0], "total_clicks": row[1]}


def delete_url(url_id, user_id):
    """Delete a URL by its id, scoped to the user. Returns True if deleted."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM urls WHERE id = %s AND user_id = %s",
            (url_id, user_id)
        )
        deleted = cur.rowcount > 0
        cur.close()
    return deleted


def get_url_by_id(url_id):
    """Return a URL record by its id, or None."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_id, original_url, short_code, clicks, created_at FROM urls WHERE id = %s",
            (url_id,)
        )
        row = cur.fetchone()
        cur.close()
    return _url_from_row(row) if row else None


def get_user_analytics(user_id):
    """Return detailed aggregate analytics for a user's URLs."""
    with get_db() as conn:
        cur = conn.cursor()

        # Aggregate metrics
        cur.execute(
            """
            SELECT
                COUNT(*)::int AS total_urls,
                COALESCE(SUM(clicks), 0)::int AS total_clicks,
                COALESCE(AVG(clicks), 0)::int AS avg_clicks,
                COALESCE(MAX(clicks), 0)::int AS most_clicked_count
            FROM urls
            WHERE user_id = %s
            """,
            (user_id,)
        )
        stats = cur.fetchone()

        # Top 5 most-clicked URLs
        cur.execute(
            """
            SELECT id, original_url, short_code, clicks, created_at
            FROM urls
            WHERE user_id = %s
            ORDER BY clicks DESC
            LIMIT 5
            """,
            (user_id,)
        )
        top_rows = cur.fetchall()
        cur.close()

    return {
        "total_urls": stats[0],
        "total_clicks": stats[1],
        "avg_clicks": stats[2],
        "most_clicked_count": stats[3],
        "top_urls": [
            {
                "id": r[0],
                "original_url": r[1],
                "short_code": r[2],
                "short_url": f"{_BASE_URL}/{r[2]}",
                "clicks": r[3],
                "created_at": r[4].isoformat()
            }
            for r in top_rows
        ]
    }
