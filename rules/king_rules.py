from model.board import Board
from model.piece import Piece
from model.position import Position


def get_king_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים של המלך (צעד אחד לכל 8 הכיוונים)"""
    destinations = set()
    current_pos = piece.cell

    # הגדרת כל 8 הכיוונים האפשריים מסביב למלך
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1),  # ישרים (למעלה, למטה, ימינה, שמאלה)
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # אלכסונים
    ]

    for d_row, d_col in directions:
        # המלך זז רק צעד אחד, לכן אין צורך בלולאת while, פשוט בודקים את המיקום הבא
        next_pos = Position(row=current_pos.row + d_row, col=current_pos.col + d_col)

        # בודקים שהמשבצת בכלל על הלוח
        if board.is_in_bounds(next_pos):
            target_piece = board.get_piece_at(next_pos)

            # אם המשבצת ריקה, או שיש שם אויב - המהלך חוקי!
            if target_piece is None or target_piece.color != piece.color:
                destinations.add(next_pos)

    return destinations