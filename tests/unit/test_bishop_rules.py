
import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.bishop_rules import get_bishop_destinations


# 2. הוסיפי את המחלקה הזו בסוף הקובץ:
class TestBishopRules(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_bishop_moves_freely_on_empty_board(self):
        """בדיקה שרץ במרכז לוח ריק נע בצורת X ארוכה"""
        # נשים רץ ב-(3, 3)
        bishop = Piece(piece_id="w_bishop_1", color="white", kind="bishop", cell=Position(row=3, col=3))
        self.board.add_piece(bishop)

        moves = get_bishop_destinations(self.board, bishop)

        # במיקום (3,3) בלוח 8x8, לרץ יש בדיוק 13 משבצות אלכסוניות פנויות
        self.assertEqual(len(moves), 13)
        # נוודא שהוא מגיע לפינות ספציפיות
        self.assertIn(Position(row=7, col=7), moves)  # למעלה-ימינה בסוף
        self.assertIn(Position(row=0, col=0), moves)  # למטה-שמאלה בסוף

    def test_bishop_blocked_by_friend_and_captures_enemy(self):
        """בדיקה שרץ נחסם על ידי חבר באלכסון אחד, ואוכל אויב באלכסון אחר"""
        bishop = Piece(piece_id="w_bishop_1", color="white", kind="bishop", cell=Position(row=3, col=3))
        friend = Piece(piece_id="w_pawn_1", color="white", kind="pawn", cell=Position(row=5, col=5))  # חוסם למעלה-ימינה
        enemy = Piece(piece_id="b_pawn_1", color="black", kind="pawn", cell=Position(row=5, col=1))  # מטרה למעלה-שמאלה

        self.board.add_piece(bishop)
        self.board.add_piece(friend)
        self.board.add_piece(enemy)

        moves = get_bishop_destinations(self.board, bishop)

        # אלכסון למעלה-ימינה (חבר ב-5,5): מגיע רק ל-(4,4). המשבצות (5,5), (6,6), (7,7) חסומות
        self.assertIn(Position(row=4, col=4), moves)
        self.assertNotIn(Position(row=5, col=5), moves)

        # אלכסון למעלה-שמאלה (אויב ב-5,1): מגיע ל-(4,2) ולאכול ב-(5,1). המשבצת (6,0) חסומה
        self.assertIn(Position(row=4, col=2), moves)
        self.assertIn(Position(row=5, col=1), moves)
        self.assertNotIn(Position(row=6, col=0), moves)