
from __future__ import annotations
import time
from engine.model.position import Position
from client.input.board_mapper import BoardMapper
from client.network.ws_client import WSClient
from client.input.config import KIND_TO_LETTER, COLOR_TO_LETTER, COL_TO_LETTER, DOUBLE_CLICK_THRESHOLD

class GameController:
    def __init__(self, ws_client: WSClient, board_mapper: BoardMapper, get_snapshot):
        self._ws = ws_client
        self._mapper = board_mapper
        self._get_snapshot = get_snapshot
        self._selected_position = None
        self._last_click_time: float = 0.0
        self._last_click_pos: Position | None = None

    def handle_click(self, x: int, y: int) -> None:
        clicked_pos = self._mapper.to_board_position(x, y)
        current_board = self._get_snapshot().board

        if not current_board.is_in_bounds(clicked_pos):
            self._selected_position = None
            self._last_click_pos = None
            return

        now = time.time()
        is_double_click = (
            self._last_click_pos == clicked_pos
            and (now - self._last_click_time) < DOUBLE_CLICK_THRESHOLD
        )

        self._last_click_time = now
        self._last_click_pos = clicked_pos

        clicked_piece = current_board.get_piece_at(clicked_pos)

        if is_double_click and clicked_piece is not None:
            self._selected_position = None
            self._ws.send(self._build_jump(clicked_piece, clicked_pos))
            return

        if self._selected_position is None:
            if clicked_piece is not None:
                self._selected_position = clicked_pos
            return

        source_pos = self._selected_position
        source_piece = current_board.get_piece_at(source_pos)

        if clicked_pos == source_pos:
            self._selected_position = None
            self._ws.send(self._build_jump(source_piece, source_pos))
            return

        if (source_piece is not None and clicked_piece is not None
                and source_piece.color == clicked_piece.color):
            self._selected_position = clicked_pos
            return

        self._selected_position = None
        self._ws.send(self._build_move(source_piece, source_pos, clicked_pos))

    def _pos_to_str(self, pos: Position) -> str:
        col_letter = COL_TO_LETTER[pos.col]
        row_number = str(pos.row + 1)
        return col_letter + row_number

    def _build_move(self, piece, source: Position, target: Position) -> str:
        color = COLOR_TO_LETTER[piece.color]
        kind  = KIND_TO_LETTER[piece.kind]
        src   = self._pos_to_str(source)
        tgt   = self._pos_to_str(target)
        return color + kind + src + tgt

    def _build_jump(self, piece, pos: Position) -> str:
        color = COLOR_TO_LETTER[piece.color]
        kind  = KIND_TO_LETTER[piece.kind]
        p     = self._pos_to_str(pos)
        return color + kind + p

    @property
    def selected_position(self) -> Position:
        return self._selected_position