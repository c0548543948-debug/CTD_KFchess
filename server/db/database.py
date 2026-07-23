import sqlite3
from server.config import DB_PATH


def get_connection() -> sqlite3.Connection:
    """מחזיר חיבור למסד הנתונים."""
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """יוצר את הטבלאות אם הן לא קיימות."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                rating   INTEGER NOT NULL DEFAULT 1200
            )
        """)
        conn.commit()