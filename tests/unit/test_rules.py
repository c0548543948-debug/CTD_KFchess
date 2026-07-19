import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position
from rules.rule_engine import validate_motion


def make_board(w, h, *specs):
    """specs = (kind, color, row, col)"""
    board = Board(w, h)
    for kind, color, row, col in specs:
        p = Piece(f"{color}_{kind}", color, kind, Position(row, col))
        board.add_piece(p)
    return board


class TestRuleEngine(unittest.TestCase):

    # --- rook ---
    def test_rook_move_horizontal_valid(self):
        board = make_board(8, 8, ("rook", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(0, 5))
        self.assertTrue(res["IS_VALID"])

    def test_rook_move_vertical_valid(self):
        board = make_board(8, 8, ("rook", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(5, 0))
        self.assertTrue(res["IS_VALID"])

    def test_rook_move_diagonal_invalid(self):
        board = make_board(8, 8, ("rook", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(2, 2))
        self.assertFalse(res["IS_VALID"])

    # --- bishop ---
    def test_bishop_diagonal_valid(self):
        board = make_board(8, 8, ("bishop", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(3, 3))
        self.assertTrue(res["IS_VALID"])

    def test_bishop_horizontal_invalid(self):
        board = make_board(8, 8, ("bishop", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(0, 3))
        self.assertFalse(res["IS_VALID"])

    # --- queen ---
    def test_queen_horizontal_valid(self):
        board = make_board(8, 8, ("queen", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(4, 7))
        self.assertTrue(res["IS_VALID"])

    def test_queen_diagonal_valid(self):
        board = make_board(8, 8, ("queen", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(7, 7))
        self.assertTrue(res["IS_VALID"])

    # --- king ---
    def test_king_one_step_valid(self):
        board = make_board(8, 8, ("king", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(4, 5))
        self.assertTrue(res["IS_VALID"])

    def test_king_two_steps_invalid(self):
        board = make_board(8, 8, ("king", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(4, 6))
        self.assertFalse(res["IS_VALID"])

    # --- knight ---
    def test_knight_L_valid(self):
        board = make_board(8, 8, ("knight", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(2, 5))
        self.assertTrue(res["IS_VALID"])

    def test_knight_straight_invalid(self):
        board = make_board(8, 8, ("knight", "white", 4, 4))
        res = validate_motion(board, Position(4, 4), Position(4, 6))
        self.assertFalse(res["IS_VALID"])

    # --- pawn ---
    def test_pawn_forward_valid(self):
        board = make_board(8, 8, ("pawn", "white", 6, 4))
        res = validate_motion(board, Position(6, 4), Position(5, 4))
        self.assertTrue(res["IS_VALID"])

    # --- general edge cases ---
    def test_source_out_of_bounds(self):
        board = make_board(8, 8)
        res = validate_motion(board, Position(-1, 0), Position(0, 0))
        self.assertFalse(res["IS_VALID"])

    def test_target_out_of_bounds(self):
        board = make_board(8, 8, ("rook", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(0, 9))
        self.assertFalse(res["IS_VALID"])

    def test_no_piece_at_source(self):
        board = make_board(8, 8)
        res = validate_motion(board, Position(0, 0), Position(0, 3))
        self.assertFalse(res["IS_VALID"])

    def test_same_source_and_target(self):
        board = make_board(8, 8, ("rook", "white", 0, 0))
        res = validate_motion(board, Position(0, 0), Position(0, 0))
        self.assertFalse(res["IS_VALID"])

    def test_cannot_capture_friendly(self):
        board = make_board(8, 8, ("rook", "white", 0, 0), ("pawn", "white", 0, 3))
        res = validate_motion(board, Position(0, 0), Position(0, 3))
        self.assertFalse(res["IS_VALID"])

    def test_can_capture_enemy(self):
        board = make_board(8, 8, ("rook", "white", 0, 0), ("pawn", "black", 0, 3))
        res = validate_motion(board, Position(0, 0), Position(0, 3))
        self.assertTrue(res["IS_VALID"])


if __name__ == "__main__":
    unittest.main()
