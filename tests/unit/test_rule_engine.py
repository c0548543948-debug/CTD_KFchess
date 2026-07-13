import unittest
from model.board import Board
from model.position import Position
from model.piece import Piece
from rules.rule_engine import validate_motion


class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)

    def test_source_out_of_bounds(self):
        """בדיקה שמיקום מקור מחוץ ללוח נפסל עם סיבה מתאימה"""
        res = validate_motion(self.board, Position(row=9, col=3), Position(row=3, col=3))
        self.assertFalse(res["IS_VALID"])
        self.assertEqual(res["REASON"], "Source cell is out of bounds")

    def test_target_same_as_source(self):
        """בדיקה שניסיון לזוז מאותה משבצת לאותה משבצת נפסל"""
        res = validate_motion(self.board, Position(row=3, col=3), Position(row=3, col=3))
        self.assertFalse(res["IS_VALID"])
        self.assertEqual(res["REASON"], "Target cannot be the same as source")

    def test_source_cell_is_empty(self):
        """בדיקה שניסיון להזיז תא ריק נפסל"""
        res = validate_motion(self.board, Position(row=3, col=3), Position(row=4, col=3))
        self.assertFalse(res["IS_VALID"])
        self.assertEqual(res["REASON"], "Source cell is empty")

    def test_cannot_capture_friendly_piece(self):
        """בדיקה שניסיון לנחות על כלי מאותו צבע נפסל"""
        pawn_src = Piece(piece_id="w_p_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        pawn_dest = Piece(piece_id="w_p_2", color="white", kind="pawn", cell=Position(row=2, col=3))

        self.board.add_piece(pawn_src)
        self.board.add_piece(pawn_dest)

        res = validate_motion(self.board, Position(row=1, col=3), Position(row=2, col=3))
        self.assertFalse(res["IS_VALID"])
        self.assertEqual(res["REASON"], "Cannot capture friendly piece")

    def test_invalid_move_for_piece_type(self):
        """בדיקה שמהלך שנוגד את חוקי החייל הספציפי נפסל (למשל רגלי שמנסה לזוז הצידה)"""
        pawn = Piece(piece_id="w_p_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        self.board.add_piece(pawn)

        # רגלי מנסה לזוז משבצת אחת ימינה (לא חוקי עבור רגלי)
        res = validate_motion(self.board, Position(row=1, col=3), Position(row=1, col=4))
        self.assertFalse(res["IS_VALID"])
        self.assertEqual(res["REASON"], "Invalid move for pawn")

    def test_valid_move_returns_ok(self):
        """בדיקה שמהלך חוקי לחלוטין מאושר ומחזיר OK"""
        pawn = Piece(piece_id="w_p_1", color="white", kind="pawn", cell=Position(row=1, col=3))
        self.board.add_piece(pawn)

        res = validate_motion(self.board, Position(row=1, col=3), Position(row=2, col=3))
        self.assertTrue(res["IS_VALID"])
        self.assertEqual(res["REASON"], "OK")


if __name__ == '__main__':
    unittest.main()