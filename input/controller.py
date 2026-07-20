from __future__ import annotations
import time
from model.position import Position
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper

# זמן מקסימלי בין שתי לחיצות כדי שייחשבו כ-double-click (בשניות)
DOUBLE_CLICK_THRESHOLD = 0.35

class GameController:
    def __init__(self, game_engine: GameEngine, board_mapper: BoardMapper):
        self._engine = game_engine
        self._mapper = board_mapper
        self._selected_position = None

        # לזיהוי double-click: זמן ומיקום הלחיצה הקודמת
        self._last_click_time: float = 0.0
        self._last_click_pos: Position | None = None

    def handle_click(self, x: int, y: int) -> None:
        clicked_pos = self._mapper.to_board_position(x, y)
        current_board = self._engine.get_snapshot().board

        if not current_board.is_in_bounds(clicked_pos):
            self._selected_position = None
            self._last_click_pos = None
            return

        now = time.time()
        is_double_click = (
            self._last_click_pos == clicked_pos
            and (now - self._last_click_time) < DOUBLE_CLICK_THRESHOLD
        )

        # עדכון מצב double-click לפני כל פעולה
        self._last_click_time = now
        self._last_click_pos = clicked_pos

        clicked_piece = current_board.get_piece_at(clicked_pos)

        # double-click על כלי → קפיצה מיידית, בלי צורך בסלקציה קודמת
        if is_double_click and clicked_piece is not None:
            self._selected_position = None
            self._engine.jump_request(clicked_pos)
            return

        # אין כלי מסומן — לחיצה ראשונה
        if self._selected_position is None:
            if clicked_piece is not None:
                self._selected_position = clicked_pos
            return

        source_pos = self._selected_position
        source_piece = current_board.get_piece_at(source_pos)

        # לחיצה על אותו כלי שכבר נבחר → קפיצה
        if clicked_pos == source_pos:
            self._selected_position = None
            self._engine.jump_request(source_pos)
            return

        # לחיצה על כלי חבר → החלפת סלקציה
        if (source_piece is not None and clicked_piece is not None
                and source_piece.color == clicked_piece.color):
            self._selected_position = clicked_pos
            return

        # הזזה
        self._selected_position = None
        self._engine.move_request(source_pos, clicked_pos)

    @property
    def selected_position(self) -> Position:
        return self._selected_position

    @property
    def selected_position(self) -> Position:
        return self._selected_position
