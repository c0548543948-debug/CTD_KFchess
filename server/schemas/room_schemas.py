from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
    username: str


class JoinRoomRequest(BaseModel):
    username: str
    room_id: str


class RoomState(BaseModel):
    """פרטי החדר — נשלח לכל המשתתפים"""
    room_id: str
    white: str | None = None
    black: str | None = None
    viewers: list[str] = []