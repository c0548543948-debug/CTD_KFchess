import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position

def piece(kind="rook", color="white", row=0, col=0):
    return Piece(f"{color}_{kind}_{row}_{col}", color, kind, Position(row, col))

class TestBoard(unittest.TestCase):

    def test_dimensions(self):
        b = Board(6, 3)
        self.assertEqual(b.width, 6)
        self.assertEqual(b.height, 3)

    def test_add_and_get_piece(self):
        b = Board(4, 4)
        p = piece()
        b.add_piece(p)
        self.assertEqual(b.get_piece_at(Position(0, 0)), p)

    def test_get_empty_returns_none(self):
        b = Board(4, 4)
        self.assertIsNone(b.get_piece_at(Position(0, 0)))

    def test_add_duplicate_raises(self):
        b = Board(4, 4)
        b.add_piece(piece())
        p2 = piece(color="black")
        with self.assertRaises(ValueError):
            b.add_piece(p2)

    def test_out_of_bounds_raises(self):
        b = Board(4, 4)
        with self.assertRaises(ValueError):
            b.get_piece_at(Position(5, 5))

    def test_remove_piece(self):
        b = Board(4, 4)
        b.add_piece(piece())
        b.remove_piece_at(Position(0, 0))
        self.assertIsNone(b.get_piece_at(Position(0, 0)))

    def test_remove_empty_returns_none(self):
        b = Board(4, 4)
        self.assertIsNone(b.remove_piece_at(Position(0, 0)))

    def test_is_in_bounds(self):
        b = Board(4, 4)
        self.assertTrue(b.is_in_bounds(Position(0, 0)))
        self.assertTrue(b.is_in_bounds(Position(3, 3)))
        self.assertFalse(b.is_in_bounds(Position(4, 0)))
        self.assertFalse(b.is_in_bounds(Position(0, 4)))
        self.assertFalse(b.is_in_bounds(Position(-1, 0)))

    def test_clone_is_deep(self):
        b = Board(4, 4)
        p = piece()
        b.add_piece(p)
        clone = b.clone()
        clone.remove_piece_at(Position(0, 0))
        self.assertIsNotNone(b.get_piece_at(Position(0, 0)))

    def test_clone_pieces_are_independent(self):
        b = Board(4, 4)
        p = piece()
        b.add_piece(p)
        clone = b.clone()
        clone.get_piece_at(Position(0, 0)).cooldown_remaining = 999
        self.assertEqual(b.get_piece_at(Position(0, 0)).cooldown_remaining, 0)

if __name__ == "__main__":
    unittest.main()
