import sys
import pathlib

# מוסיפים את תיקיית הבסיס של הפרויקט ל-Python path
# כך שנוכל לייבא מ-config, model וכו' גם כשרצים מתוך תיקיית view/
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import math
import cv2

from img import Img
from sprite_manager import SpriteManager

# CELL_SIZE = 100 (מוגדר ב-config.py בתיקיית הבסיס)
from config import CELL_SIZE, COOLDOWN_BY_KIND, DEFAULT_COOLDOWN

# גודל הכלי קצת פחות מגודל המשבצת — נראה יפה יותר ונותן שוליים
PIECE_SIZE = 80


class Renderer:
    """
    אחראי לצייר פריים שלם של המשחק:
    - מתחיל מתמונת לוח ריקה
    - מצייר כל כלי במיקומו הנכון (כולל מיקום אמצע-תנועה)
    - מצייר טקסט של מצב המשחק
    """

    def __init__(self, sprite_manager: SpriteManager, board_path: str):
        """
        sprite_manager - אובייקט SpriteManager שכבר טען את כל הספריטים
        board_path     - נתיב לתמונת הלוח הריק (board.png)
        """
        self._sprite_manager = sprite_manager

        # טוענים את תמונת הלוח הריק פעם אחת לזיכרון כ-numpy array גולמי
        # נשמור אותה כ-numpy array (לא Img) כדי שנוכל לעשות .copy() מהיר
        # בכל פריים, בלי לקרוא מהדיסק בכל פעם
        self._board_data = cv2.imread(board_path, cv2.IMREAD_UNCHANGED)
        if self._board_data is None:
            raise FileNotFoundError(f"לא ניתן לטעון את תמונת הלוח: {board_path}")

        # הלוח נטען כ-BGR (3 ערוצים), אבל הספריטים הם BGRA (4 ערוצים עם שקיפות).
        # ב-draw_on: אם sprite=4ch ו-canvas=3ch, הקוד ממיר את הsprite ל-3ch ומאבד את
        # ערוץ ה-alpha — הפיקסלים השקופים [0,0,0,0] הופכים ל-[0,0,0] = שחור מלא.
        # הפתרון: ממירים את הלוח ל-BGRA כאן, כך שה-draw_on רואה 4ch+4ch
        # ומבצע alpha-blending נכון במקום להשמיד את השקיפות.
        if self._board_data.shape[2] == 3:
            self._board_data = cv2.cvtColor(self._board_data, cv2.COLOR_BGR2BGRA)

        # תמונת הלוח היא 822×828 פיקסלים, לא 800×800.
        # יש גם גבול דקורטיבי: ~2px משמאל, ~6px מלמעלה.
        # מחשבים את גודל התא האמיתי מתוך ממדי התמונה בפועל.
        H, W = self._board_data.shape[:2]
        self._offset_x = 2    # פיקסלים של גבול שמאלי
        self._offset_y = 6    # פיקסלים של גבול עליון
        self._cell_w = (W - self._offset_x) / 8.0   # ~102.5 px
        self._cell_h = (H - self._offset_y) / 8.0   # ~102.75 px

    # ------------------------------------------------------------------ #
    #  ממשק ציבורי                                                         #
    # ------------------------------------------------------------------ #

    def render(self, snapshot, motion_states: list, elapsed_ms: int,
               selected_pos=None, valid_moves: list = None) -> Img:
        """
        מצייר פריים אחד של המשחק ומחזיר Img מוכן להצגה.

        snapshot      - GameState מ-engine.get_snapshot()
        motion_states - רשימה מ-engine.get_active_motion_states()
        elapsed_ms    - כמה מילישניות עברו מתחילת המשחק
        selected_pos  - Position של הכלי הנבחר (או None)
        valid_moves   - רשימת Position של מהלכים אפשריים (או None)
        """
        if valid_moves is None:
            valid_moves = []

        # שלב 1: יצירת עותק טרי של תמונת הלוח
        # חשוב: .copy() מחזיר numpy array חדש, כך שציורים על canvas
        # לא ישפיעו על self._board_data לפריימים הבאים
        canvas = Img()
        canvas.img = self._board_data.copy()

        # שלב 2: בניית מילון עזר: piece_id → מידע תנועה
        # זה מאפשר לנו לבדוק בO(1) אם כלי נמצא בתנועה
        # מבנה: { "wP_6_0": {"piece": ..., "row": 5.3, "col": 0.0, "is_jump": False}, ... }
        moving_info = {}
        for state in motion_states:
            moving_info[state["piece"].id] = state

        # שלב 3: ציור הדגשת הכלי הנבחר ואפשרויות המהלך
        if selected_pos is not None:
            self._draw_selection(canvas, selected_pos, elapsed_ms)
        for move_pos in valid_moves:
            self._draw_valid_move(canvas, move_pos, snapshot)

        # שלב 4: ציור כלים שנמצאים על הלוח הסטטי
        # get_all_pieces() מחזיר רשימה של כל הכלים שב-board._grid
        for piece in snapshot.board.get_all_pieces():

            if piece.id in moving_info:
                # הכלי בתנועה — משתמשים במיקום המאינטרפולציה (שבר עשרוני)
                # למשל row=5.7 מציין שהכלי עבר 70% מהדרך למשבצת 6
                info = moving_info[piece.id]
                row      = info["row"]
                col      = info["col"]
                is_jump  = info["is_jump"]
                is_moving = not is_jump  # קפיצה היא לא "הליכה"
            else:
                # הכלי דומם — משתמשים במיקום הלוגי שלו (מספר שלם)
                row      = float(piece.cell.row)
                col      = float(piece.cell.col)
                is_jump  = False
                is_moving = False

            # מצייר שכבת cooldown על הריבוע (לפני הספריט, כך שהספריט יהיה מעל)
            self._draw_cooldown_overlay(canvas, piece)

            # מבקשים את הפריים הנכון מה-SpriteManager
            frame = self._sprite_manager.get_frame(piece, elapsed_ms, is_moving, is_jump)

            # מצייר את הפריים על הקנבס
            self._draw_piece_at(canvas, frame, row, col)

        # שלב 5: ציור כלים שבאוויר (קפיצה)
        # כלים קופצים מוסרים מהלוח הסטטי (ב-start_jump_motion),
        # אז הם לא מופיעים ב-get_all_pieces() אבל כן ב-motion_states
        board_piece_ids = {p.id for p in snapshot.board.get_all_pieces()}
        for state in motion_states:
            if state["piece"].id not in board_piece_ids:
                # כלי שבאוויר — מציירים אותו במיקום המאינטרפולציה
                piece = state["piece"]
                row   = state["row"]
                col   = state["col"]

                # חישוב offset אנכי פרבולי לאפקט קפיצה:
                # t=0 ot=1 → offset=0 (ריצפה), t=0.5 → offset מקסימלי (שיא)
                # הנוסחה: 4 * t * (1-t) נותנת פרבולה 0→1→0
                # המיינוס מוריד את הכלי מעלה (row קטן יותר = גבוה יותר על המסך)
                t = state.get("jump_fraction", 0.0)
                parabola = 4.0 * t * (1.0 - t)          # 0 → 1 → 0
                max_height_rows = 0.9                     # גובה מקסימלי ביחידות שורות
                jump_row_offset = -parabola * max_height_rows

                frame = self._sprite_manager.get_frame(
                    piece, elapsed_ms, is_moving=False, is_jump=True
                )
                self._draw_piece_at(canvas, frame, row + jump_row_offset, col)

        # שלב 5: טקסט מצב המשחק
        if snapshot.game_over:
            # מציגים בגדול במרכז הלוח
            canvas.put_text(
                f"WINNER: {snapshot.winner.upper()}",
                x=80,
                y=420,
                font_size=2.0,
                color=(0, 255, 0, 255),
                thickness=4
            )

        return canvas

    # ------------------------------------------------------------------ #
    #  עזר פנימי                                                           #
    # ------------------------------------------------------------------ #

    def _draw_piece_at(self, canvas: Img, frame: Img, row: float, col: float) -> None:
        """
        מדביק פריים של כלי על הקנבס.

        row, col יכולים להיות שבר עשרוני (למשל 5.7) בזמן תנועה —
        לכן ממירים ל-int רק בסוף, אחרי חישוב מרכז הפיקסל.

        חישוב:
          מרכז המשבצת = offset + מיקום_לוגי * cell_size + cell_size/2
          פינה שמאלית עליונה של הכלי = מרכז - PIECE_SIZE/2
        """
        # מרכז המשבצת בפיקסלים — כולל offset של גבול הלוח
        center_x = int(self._offset_x + col * self._cell_w + self._cell_w / 2)
        center_y = int(self._offset_y + row * self._cell_h + self._cell_h / 2)

        # פינה שמאלית עליונה — ממנה מתחיל הציור
        draw_x = center_x - PIECE_SIZE // 2
        draw_y = center_y - PIECE_SIZE // 2

        # בדיקת גבולות: אם הכלי חורג מתמונת הלוח — מדלגים (לא קורסים)
        H, W = canvas.img.shape[:2]
        if draw_x < 0 or draw_y < 0 or draw_x + PIECE_SIZE > W or draw_y + PIECE_SIZE > H:
            return

        # הדבקה עם תמיכה בשקיפות (alpha) דרך מתודת draw_on של Img
        frame.draw_on(canvas, draw_x, draw_y)

    def _draw_cooldown_overlay(self, canvas: Img, piece) -> None:
        """
        מצייר אפקט cooldown על המשבצת של הכלי:
        - בהתחלה: כל הריבוע כתום מלא
        - לאט לאט: הצבע המקורי מתגלה מלמעלה למטה
        - בסוף: הריבוע חוזר לצבעו המקורי לחלוטין
        """
        if piece.cooldown_remaining <= 0:
            return

        max_cooldown = COOLDOWN_BY_KIND.get(piece.kind, DEFAULT_COOLDOWN)

        # ratio: 1.0 = cooldown מלא (כל הריבוע אפור)
        #        0.0 = cooldown נגמר (אין אפור)
        ratio = piece.cooldown_remaining / max_cooldown

        # כמה פיקסלים מהריבוע עדיין אפורים (תמיד בתחתית)
        # ratio=1.0 → gray_height = cell_h (כל הריבוע)
        # ratio=0.5 → gray_height = cell_h/2 (חצי תחתון)
        # ratio=0.0 → gray_height = 0 (כלום)
        cell_w = int(self._cell_w)
        cell_h = int(self._cell_h)
        gray_height = int(ratio * cell_h)
        if gray_height <= 0:
            return

        # פינה שמאלית עליונה של המשבצת — כולל offset של גבול הלוח
        sq_x = int(self._offset_x + piece.cell.col * self._cell_w)
        sq_y = int(self._offset_y + piece.cell.row * self._cell_h)

        # החלק האפור תמיד בתחתית הריבוע ומתכווץ כלפי מטה
        gray_y_start = sq_y + (cell_h - gray_height)
        gray_y_end   = sq_y + cell_h

        # בדיקת גבולות
        H, W = canvas.img.shape[:2]
        x1 = max(0, sq_x)
        y1 = max(0, gray_y_start)
        x2 = min(W, sq_x + cell_w)
        y2 = min(H, gray_y_end)
        if x1 >= x2 or y1 >= y2:
            return

        # אפור בינוני: BGR = [140, 140, 140]
        channels = canvas.img.shape[2]
        if channels == 4:
            canvas.img[y1:y2, x1:x2] = [140, 140, 140, 255]  # BGRA
        else:
            canvas.img[y1:y2, x1:x2] = [140, 140, 140]        # BGR

    def _draw_selection(self, canvas: Img, selected_pos, elapsed_ms: int) -> None:
        """
        מצייר מסגרת מהבהבת סביב המשבצת של הכלי הנבחר.

        האפקט: מסגרת צהובה/זהב שעוברת pulse — עוצמת הצבע גדלה וקטנה
        בגל סינוס עם תדר של ~2Hz (מחזור כל 500ms).

        math.sin מחזיר ערך בין -1 ל-1.
        (sin+1)/2 מנרמל אותו ל-0..1.
        משתמשים בזה לאינטרפולציה בין עוצמה מינימלית למקסימלית.
        """
        row = selected_pos.row
        col = selected_pos.col

        # פינה שמאלית עליונה של המשבצת
        x1 = int(self._offset_x + col * self._cell_w)
        y1 = int(self._offset_y + row * self._cell_h)
        x2 = int(x1 + self._cell_w)
        y2 = int(y1 + self._cell_h)

        # pulse: 0.0 עד 1.0, מחזור כל ~500ms
        pulse = (math.sin(elapsed_ms / 250.0) + 1.0) / 2.0

        # עוצמת הצבע: בין 160 ל-255 (תמיד גלוי, לא נכבה לגמרי)
        intensity = int(160 + pulse * 95)

        # צהוב: B=0, G=intensity, R=intensity (BGR)
        color = (0, intensity, intensity, 255)

        # עובי המסגרת: 3 פיקסלים
        thickness = 3

        # cv2.rectangle מקבל (canvas, pt1, pt2, color, thickness)
        # כשthickness > 0 מציירים רק את המסגרת (לא מלא)
        cv2.rectangle(canvas.img, (x1, y1), (x2, y2), color, thickness)

    def _draw_valid_move(self, canvas: Img, move_pos, snapshot) -> None:
        """
        מצייר ריבוע צהוב שקוף חלקית על משבצת יעד אפשרית.

        alpha blending ידני: pixel_out = pixel_bg * (1-alpha) + yellow * alpha
        cv2.rectangle לא תומך ב-alpha, אז עושים זאת ישירות על מערך ה-numpy.
        """
        import numpy as np

        row = move_pos.row
        col = move_pos.col

        # גבולות המשבצת בפיקסלים
        x1 = int(self._offset_x + col * self._cell_w)
        y1 = int(self._offset_y + row * self._cell_h)
        x2 = int(x1 + self._cell_w)
        y2 = int(y1 + self._cell_h)

        # בדיקת גבולות
        H, W = canvas.img.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(W, x2)
        y2 = min(H, y2)
        if x1 >= x2 or y1 >= y2:
            return

        # alpha = כמה "צהוב" מתווסף — 0.0 שקוף לגמרי, 1.0 אטום לגמרי
        alpha = 0.35

        # צהוב ב-BGR: B=0, G=220, R=220
        yellow = np.array([0, 220, 220], dtype=np.float32)

        # שולפים את אזור הריבוע מהקנבס
        region = canvas.img[y1:y2, x1:x2].astype(np.float32)

        # מבצעים blending על ערוצי BGR בלבד (3 ערוצים ראשונים)
        region[..., :3] = region[..., :3] * (1 - alpha) + yellow * alpha

        # כותבים בחזרה לקנבס
        canvas.img[y1:y2, x1:x2] = region.astype(canvas.img.dtype)
