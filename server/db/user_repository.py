import sqlite3
from server.db.database import get_connection
from server.config import STARTING_RATING


def register_user(username: str, password: str) -> bool:
    """
    רושם משתמש חדש.
    מחזיר True אם הצליח, False אם השם כבר תפוס.
    """
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password, rating) VALUES (?, ?, ?)",
                (username, password, STARTING_RATING)
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def authenticate_user(username: str, password: str) -> bool:
    """
    מאמת שם משתמש וסיסמה.
    מחזיר True אם נכון, False אחרת.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    if row is None:
        return False
    return row[0] == password


def get_rating(username: str) -> int:
    """מחזיר את הדירוג של המשתמש."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT rating FROM users WHERE username = ?",
            (username,)
        ).fetchone()
    return row[0] if row else STARTING_RATING


def update_rating(username: str, new_rating: int) -> None:
    """מעדכן את הדירוג של המשתמש."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET rating = ? WHERE username = ?",
            (new_rating, username)
        )
        conn.commit()