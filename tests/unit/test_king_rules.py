import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.king_rules import get_king_destinations


# 2. הוסיפי את המחלקה הזו בסוף הקובץ:
class TestKingRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_king_moves_one_step_in_all_directions(self):
        """בדיקה שמלך במרכז לוח ריק יכול לזוז רק משבצת אחת לכל 8 הכיוונים"""
        king = Piece(piece_id="w_king_1", color="white", kind="king", cell=Position(row=3, col=3))
        self.board.add_piece(king)

        moves = get_king_destinations(self.board, king)

        # מלך במרכז מוקף בדיוק ב-8 משבצות
        self.assertEqual(len(moves), 8)
        # ודא שהוא מגיע למשבצת סמוכה, אבל לא למשבצת רחוקה
        self.assertIn(Position(row=4, col=4), moves)  # צעד אחד באלכסון
        self.assertNotIn(Position(row=5, col=5), moves)  # שני צעדים (אסור לו!)

    def test_king_blocked_by_friend_and_captures_enemy(self):
        """בדיקה שהמלך נחסם על ידי חבר לצוות ומסוגל לאכול אויב שנמצא צעד אחד לידו"""
        king = Piece(piece_id="w_king_1", color="white", kind="king", cell=Position(row=3, col=3))
        friend = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=4, col=3))  # חבר ישירות מעליו
        enemy = Piece(piece_id="b_pawn_1", color="black", kind="pawn", cell=Position(row=3, col=4))  # אויב מימינו

        self.board.add_piece(king)
        self.board.add_piece(friend)
        self.board.add_piece(enemy)

        moves = get_king_destinations(self.board, king)

        self.assertNotIn(Position(row=4, col=3), moves)  # המשבצת של החבר חסומה
        self.assertIn(Position(row=3, col=4), moves)  # המשבצת של האויב חוקית (לאכילה)