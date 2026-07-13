# להוסיף את ה-import הזה בראש קובץ test_rules.py:
import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.rook_rules import get_rook_destinations


# להוסיף את המחלקה הזו בסוף הקובץ:
class TestRookRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_rook_moves_freely_on_empty_board(self):
        """בדיקה שצריח במרכז לוח ריק מקבל את כל צלב המשבצות שלו"""
        # נשים צריח ב-(3, 3)
        rook = Piece(piece_id="w_rook_1", color="white", kind="rook", cell=Position(row=3, col=3))
        self.board.add_piece(rook)

        moves = get_rook_destinations(self.board, rook)

        # בלוח 8x8, צריח במרכז תמיד שולט על 14 משבצות (7 בשורה שלו, 7 בעמודה שלו)
        self.assertEqual(len(moves), 14)
        # ודא משבצת קצה ספציפית למשל למעלה ולשמאלה
        self.assertIn(Position(row=7, col=3), moves)
        self.assertIn(Position(row=3, col=0), moves)

    def test_rook_blocked_by_friend_and_captures_enemy(self):
        """בדיקה שצריח נחסם על ידי חבר לצוות, ומסוגל לאכול אויב בקצה המסלול"""
        rook = Piece(piece_id="w_rook_1", color="white", kind="rook", cell=Position(row=3, col=3))
        friend = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=5, col=3))  # חוסם למעלה
        enemy = Piece(piece_id="b_pawn_1", color="black", kind="pawn", cell=Position(row=3, col=5))  # מטרה מימין

        self.board.add_piece(rook)
        self.board.add_piece(friend)
        self.board.add_piece(enemy)

        moves = get_rook_destinations(self.board, rook)

        # בדיקת כיוון למעלה (חבר ב-5,3): אמור להגיע רק ל-(4,3). המשבצות (5,3), (6,3), (7,3) חסומות!
        self.assertIn(Position(row=4, col=3), moves)
        self.assertNotIn(Position(row=5, col=3), moves)

        # בדיקת כיוון ימינה (אויב ב-3,5): אמור להגיע ל-(3,4) ולאכול ב-(3,5). המשבצות (3,6), (3,7) חסומות!
        self.assertIn(Position(row=3, col=4), moves)
        self.assertIn(Position(row=3, col=5), moves)
        self.assertNotIn(Position(row=3, col=6), moves)