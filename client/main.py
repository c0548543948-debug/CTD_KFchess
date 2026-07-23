
import time
import cv2

from client.shell_login import login, show_menu
from client.network.ws_client import WSClient
from client.input.board_mapper import BoardMapper
from client.input.controller import GameController
from rendering.sprite_manager import SpriteManager
from rendering.renderer import Renderer

ASSETS_PATH = "rendering/assets"
WINDOW_NAME = "KungFu Chess"

# מצב גלובלי שמתעדכן מהשרת
current_snapshot = None
active_motions = []


def on_server_message(data: dict):
    """
    נקרא כל פעם שמגיע מסר מהשרת.
    מעדכן את ה-snapshot וה-motions.
    """
    global current_snapshot, active_motions

    msg_type = data.get("type")

    if msg_type == "snapshot":
        current_snapshot = data["snapshot"]

    elif msg_type == "motions":
        active_motions = data["motions"]


def make_mouse_callback(controller: GameController):
    def on_mouse(event, x, y, flags, param):
        if event in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_LBUTTONDBLCLK):
            controller.handle_click(x, y)
    return on_mouse


def main():
    global current_snapshot, active_motions

    # --- שלב 1: לוגין ---
    username, password = login()

    # --- שלב 2: חיבור לשרת ---
    ws = WSClient(on_message=on_server_message)
    ws.connect("ws://localhost:8000/ws")

    # שליחת פרטי לוגין לשרת
    ws.send({"type": "login", "username": username, "password": password})

    # המתנה לאישור מהשרת + קבלת דירוג
    # (בינתיים נחכה שנייה — בהמשך נטפל בזה נכון)
    time.sleep(1)

    # --- שלב 3: תפריט ---
    rating = current_snapshot.get("rating", 1200) if current_snapshot else 1200
    choice = show_menu(username, rating)
    ws.send({"type": choice})

    # --- שלב 4: אתחול רכיבי view ---
    sprite_manager = SpriteManager(ASSETS_PATH, piece_size=80)
    renderer = Renderer(sprite_manager, board_path=f"{ASSETS_PATH}/board.png")
    mapper = BoardMapper()
    controller = GameController(
        ws_client=ws,
        board_mapper=mapper,
        get_snapshot=lambda: current_snapshot
    )

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, make_mouse_callback(controller))

    start_time = time.time()

    # --- שלב 5: לולאת 16ms ---
    while True:
        if current_snapshot is None:
            # עדיין מחכים לסנאפשוט ראשון מהשרת
            cv2.waitKey(16)
            continue

        elapsed_ms = int((time.time() - start_time) * 1000)

        selected_pos = controller.selected_position
        canvas = renderer.render(
            current_snapshot,
            active_motions,
            elapsed_ms,
            selected_pos=selected_pos
        )

        cv2.imshow(WINDOW_NAME, canvas.img)

        key = cv2.waitKey(16) & 0xFF
        if key == 27:
            break
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()