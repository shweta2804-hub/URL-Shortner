import os
import random
import string
from database import get_db
from config import Config

# Base URL for constructing resource links (configurable for production)
_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


def _material_from_row(row):
    """Convert a database row to a material dict."""
    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "description": row[3],
        "subject": row[4],
        "category": row[5],
        "resource_link": row[6],
        "resource_code": row[7],
        "short_url": f"{_BASE_URL}/{row[7]}",
        "views": row[8],
        "created_at": row[9].isoformat()
    }


def generate_resource_code(length=6):
    """Generate a random alphanumeric resource code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_material(user_id, title, resource_link, description="", subject="", category=""):
    """Insert a new study material and return the record."""
    with get_db() as conn:
        cur = conn.cursor()

        # Generate a unique resource code (retry on collision up to 5 times)
        code = None
        for _ in range(5):
            code = generate_resource_code()
            cur.execute(
                "SELECT id FROM materials WHERE resource_code = %s", (code,)
            )
            if not cur.fetchone():
                break
        else:
            cur.close()
            raise RuntimeError(
                "Could not generate a unique resource code after 5 attempts"
            )

        cur.execute(
            """
            INSERT INTO materials (user_id, title, description, subject, category, resource_link, resource_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, user_id, title, description, subject, category, resource_link, resource_code, views, created_at
            """,
            (user_id, title, description, subject, category, resource_link, code)
        )
        row = cur.fetchone()
        cur.close()
    return _material_from_row(row)


def get_material_by_code(resource_code):
    """Return a material record by resource code, or None if not found."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, title, description, subject, category, resource_link, resource_code, views, created_at
            FROM materials WHERE resource_code = %s
            """,
            (resource_code,)
        )
        row = cur.fetchone()
        cur.close()
    return _material_from_row(row) if row else None


def get_materials_by_user(user_id):
    """Return all materials created by a specific user, ordered newest first."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, user_id, title, description, subject, category, resource_link, resource_code, views, created_at
            FROM materials
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = cur.fetchall()
        cur.close()
    return [_material_from_row(row) for row in rows]


def increment_views(resource_code):
    """Increment the view count for a resource code."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE materials SET views = views + 1 WHERE resource_code = %s",
            (resource_code,)
        )
        cur.close()


def get_user_stats(user_id):
    """
    Return lightweight aggregate stats for a user's materials.

    This is a lighter version of analytics for quick profile display.
    """
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                COUNT(*)::int,
                COALESCE(SUM(views), 0)::int
            FROM materials
            WHERE user_id = %s
            """,
            (user_id,)
        )
        row = cur.fetchone()
        cur.close()
    return {"total_materials": row[0], "total_views": row[1]}


def delete_material(material_id, user_id):
    """Delete a material by its id, scoped to the user. Returns True if deleted."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM materials WHERE id = %s AND user_id = %s",
            (material_id, user_id)
        )
        deleted = cur.rowcount > 0
        cur.close()
    return deleted


def get_material_by_id(material_id):
    """Return a material record by its id, or None."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_id, title, description, subject, category, resource_link, resource_code, views, created_at FROM materials WHERE id = %s",
            (material_id,)
        )
        row = cur.fetchone()
        cur.close()
    return _material_from_row(row) if row else None


def get_user_analytics(user_id):
    """Return detailed aggregate analytics for a user's materials."""
    with get_db() as conn:
        cur = conn.cursor()

        # Aggregate metrics
        cur.execute(
            """
            SELECT
                COUNT(*)::int AS total_materials,
                COALESCE(SUM(views), 0)::int AS total_views,
                COALESCE(AVG(views), 0)::int AS avg_views,
                COALESCE(MAX(views), 0)::int AS most_viewed_count
            FROM materials
            WHERE user_id = %s
            """,
            (user_id,)
        )
        stats = cur.fetchone()

        # Top 5 most-viewed materials
        cur.execute(
            """
            SELECT id, title, description, subject, category, resource_link, resource_code, views, created_at
            FROM materials
            WHERE user_id = %s
            ORDER BY views DESC
            LIMIT 5
            """,
            (user_id,)
        )
        top_rows = cur.fetchall()
        cur.close()

    return {
        "total_materials": stats[0],
        "total_views": stats[1],
        "avg_views": stats[2],
        "most_viewed_count": stats[3],
        "top_materials": [
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "subject": r[3],
                "category": r[4],
                "resource_link": r[5],
                "resource_code": r[6],
                "short_url": f"{_BASE_URL}/{r[6]}",
                "views": r[7],
                "created_at": r[8].isoformat()
            }
            for r in top_rows
        ]
    }


def search_materials(user_id, query):
    """
    Search materials by title, description, subject, or category.
    Returns matching materials ordered by newest first.
    """
    with get_db() as conn:
        cur = conn.cursor()
        search_pattern = f"%{query}%"
        cur.execute(
            """
            SELECT id, user_id, title, description, subject, category, resource_link, resource_code, views, created_at
            FROM materials
            WHERE user_id = %s
              AND (
                  LOWER(title) LIKE LOWER(%s)
                  OR LOWER(description) LIKE LOWER(%s)
                  OR LOWER(subject) LIKE LOWER(%s)
                  OR LOWER(category) LIKE LOWER(%s)
              )
            ORDER BY created_at DESC
            """,
            (user_id, search_pattern, search_pattern, search_pattern, search_pattern)
        )
        rows = cur.fetchall()
        cur.close()
    return [_material_from_row(row) for row in rows]