from typing import Dict, Optional
from model.position import Position
from model.piece import Piece


class Board:
    def __init__(self, width, height):
        """מאתחל לוח משחק עם אורך ורוחב מוגדרים"""
        self._width = width
        self._height = height
        # מילון פנימי שממפה בין אובייקט Position לאובייקט Piece
        self._grid: Dict[Position, Piece] = {}

    # --- מאפיינים לקריאה בלבד (Dimensions) ---
    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    # --- בדיקת גבולות (In Bounds) ---
    def is_in_bounds(self, position: Position) -> bool:
        """בודק האם מיקום מסוים נמצא בתוך גבולות הלוח"""
        return 0 <= position.row < self._height and 0 <= position.col < self._width

    # --- תשאול חתיכה בתא (Query Cell) ---
    def get_piece_at(self, position: Position) -> Optional[Piece]:
        """מחזיר את הכלי שנמצא במיקום מסוים, או None אם התא ריק"""
        if not self.is_in_bounds(position):
            raise ValueError(f"Position {position} is out of board bounds.")
        return self._grid.get(position, None)

    # --- הוספת חתיכה (Add Piece & Reject Duplicate Occupancy) ---
    def add_piece(self, piece: Piece) -> None:
        """מוסיף כלי ללוח לפי המיקום המוגדר בתוכו. זורק שגיאה אם התא תפוס"""
        position = piece.cell

        if not self.is_in_bounds(position):
            raise ValueError(f"Cannot add piece: Position {position} is out of bounds.")

        if position in self._grid:
            raise ValueError(f"Cannot add piece: Cell {position} is already occupied.")

        # הוספת הכלי למבנה הנתונים
        self._grid[position] = piece

    # --- הסרת חתיכה (Remove Piece) ---
    def remove_piece_at(self, position: Position) -> Optional[Piece]:
        """מסיר את הכלי שנמצא במיקום מסוים ומחזיר אותו. מחזיר None אם התא היה ריק"""
        if not self.is_in_bounds(position):
            raise ValueError(f"Cannot remove piece: Position {position} is out of bounds.")

        # הפונקציה pop מסירה מהמילון ומחזירה את הערך, או None אם המפתח לא קיים
        return self._grid.pop(position, None)

    # --- הזזת חתיכה (Move Piece) ---
    def move_piece(self, source: Position, destination: Position) -> None:
        """
        מזיז כלי ממיקום מקור למיקום יעד.
        מסתמך על כך שחוקיות המהלך נבדקה מראש על ידי רכיב חיצוני.
        """
        if not self.is_in_bounds(source) or not self.is_in_bounds(destination):
            raise ValueError("Source or destination position is out of bounds.")

        piece = self.get_piece_at(source)
        if piece is None:
            raise ValueError(f"No piece found at source position {source} to move.")

        if destination in self._grid:
            raise ValueError(f"Destination cell {destination} is already occupied.")

        # 1. נסיר את הכלי ממיקום המקור במילון
        self.remove_piece_at(source)

        # 2. נעדכן את השדה הפנימי של הכלי עצמו למיקום החדש (Side Effect רצוי של הישות)
        piece.cell = destination

        # 3. נשמור את הכלי במיקום החדש במילון הלוח
        self._grid[destination] = piece

    def get_all_pieces(self) -> list:
        """
        מחזיר רשימה של כל הכלים שנמצאים כרגע על הלוח.
        הרשימה היא עותק של ה-values מה-dict הפנימי,
        כדי שאפשר יהיה לעבור עליה בלי לשנות את הלוח.
        """
        return list(self._grid.values())

    def clone(self) -> 'Board':
        """
        מייצר עותק חדש ועצמאי לחלוטין (Deep Copy) של הלוח וכל הכלים שעליו.
        מוודא שהלוח החדש לא חולק רפרנסים בזיכרון עם הלוח המקורי.
        """
        # 1. יצירת לוח חדש עם אותם הממדים
        cloned_board = Board(width=self.width, height=self.height)

        # 2. מעבר על הרשת (grid) של הלוח המקורי, שכפול הכלים והוספתם ללוח החדש
        for pos, piece in self._grid.items():
            # שימוש במתודת ה-clone של ה-Piece (שומרת על ה-cooldown_remaining וה-state)
            cloned_piece = piece.clone()
            cloned_board.add_piece(cloned_piece)

        return cloned_board

    # --- ייצוג קריא לצרכי דיבאג ---
    def __repr__(self) -> str:
        return f"Board(width={self._width}, height={self._height}, occupied_cells={len(self._grid)})"