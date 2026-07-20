from __future__ import annotations
from model.position import Position

# פרמטרי הלוח האמיתיים — חייבים להתאים לחישובים ב-renderer.py
# תמונת הלוח היא 822×828 פיקסלים עם גבול קישוטי של 2px משמאל ו-6px מלמעלה
BOARD_OFFSET_X = 2
BOARD_OFFSET_Y = 6
BOARD_CELL_W   = (822 - BOARD_OFFSET_X) / 8.0   # ≈ 102.5 px
BOARD_CELL_H   = (828 - BOARD_OFFSET_Y) / 8.0   # ≈ 102.75 px


class BoardMapper:
    def __init__(self):
        """
        מאתחל את הממפה עם פרמטרי הלוח האמיתיים (offset + גודל תא מדויק).
        """
        self._offset_x = BOARD_OFFSET_X
        self._offset_y = BOARD_OFFSET_Y
        self._cell_w   = BOARD_CELL_W
        self._cell_h   = BOARD_CELL_H

    def to_board_position(self, x: int, y: int) -> Position:
        """
        ממיר קואורדינטות פיקסלים (x, y) מהמסך לאובייקט Position של הלוח.
        מחשב לפי offset וגודל תא אמיתי — לא 100px גלובלי.
        """
        col = int((x - self._offset_x) / self._cell_w)
        row = int((y - self._offset_y) / self._cell_h)
        return Position(row=row, col=col)

    def to_pixel_coordinates(self, position: Position) -> tuple[int, int]:
        """
        ממיר מיקום לוח חזרה לפיקסלים של מרכז התא.
        """
        x = int(self._offset_x + position.col * self._cell_w + self._cell_w / 2)
        y = int(self._offset_y + position.row * self._cell_h + self._cell_h / 2)
        return x, y