import unittest
from model.position import Position
from model.piece import Piece
from model.motion import Motion


class TestMotion(unittest.TestCase):

    def test_straight_route_calculation(self):
        """בדיקה שצריח שמבצע תנועה ישרה מחשב נכון את כל משבצות הביניים"""
        # הוספנו piece_id="w_rook_1"
        rook = Piece(piece_id="w_rook_1", kind="rook", color="white", cell=Position(0, 0))
        target = Position(3, 0)

        motion = Motion(rook, target)

        expected_route = {
            Position(0, 0),
            Position(1, 0),
            Position(2, 0),
            Position(3, 0)
        }

        self.assertEqual(motion.route_cells, expected_route)

    def test_diagonal_route_calculation(self):
        """בדיקה שרץ שמבצע תנועה באלכסון מחשב נכון את כל משבצות הביניים"""
        # הוספנו piece_id="b_bishop_1"
        bishop = Piece(piece_id="b_bishop_1", kind="bishop", color="black", cell=Position(0, 2))
        target = Position(3, 5)

        motion = Motion(bishop, target)

        expected_route = {
            Position(0, 2),
            Position(1, 3),
            Position(2, 4),
            Position(3, 5)
        }

        self.assertEqual(motion.route_cells, expected_route)

    def test_knight_route_skips_intermediate_cells(self):
        """בדיקה שפרש מדלג ותופס רק את משבצת המקור ומשבצת היעד"""
        # הוספנו piece_id="w_knight_1"
        knight = Piece(piece_id="w_knight_1", kind="knight", color="white", cell=Position(0, 1))
        target = Position(2, 2)

        motion = Motion(knight, target)

        expected_route = {
            Position(0, 1),
            Position(2, 2)
        }

        self.assertEqual(motion.route_cells, expected_route)

    def test_advance_time_and_finish(self):
        """בדיקה שקידום הזמן מפחית את הזמן שנותר ומסיים את התנועה בדיוק בזמן"""
        # הוספנו piece_id="w_pawn_1"
        pawn = Piece(piece_id="w_pawn_1", kind="pawn", color="white", cell=Position(1, 1))
        target = Position(2, 1)

        motion = Motion(pawn, target, duration_ms=1000)

        self.assertFalse(motion.is_finished)
        self.assertEqual(motion.time_left, 1000)

        motion.advance_time(400)
        self.assertEqual(motion.time_left, 600)
        self.assertFalse(motion.is_finished)

        motion.advance_time(600)
        self.assertEqual(motion.time_left, 0)
        self.assertTrue(motion.is_finished)

    def test_advance_time_does_not_go_below_zero(self):
        """בדיקה שהזמן שנותר לעולם לא הופך למספר שלילי"""
        # הוספנו piece_id="w_pawn_2"
        pawn = Piece(piece_id="w_pawn_2", kind="pawn", color="white", cell=Position(1, 1))
        target = Position(2, 1)

        motion = Motion(pawn, target, duration_ms=500)

        motion.advance_time(600)
        self.assertEqual(motion.time_left, 0)
        self.assertTrue(motion.is_finished)