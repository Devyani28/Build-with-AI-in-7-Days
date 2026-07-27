from typing import TypedDict, Optional
from pathlib import Path
import sqlite3


class UserRecord(TypedDict):
    email: str
    full_name: str
    role: str


def authenticate_user(
    email: str,
    password: str,
    role: Optional[str] = None
) -> UserRecord | None:

    # Same pattern as db_init.py
    ROOT = Path(__file__).resolve().parents[1]
    DB_PATH = ROOT / "ecommerce.db"

    query = """
        SELECT email, full_name, role
        FROM users
        WHERE email = ?
        AND password = ?
    """

    params = [email, password]

    if role:
        query += " AND role = ?"
        params.append(role)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute(query, params)

        row = cursor.fetchone()

        if row:
            return {
                "email": row[0],
                "full_name": row[1],
                "role": row[2],
            }

    return None

#test: uv run python -c "from support_chatbot.auth import authenticate_user; print(authenticate_user('admin@example.com','admin123'))"