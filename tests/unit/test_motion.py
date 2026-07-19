import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.motion import Motion
from model.piece import Piece
from model.position import Position
from config import STEP_DURATION_MS

def make_piece(kind="rook", color="white", row=0, col=0):
    return Piece(f"{color}_{kind}_{row}_{col}", color, kind, Position(row, col))

class TestMotion(unittest.TestCase):

    def test_steps_straight(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        self.assertEqual(len(m.steps), 4)
        self.assertEqual(m.steps[0], Position(0, 0))
        self.assertEqual(m.steps[-1], Position(0, 3))

    def test_total_duration(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        self.assertEqual(m.total_duration_ms, 3 * STEP_DURATION_MS)

    def test_not_finished_at_start(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        self.assertFalse(m.is_finished)

    def test_finished_after_full_time(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 1))
        m.advance_time(STEP_DURATION_MS)
        self.assertTrue(m.is_finished)

    def test_current_position_advances(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        m.advance_time(STEP_DURATION_MS)
        self.assertEqual(m.get_current_physical_position(), Position(0, 1))

    def test_next_position(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        self.assertEqual(m.get_next_physical_position(), Position(0, 1))

    def test_next_position_none_when_finished(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 1))
        m.advance_time(STEP_DURATION_MS)
        self.assertIsNone(m.get_next_physical_position())

    def test_force_stop(self):
        p = make_piece(row=0, col=0)
        m = Motion(p, Position(0, 3))
        m.advance_time(STEP_DURATION_MS)
        m.force_stop_at_step(1)
        self.assertTrue(m.is_finished)
        self.assertEqual(m.target, Position(0, 1))

    def test_knight_jumps_directly(self):
        p = make_piece(kind="knight", row=0, col=0)
        m = Motion(p, Position(2, 1))
        self.assertEqual(len(m.steps), 2)
        self.assertEqual(m.steps[0], Position(0, 0))
        self.assertEqual(m.steps[1], Position(2, 1))

    # --- קפיצה הגנתית ---
    def test_jump_source_equals_target(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        self.assertEqual(m.source, m.target)
        self.assertEqual(len(m.steps), 1)

    def test_jump_duration_equals_one_step(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        self.assertEqual(m.total_duration_ms, STEP_DURATION_MS)

    def test_jump_not_finished_before_duration(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        m.advance_time(STEP_DURATION_MS - 100)
        self.assertFalse(m.is_finished)

    def test_jump_finished_after_duration(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        m.advance_time(STEP_DURATION_MS)
        self.assertTrue(m.is_finished)

    def test_jump_current_position_stays_at_source(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        m.advance_time(500)
        self.assertEqual(m.get_current_physical_position(), Position(1, 1))

    def test_jump_no_next_position(self):
        p = make_piece(row=1, col=1)
        m = Motion(p, Position(1, 1), is_jump=True)
        self.assertIsNone(m.get_next_physical_position())

if __name__ == "__main__":
    unittest.main()
