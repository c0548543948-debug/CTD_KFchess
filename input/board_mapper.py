from model.position import Position
from config import CELL_SIZE  # מייבא את משתנה הסביבה שהגדרת בקונפיג שלך

class BoardMapper:
    def __init__(self, cell_size: int = CELL_SIZE):
        """
        מאתחל את הממפה עם גודל המשבצת מתוך ה-Config.
        """
        self.cell_size = cell_size

    def to_board_position(self, x: int, y: int) -> Position:
        """
        ממיר קואורדינטות פיקסלים (x, y) מהמסך לאובייקט Position של הלוח.
        """
        col = x // self.cell_size
        row = y // self.cell_size
        return Position(row=row, col=col)

    def to_pixel_coordinates(self, position: Position) -> tuple[int, int]:
        """
        (אופציונלי עבור ה-UI) ממיר מיקום לוח חזרה לפיקסלים של הפינה השמאלית העליונה של התא.
        """
        x = position.col * self.cell_size
        y = position.row * self.cell_size
        return x, y