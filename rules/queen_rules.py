from model.board import Board
from model.piece import Piece
from model.position import Position
from rules.rook_rules import get_rook_destinations
from rules.bishop_rules import get_bishop_destinations


def get_queen_destinations(board: Board, piece: Piece) -> set[Position]:
    """מחזיר את כל המיקומים החוקיים של המלכה (שילוב של צריח ורץ)"""
    # המלכה זזה כמו צריח...
    rook_moves = get_rook_destinations(board, piece)

    # ...וגם כמו רץ!
    bishop_moves = get_bishop_destinations(board, piece)

    # מחזירים את האיחוד של שתי הקבוצות (הסימן | משלב את כל האיברים משתי הקבוצות בלי כפילויות)
    return rook_moves | bishop_moves