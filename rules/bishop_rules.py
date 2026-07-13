from model.board import Board
from model.piece import Piece
from model.position import Position


def get_bishop_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים שאליהם הרץ יכול לצעוד או לאכול בארבעת האלכסונים"""
    destinations = set()
    current_pos = piece.cell

    # הגדרת 4 כיווני האלכסון: (שינוי בשורה, שינוי בעמודה)
    # למעלה-ימינה, למעלה-שמאלה, למטה-ימינה, למטה-שמאלה
    directions = [
        (1, 1),  # Up-Right
        (1, -1),  # Up-Left
        (-1, 1),  # Down-Right
        (-1, -1)  # Down-Left
    ]

    for d_row, d_col in directions:
        step = 1
        while True:
            # המתמטיקה המוכרת: גם השורה וגם העמודה משתנות ביחד בכל צעד!
            next_pos = Position(row=current_pos.row + (d_row * step), col=current_pos.col + (d_col * step))

            if not board.is_in_bounds(next_pos):
                break

            target_piece = board.get_piece_at(next_pos)

            if target_piece is None:
                destinations.add(next_pos)
                step += 1
            else:
                if target_piece.color != piece.color:
                    destinations.add(next_pos)  # אוייב - מותר לאכול
                break  # חסום!

    return destinations