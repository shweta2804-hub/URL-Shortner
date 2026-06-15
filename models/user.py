from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def _user_from_row(row):
    """Convert a database row to a user dict, EXCLUDING the password hash."""
    return {
        "id": row[0],
        "username": row[1],
        "email": row[2],
        "created_at": row[3].isoformat()
    }


def create_user(username, email, password):
    """Insert a new user and return the user dict (password excluded)."""
    hashed = generate_password_hash(password)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING id, username, email, created_at
            """,
            (username, email, hashed)
        )
        user = cur.fetchone()
        cur.close()
    return _user_from_row(user)


def get_user_by_email(email):
    """Return user dict (WITH password hash for verification) or None."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, username, email, password, created_at
            FROM users WHERE email = %s
            """,
            (email,)
        )
        row = cur.fetchone()
        cur.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "password": row[3],
            "created_at": row[4].isoformat()
        }
    return None


def get_public_user_by_email(email):
    """Return user dict WITHOUT password hash, or None."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, created_at FROM users WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        cur.close()
    return _user_from_row(row) if row else None


def get_user_by_id(user_id):
    """Return user dict (without password) by id, or None."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        row = cur.fetchone()
        cur.close()
    return _user_from_row(row) if row else None


def verify_password(email, password):
    """
    Verify a password against the stored hash.

    Returns the user dict (without password) on success, or None.
    This prevents password hashes from leaking through API responses.
    """
    user = get_user_by_email(email)
    if user and check_password_hash(user["password"], password):
        # Return user WITHOUT the password hash
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    return None
