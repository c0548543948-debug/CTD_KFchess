from model.board import Board
from model.piece import Piece
from model.position import Position


def get_rook_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים שאליהם הצריח יכול לצעוד או לאכול בארבעת הכיוונים הישרים"""
    destinations = set()
    current_pos = piece.cell

    # הגדרת 4 כיווני התנועה: (שינוי בשורה, שינוי בעמודה)
    # למעלה, למטה, ימינה, שמאלה
    directions = [
        (1, 0),  # Up
        (-1, 0),  # Down
        (0, 1),  # Right
        (0, -1)  # Left
    ]

    for d_row, d_col in directions:
        # מתחילים לצעוד צעד אחד מהמיקום הנוכחי בכיוון הנבחר
        step = 1
        while True:
            next_pos = Position(row=current_pos.row + (d_row * step), col=current_pos.col + (d_col * step))

            # אם יצאנו מגבולות הלוח, הכיוון הזה הסתיים - עוברים לכיוון הבא
            if not board.is_in_bounds(next_pos):
                break

            target_piece = board.get_piece_at(next_pos)

            if target_piece is None:
                # המשבצת ריקה - המהלך חוקי וממשיכים לצעוד הלאה בכיוון הזה
                destinations.add(next_pos)
                step += 1
            else:
                # נתקלנו בכלי!
                if target_piece.color != piece.color:
                    # זה אויב! מותר לאכול אותו (המשבצת חוקית)
                    destinations.add(next_pos)

                # בין אם זה אויב ובין אם זה חבר - הצריח חסום ולא יכול להמשיך הלאה בכיוון הזה
                break

    return destinations