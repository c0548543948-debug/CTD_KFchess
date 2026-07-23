from server.db.user_repository import register_user, authenticate_user, get_rating


def login(username: str, password: str) -> dict:
    """
    מנסה להתחבר — אם המשתמש לא קיים, רושם אותו אוטומטית.
    מחזיר dict עם success, rating, message.
    """
    # ניסיון אימות
    if authenticate_user(username, password):
        return {
            "success": True,
            "rating": get_rating(username),
            "message": None
        }

    # אם המשתמש לא קיים — נרשום אותו
    registered = register_user(username, password)
    if registered:
        return {
            "success": True,
            "rating": get_rating(username),
            "message": "נרשמת בהצלחה"
        }

    # המשתמש קיים אבל הסיסמה שגויה
    return {
        "success": False,
        "rating": None,
        "message": "סיסמה שגויה"
    }