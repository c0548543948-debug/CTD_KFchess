from model.position import Position
from model.piece import Piece


class Motion:
    def __init__(self, piece: Piece, target: Position, duration_ms: int = 1000):
        self.piece: Piece = piece
        self.source: Position = piece.cell
        self.target: Position = target
        self.time_left: int = duration_ms  # הזמן שנותר לתנועה במילישניות

        # חישוב כל משבצות המסלול שהכלי עובר בהן (ה-Common Route)
        self.route_cells: set[Position] = self._calculate_route_cells()

    def _calculate_route_cells(self) -> set[Position]:
        """
        מחשב ומחזיר את כל המשבצות שהכלי תופס/עובר דרכן במהלך התנועה שלו.
        כולל את משבצת המקור ומשבצת היעד.
        """
        cells = {self.source, self.target}

        # אם זה פרש, הוא מדלג! לכן הוא תופס רק את המקור והיעד ולא את משבצות הביניים
        if self.piece.kind == "knight":
            return cells

        # עבור כלים אחרים (צריח, רץ, מלכה, מלך, רגלי) - נחשב את משבצות הביניים
        row_diff = self.target.row - self.source.row
        col_diff = self.target.col - self.source.col

        # מציאת כיוון הצעד (1, 0, או 1-)
        step_row = (row_diff // abs(row_diff)) if row_diff != 0 else 0
        step_col = (col_diff // abs(col_diff)) if col_diff != 0 else 0

        current_row = self.source.row + step_row
        current_col = self.source.col + step_col

        # מתקדמים צעד אחר צעד מהמקור ליעד ומכניסים את המשבצות למסלול
        while (current_row, current_col) != (self.target.row, self.target.col):
            cells.add(Position(row=current_row, col=current_col))
            current_row += step_row
            current_col += step_col

        return cells

    def advance_time(self, ms: int) -> None:
        """מוריד את הזמן שנותר לתנועה"""
        self.time_left = max(0, self.time_left - ms)

    @property
    def is_finished(self) -> bool:
        """מחזיר True אם התנועה הסתיימה (הזמן הגיע ל-0)"""
        return self.time_left <= 0