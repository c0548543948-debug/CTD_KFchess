from model.position import Position
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper  # ייבוא של הממפה החדש


class GameController:
    def __init__(self, game_engine: GameEngine, board_mapper: BoardMapper):
        """
        מאתחל את הבקר עם מנוע המשחק וה-BoardMapper האחראי על המרת הקואורדינטות.
        """
        self._engine = game_engine
        self._mapper = board_mapper
        # מצב הסימון הנוכחי (None אומר שאין כלי מסומן)
        self._selected_position = None

    def handle_click(self, x: int, y: int) -> None:
        """
        השער המרכזי לקבלת קואורדינטות הלחיצה מה-UI (בפיקסלים).
        """
        # 1. תרגום הפיקסלים למשבצת בעזרת ה-BoardMapper
        clicked_pos = self._mapper.to_board_position(x, y)

        # שליפת הלוח מהסנאפשוט של המנוע
        current_board = self._engine.get_snapshot().board

        # 2. בדיקה האם הלחיצה חרגה מגבולות הלוח
        if not current_board.is_in_bounds(clicked_pos):
            # אם יש כלי מסומן - לחיצה מחוץ ללוח מבטלת את הסימון (חוק 8)
            if self._selected_position is not None:
                self._selected_position = None
            # אם אין כלי מסומן - מתעלמים לחלוטין (חוק 7)
            return

        # 3. הלחיצה בתוך גבולות הלוח:

        # תרחיש א': לחיצה ראשונה (אין כלי מסומן)
        if self._selected_position is None:
            piece = current_board.get_piece_at(clicked_pos)
            if piece is None:
                # חוק 9: מתעלמים מלחיצה ראשונה על תא ריק
                return
            else:
                # חוק 4: מסמנים את הכלי
                self._selected_position = clicked_pos
                return

        # תרחיש ב': לחיצה שנייה (כבר יש כלי מסומן)
        else:
            # שומרים את המקור ומנקים את הסימון מיידית (חוק 5 + 6)
            source_pos = self._selected_position
            self._selected_position = None

            # שליחת הבקשה הרשמית למנוע המשחק
            self._engine.move_request(source_pos, clicked_pos)

    @property
    def selected_position(self) -> Position:
        """מאפשר ל-UI לקרוא את המיקום המסומן לצורך הדגשה גרפית"""
        return self._selected_position