import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position
from model.game_state import GameState
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from config import STEP_DURATION_MS, COOLDOWN_BY_KIND


def make_engine(*specs, w=8, h=8):
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
    return engine, pieces


class TestGameEngine(unittest.TestCase):

    # --- move_request ---
    def test_move_accepted(self):
        eng, [rook] = make_engine(("rook", "white", 0, 0))
        res = eng.move_request(Position(0, 0), Position(0, 3))
        self.assertTrue(res["IS_ACCEPTED"])

    def test_move_rejected_game_over(self):
        eng, _ = make_engine(("rook", "white", 0, 0))
        eng._state.game_over = True
        res = eng.move_request(Position(0, 0), Position(0, 3))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "GAME OVER")

    def test_move_rejected_cooldown(self):
        eng, [rook] = make_engine(("rook", "white", 0, 0))
        rook.cooldown_remaining = 500
        res = eng.move_request(Position(0, 0), Position(0, 3))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "PIECE IN COOLDOWN")

    def test_move_rejected_invalid_rule(self):
        eng, _ = make_engine(("rook", "white", 0, 0))
        res = eng.move_request(Position(0, 0), Position(1, 1))
        self.assertFalse(res["IS_ACCEPTED"])

    # --- jump_request ---
    def test_jump_accepted(self):
        eng, _ = make_engine(("king", "white", 1, 1))
        res = eng.jump_request(Position(1, 1))
        self.assertTrue(res["IS_ACCEPTED"])

    def test_jump_rejected_no_piece(self):
        eng, _ = make_engine(("king", "white", 1, 1))
        res = eng.jump_request(Position(3, 3))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "NO PIECE")

    def test_jump_rejected_game_over(self):
        eng, _ = make_engine(("king", "white", 1, 1))
        eng._state.game_over = True
        res = eng.jump_request(Position(1, 1))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "GAME OVER")

    def test_jump_rejected_cooldown(self):
        eng, [king] = make_engine(("king", "white", 1, 1))
        king.cooldown_remaining = 1000
        res = eng.jump_request(Position(1, 1))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "PIECE IN COOLDOWN")

    def test_jump_rejected_already_moving(self):
        # Use a rook (can move 3 squares) so move_request is actually accepted
        eng, _ = make_engine(("rook", "white", 0, 0))
        move_res = eng.move_request(Position(0, 0), Position(0, 3))
        self.assertTrue(move_res["IS_ACCEPTED"], "Precondition: move must be accepted")
        res = eng.jump_request(Position(0, 0))
        self.assertFalse(res["IS_ACCEPTED"])

    # --- wait + game over ---
    def test_wait_triggers_game_over_on_king_capture(self):
        eng, _ = make_engine(("rook", "white", 0, 0), ("king", "black", 0, 3))
        eng.move_request(Position(0, 0), Position(0, 3))
        eng.wait(3 * STEP_DURATION_MS + 1)
        self.assertTrue(eng._state.game_over)
        self.assertEqual(eng._state.winner, "white")

    def test_wait_sets_white_winner_when_black_king_captured(self):
        eng, _ = make_engine(("rook", "white", 0, 0), ("king", "black", 0, 2))
        eng.move_request(Position(0, 0), Position(0, 2))
        eng.wait(3 * STEP_DURATION_MS)
        self.assertEqual(eng._state.winner, "white")

    # --- get_snapshot isolates state ---
    def test_snapshot_does_not_share_board(self):
        eng, [rook] = make_engine(("rook", "white", 0, 0))
        snap = eng.get_snapshot()
        p2 = Piece("new", "black", "pawn", Position(7, 7))
        snap.board.add_piece(p2)
        self.assertIsNone(eng._state.board.get_piece_at(Position(7, 7)))


if __name__ == "__main__":
    unittest.main()
