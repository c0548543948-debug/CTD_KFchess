from pydantic import BaseModel


class MoveRequest(BaseModel):
    """בקשת תזוזה מהקליינט — למשל 'e2e5'"""
    command: str


class MoveEvent(BaseModel):
    """אירוע תזוזה שהשרת שולח לכל הקליינטים"""
    piece_id: str
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    start_time_ms: int
    duration_ms: int


class JumpEvent(BaseModel):
    """אירוע קפיצה שהשרת שולח לכל הקליינטים"""
    piece_id: str
    row: int
    col: int
    start_time_ms: int
    duration_ms: int


class GameStateSnapshot(BaseModel):
    """מצב הלוח הסטטי — נשלח כשמשהו משתנה"""
    pieces: list[dict]
    game_over: bool
    winner: str | None = None