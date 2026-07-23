from server.db.user_repository import get_rating, update_rating

K = 32


def _expected(rating_player: int, rating_opponent: int) -> float:
    return 1 / (1 + 10 ** ((rating_opponent - rating_player) / 400))


def update_ratings(winner: str, loser: str) -> None:
    """
    מחשב ומעדכן את הדירוג של שני השחקנים אחרי משחק.
    """
    rating_winner = get_rating(winner)
    rating_loser = get_rating(loser)

    expected_winner = _expected(rating_winner, rating_loser)
    expected_loser = _expected(rating_loser, rating_winner)

    new_winner = round(rating_winner + K * (1 - expected_winner))
    new_loser = round(rating_loser + K * (0 - expected_loser))

    update_rating(winner, new_winner)
    update_rating(loser, new_loser)