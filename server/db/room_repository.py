# server/db/room_repository.py

_rooms: dict = {}  # room_id → RoomState


def create_room(room_id: str, username: str):
    _rooms[room_id] = {"room_id": room_id, "white": username, "black": None, "viewers": []}


def get_room(room_id: str):
    return _rooms.get(room_id)


def join_room(room_id: str, username: str):
    room = _rooms.get(room_id)
    if room is None:
        return None
    if room["black"] is None:
        room["black"] = username
    else:
        room["viewers"].append(username)
    return room


def delete_room(room_id: str):
    _rooms.pop(room_id, None)