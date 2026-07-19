import pathlib
import cv2

# ייבוא מחלקת Img מאותה תיקייה
from img import Img


class SpriteManager:
    """
    אחראי על:
    1. טעינת כל הספריטים מהדיסק לזיכרון בעת האתחול
    2. החלטה איזה אנימציה להציג (idle / move / jump / short_rest)
    3. חישוב מתמטי של איזה פריים בתוך האנימציה להציג
    4. החזרת אובייקט Img של הפריים הנכון
    """

    # כמה פריימים של אנימציה מוצגים בשנייה
    FPS = 8

    # ממפה מ-kind של הכלי (מהמודל) לאות בשם תיקיית ה-assets
    # למשל: piece.kind == "bishop" → תיקיית "BB" או "BW"
    KIND_TO_LETTER = {
        "bishop": "B",
        "king":   "K",
        "knight": "N",
        "pawn":   "P",
        "queen":  "Q",
        "rook":   "R"
    }

    # ממפה מ-color של הכלי לאות בשם התיקייה
    COLOR_TO_LETTER = {
        "white": "W",
        "black": "B"
    }

    def __init__(self, assets_path: str, piece_size: int = 80):
        """
        assets_path - נתיב לתיקיית assets (שמכילה board.png ו-pieces_classic/)
        piece_size  - גודל הכלי בפיקסלים (ברירת מחדל: 80)
        """
        self._piece_size = piece_size

        # כמה מילישניות כל פריים מוצג? למשל FPS=8 → 125ms לפריים
        self._frame_duration_ms = 1000 // self.FPS

        # מילון מקונן שמחזיק את כל הספריטים טעונים בזיכרון:
        # { "BB": { "idle": [Img, Img, ...], "move": [...], ... }, "BW": { ... }, ... }
        self._sprites: dict = {}

        # טוען הכל מהדיסק לזיכרון — קורה פעם אחת בלבד בהפעלה
        self._load_all_sprites(assets_path)

    # ------------------------------------------------------------------ #
    #  טעינה                                                               #
    # ------------------------------------------------------------------ #

    def _load_all_sprites(self, assets_path: str) -> None:
        """
        עוברת על כל תיקיית כלי (BB, BW, KB, ...) ועל כל state (idle, move, ...)
        וטוענת את הפריימים לזיכרון בסדר נכון.
        """
        pieces_root = pathlib.Path(assets_path) / "pieces_classic"

        for piece_folder in pieces_root.iterdir():
            # piece_folder.name = "BB", "BW", "KB" וכו'
            folder_key = piece_folder.name
            self._sprites[folder_key] = {}

            states_root = piece_folder / "states"
            for state_folder in states_root.iterdir():
                # state_folder.name = "idle", "move", "jump", "short_rest", "long_rest"
                state_name = state_folder.name

                sprites_dir = state_folder / "sprites"

                # ממיינים לפי שם הקובץ כך שהפריימים ייטענו בסדר 1, 2, 3, 4, 5
                # sorted() עם key=lambda f: f.name עובד כי השם מתחיל במספר
                sprite_files = sorted(sprites_dir.iterdir(), key=lambda f: f.name)

                frames = []
                for sprite_file in sprite_files:
                    # טוענים כל פריים ומשנים גודל ל-piece_size
                    img = Img().read(
                        str(sprite_file),
                        size=(self._piece_size, self._piece_size),
                        keep_aspect=True,           # שומרים יחס גובה-רוחב
                        interpolation=cv2.INTER_AREA  # INTER_AREA מתאים לכיווץ
                    )
                    frames.append(img)

                self._sprites[folder_key][state_name] = frames

    # ------------------------------------------------------------------ #
    #  עזר פנימי                                                           #
    # ------------------------------------------------------------------ #

    def _get_folder_key(self, piece) -> str:
        """
        ממיר אובייקט Piece לשם תיקיית ה-assets שלו.
        לדוגמה: bishop + black → "BB"
                 king   + white → "KW"
        """
        kind_letter  = self.KIND_TO_LETTER[piece.kind]
        color_letter = self.COLOR_TO_LETTER[piece.color]
        return kind_letter + color_letter

    def _pick_state_name(self, piece, is_moving: bool, is_jump: bool) -> str:
        """
        מחליט איזה אנימציה להפעיל לפי מצב הכלי:

        is_jump    → "jump"       (קפיצה הגנתית)
        is_moving  → "move"       (הליכה רגילה בין משבצות)
        cooldown>0 → "short_rest" (ממתין אחרי מהלך)
        אחרת       → "idle"       (עומד בשקט)
        """
        if is_jump:
            return "jump"
        if is_moving:
            return "move"
        if piece.cooldown_remaining > 0:
            return "short_rest"
        return "idle"

    # ------------------------------------------------------------------ #
    #  ממשק ציבורי                                                         #
    # ------------------------------------------------------------------ #

    def get_frame(self, piece, elapsed_ms: int,
                  is_moving: bool = False,
                  is_jump: bool = False) -> Img:
        """
        מחזיר את הפריים הנכון של האנימציה עבור הכלי בנקודת הזמן elapsed_ms.

        piece      - אובייקט Piece מהמודל
        elapsed_ms - כמה מילישניות עברו מתחילת המשחק (לחישוב הפריים)
        is_moving  - True אם הכלי כרגע בתנועה (ה-Renderer שולח את זה)
        is_jump    - True אם הכלי כרגע בקפיצה
        """
        folder_key = self._get_folder_key(piece)
        state_name = self._pick_state_name(piece, is_moving, is_jump)

        frames = self._sprites[folder_key][state_name]

        # חישוב מספר הפריים:
        # elapsed_ms // frame_duration_ms  = כמה פריימים כולל עברו מתחילת המשחק
        # % len(frames)                    = מודולו מספר הפריימים → סיבוב בלופ
        # דוגמה: elapsed=600ms, FPS=8 (125ms/frame), 5 פריימים
        #   600 // 125 = 4 פריימים עברו → 4 % 5 = פריים מספר 4
        frame_index = (elapsed_ms // self._frame_duration_ms) % len(frames)

        return frames[frame_index]
