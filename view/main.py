import sys
import pathlib
import time

# מוסיפים את תיקיית הבסיס של הפרויקט ל-Python path
# בלי זה Python לא ימצא את model, engine, input וכו'
# pathlib.Path(__file__).parent = תיקיית view/
# .parent שוב = תיקיית הבסיס של הפרויקט
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import cv2

# ייבוא רכיבי הלוגיקה מהפרויקט
from model.game_state import GameState
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import GameController
from io_utils.board_parser import BoardParser

# ייבוא רכיבי ה-View (מאותה תיקייה)
from sprite_manager import SpriteManager
from renderer import Renderer

# ------------------------------------------------------------------ #
#  הגדרות                                                              #
# ------------------------------------------------------------------ #

# לוח שחמט סטנדרטי בפורמט שה-BoardParser מבין
# b = black, w = white
# K=King, Q=Queen, R=Rook, B=Bishop, N=Knight, P=Pawn
INITIAL_BOARD = """\
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR"""

# נתיב לתיקיית ה-assets — יחסי לתיקיית view/ שממנה רצים
ASSETS_PATH = "assets"

# שם חלון OpenCV
WINDOW_NAME = "KungFu Chess"


# ------------------------------------------------------------------ #
#  Callback ללחיצות עכבר                                              #
# ------------------------------------------------------------------ #

# הפונקציה מוגדרת בחוץ כדי שתוכל לגשת ל-controller
# OpenCV דורש signature מסוים: (event, x, y, flags, param)
def make_mouse_callback(controller: GameController):
    """
    יוצרת פונקציית callback שמועברת ל-OpenCV.
    משתמשים ב-closure כדי שהפונקציה "תזכור" את ה-controller.
    """
    def on_mouse(event, x, y, flags, param):
        # EVENT_LBUTTONDOWN = לחיצה שמאלית בלבד (לא גרירה, לא שחרור)
        if event == cv2.EVENT_LBUTTONDOWN:
            # x, y הם קואורדינטות פיקסלים בחלון
            # ה-controller + BoardMapper ממירים אותם לשורה/עמודה לוגית
            controller.handle_click(x, y)
    return on_mouse


# ------------------------------------------------------------------ #
#  פונקציה ראשית                                                       #
# ------------------------------------------------------------------ #

def main():

    # --- בניית לוח ראשוני ---
    # BoardParser.parse() קורא את מחרוזת הלוח וממיר אותה לאובייקט Board
    board = BoardParser.parse(INITIAL_BOARD)

    # --- יצירת רכיבי הלוגיקה ---
    game_state = GameState(board)       # מצב המשחק (לוח + game_over + winner)
    arbiter    = RealTimeArbiter()      # מנהל את כל התנועות הפעילות
    engine     = GameEngine(game_state, arbiter)  # ממשק מרכזי ללוגיקת המשחק

    mapper     = BoardMapper()          # ממיר פיקסלים ↔ מיקום לוגי
    controller = GameController(engine, mapper)   # מנהל לחיצות המשתמש

    # --- בניית רכיבי ה-View ---
    # SpriteManager טוען את כל הספריטים לזיכרון — לוקח שנייה בהפעלה
    sprite_manager = SpriteManager(ASSETS_PATH, piece_size=80)

    # Renderer מקבל את SpriteManager ונתיב ללוח הריק
    renderer = Renderer(sprite_manager, board_path=f"{ASSETS_PATH}/board.png")

    # --- הגדרת חלון OpenCV ---
    cv2.namedWindow(WINDOW_NAME)

    # קישור פונקציית ה-callback ללחיצות עכבר לחלון
    cv2.setMouseCallback(WINDOW_NAME, make_mouse_callback(controller))

    # --- שעון ---
    start_time = time.time()   # זמן תחילת המשחק (לחישוב elapsed_ms)
    last_time  = start_time    # זמן הפריים הקודם (לחישוב delta_ms)

    # ------------------------------------------------------------------ #
    #  לולאת המשחק הראשית                                                  #
    # ------------------------------------------------------------------ #

    while True:
        now = time.time()

        # delta_ms = כמה זמן עבר מאז הפריים הקודם (בפועל)
        # זה מה שמועבר ל-engine.wait() כדי להקדים את שעון המשחק
        delta_ms = int((now - last_time) * 1000)
        last_time = now

        # elapsed_ms = כמה זמן עבר מתחילת המשחק (לחישוב פריים אנימציה)
        elapsed_ms = int((now - start_time) * 1000)

        # --- שלב 1: קידום הפיזיקה ---
        # advance_time בתוך engine.wait() מזיז את כל הכלים שבתנועה
        # ומטפל בהגעות, התנגשויות, cooldowns
        engine.wait(delta_ms)

        # --- שלב 2: קריאת מצב ---
        # snapshot = עותק של הלוח הסטטי (כלים שעל הלוח לפי הלוגיקה)
        snapshot = engine.get_snapshot()

        # motion_states = רשימת כלים שזזים כרגע עם מיקומי אינטרפולציה
        motion_states = engine.get_active_motion_states()

        # --- שלב 3: ציור ---
        # renderer מחזיר Img עם הפריים המצויר
        canvas = renderer.render(snapshot, motion_states, elapsed_ms)

        # הצגה בחלון OpenCV
        cv2.imshow(WINDOW_NAME, canvas.img)

        # --- שלב 4: קלט ---
        # waitKey(16) = מחכים עד 16ms לקלט מקלדת → ~60 פריימים לשנייה
        # & 0xFF = מסיכה לקחת רק 8 ביטים תחתונים (נחוץ בחלק מהמערכות)
        key = cv2.waitKey(16) & 0xFF

        # ESC = צא מהמשחק
        if key == 27:
            break

        # אם החלון נסגר ידנית (לחיצה על X)
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

    # סגירת כל חלונות OpenCV
    cv2.destroyAllWindows()


# ------------------------------------------------------------------ #
#  נקודת כניסה                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    # הרצה: cd view && python main.py
    main()
