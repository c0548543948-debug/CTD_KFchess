import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.queen_rules import get_queen_destinations


# 2. הוסיפי את המחלקה הזו בסוף הקובץ:
class TestQueenRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_queen_combines_rook_and_bishop(self):
        """בדיקה שמלכה במרכז לוח ריק מקבלת את כל המהלכים של צריח ורץ יחד"""
        queen = Piece(piece_id="w_queen_1", color="white", kind="queen", cell=Position(row=3, col=3))
        self.board.add_piece(queen)

        moves = get_queen_destinations(self.board, queen)

        # צריח במרכז (14 משבצות) + רץ במרכז (13 משבצות) = 27 משבצות שליטה למלכה!
        self.assertEqual(len(moves), 27)

        # בדיקה שהיא מגיעה גם לקו ישר וגם לאלכסון
        self.assertIn(Position(row=7, col=3), moves)  # קו ישר (צריח)
        self.assertIn(Position(row=7, col=7), moves)  # אלכסון (רץ)