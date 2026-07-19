import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position
from model.game_state import GameState
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from input.controller import GameController
from input.board_mapper import BoardMapper
from config import CELL_SIZE


def make_controller(*specs, w=8, h=8):
    """specs = (kind, color, row, col)"""
    board = Board(w, h)
    pieces = []
    for kind, color, row, col in specs:
        p = Piece(f"{color}_{kind}_{row}_{col}", color, kind, Position(row, col))
        board.add_piece(p)
        pieces.append(p)
    state = GameState(board)
    arbiter = RealTimeArbiter()
    engine = GameEngine(state, arbiter)
    mapper = BoardMapper(CELL_SIZE)
    ctrl = GameController(engine, mapper)
    return ctrl, engine, pieces


def px(row, col):
    """Center pixel of a cell."""
    return col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2


class TestGameController(unittest.TestCase):

    # --- first click selects ---
    def test_first_click_selects_piece(self):
        ctrl, eng, _ = make_controller(("rook", "white", 0, 0))
        x, y = px(0, 0)
        ctrl.handle_click(x, y)
        self.assertEqual(ctrl.selected_position, Position(0, 0))

    def test_click_empty_square_no_selection(self):
        ctrl, eng, _ = make_controller(("rook", "white", 0, 0))
        x, y = px(3, 3)
        ctrl.handle_click(x, y)
        self.assertIsNone(ctrl.selected_position)

    # --- double click = jump ---
    def test_double_click_same_piece_triggers_jump(self):
        ctrl, eng, [rook] = make_controller(("rook", "white", 0, 0))
        x, y = px(0, 0)
        ctrl.handle_click(x, y)   # select
        ctrl.handle_click(x, y)   # jump
        # piece removed from board (airborne)
        board = eng.get_snapshot().board
        self.assertIsNone(board.get_piece_at(Position(0, 0)))

    def test_double_click_clears_selection(self):
        ctrl, eng, _ = make_controller(("rook", "white", 0, 0))
        x, y = px(0, 0)
        ctrl.handle_click(x, y)
        ctrl.handle_click(x, y)
        self.assertIsNone(ctrl.selected_position)

    # --- move ---
    def test_click_move_starts_motion(self):
        ctrl, eng, [rook] = make_controller(("rook", "white", 0, 0))
        ctrl.handle_click(*px(0, 0))   # select
        ctrl.handle_click(*px(0, 3))   # move
        self.assertIsNone(ctrl.selected_position)

    # --- reselect friendly ---
    def test_click_friendly_switches_selection(self):
        ctrl, eng, _ = make_controller(("rook", "white", 0, 0), ("pawn", "white", 3, 3))
        ctrl.handle_click(*px(0, 0))   # select rook
        ctrl.handle_click(*px(3, 3))   # switch to pawn
        self.assertEqual(ctrl.selected_position, Position(3, 3))

    # --- out of bounds resets ---
    def test_click_out_of_bounds_clears_selection(self):
        ctrl, eng, _ = make_controller(("rook", "white", 0, 0))
        ctrl.handle_click(*px(0, 0))   # select
        ctrl.handle_click(-10, -10)    # out of bounds
        self.assertIsNone(ctrl.selected_position)


class TestBoardMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = BoardMapper(CELL_SIZE)

    def test_pixel_to_position(self):
        pos = self.mapper.to_board_position(150, 250)
        self.assertEqual(pos, Position(row=2, col=1))

    def test_top_left_origin(self):
        pos = self.mapper.to_board_position(0, 0)
        self.assertEqual(pos, Position(row=0, col=0))

    def test_position_to_pixel(self):
        x, y = self.mapper.to_pixel_coordinates(Position(2, 3))
        self.assertEqual(x, 3 * CELL_SIZE)
        self.assertEqual(y, 2 * CELL_SIZE)

    def test_roundtrip(self):
        original = Position(4, 5)
        x, y = self.mapper.to_pixel_coordinates(original)
        back = self.mapper.to_board_position(x, y)
        self.assertEqual(back, original)


if __name__ == "__main__":
    unittest.main()
