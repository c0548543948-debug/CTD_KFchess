import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.piece import Piece
from model.position import Position

class TestPiece(unittest.TestCase):

    def _make(self, kind="rook", color="white", row=0, col=0):
        return Piece(f"{color}_{kind}", color, kind, Position(row, col))

    def test_properties(self):
        p = self._make("king", "black", 2, 3)
        self.assertEqual(p.kind, "king")
        self.assertEqual(p.color, "black")
        self.assertEqual(p.cell, Position(2, 3))

    def test_initial_cooldown_zero(self):
        p = self._make()
        self.assertEqual(p.cooldown_remaining, 0)

    def test_clone_is_independent(self):
        p = self._make()
        p.cooldown_remaining = 500
        clone = p.clone()
        clone.cooldown_remaining = 999
        self.assertEqual(p.cooldown_remaining, 500)

    def test_clone_same_values(self):
        p = self._make("queen", "white", 1, 2)
        p.cooldown_remaining = 1500
        clone = p.clone()
        self.assertEqual(clone.kind, "queen")
        self.assertEqual(clone.color, "white")
        self.assertEqual(clone.cell, Position(1, 2))
        self.assertEqual(clone.cooldown_remaining, 1500)

    def test_equality_by_id(self):
        p1 = Piece("id1", "white", "rook", Position(0, 0))
        p2 = Piece("id1", "black", "king", Position(1, 1))
        p3 = Piece("id2", "white", "rook", Position(0, 0))
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)

if __name__ == "__main__":
    unittest.main()
