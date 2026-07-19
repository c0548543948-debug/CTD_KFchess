import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position
from real_time.real_time_arbiter import RealTimeArbiter
from config import COOLDOWN_BY_KIND, STEP_DURATION_MS

def make_board(*specs):
    """specs = (kind, color, row, col) ..."""
    rows = [s[2] for s in specs]; cols = [s[3] for s in specs]
    h = max(rows) + 1 if rows else 4
    w = max(cols) + 1 if cols else 4
    board = Board(max(w, 4), max(h, 4))
    pieces = []
    for kind, color, row, col in specs:
        p = Piece(f"{color}_{kind}_{row}_{col}", color, kind, Position(row, col))
        board.add_piece(p)
        pieces.append(p)
    return board, pieces

class TestRealTimeArbiter(unittest.TestCase):

    def setUp(self):
        self.arb = RealTimeArbiter()

    # --- תנועה בסיסית ---
    def test_piece_arrives_at_target(self):
        board, [rook] = make_board(("rook", "white", 0, 0))
        self.arb.start_motion(board, Position(0, 0), Position(0, 2))
        self.arb.advance_time(2 * STEP_DURATION_MS, board)
        self.assertIsNone(board.get_piece_at(Position(0, 0)))
        self.assertEqual(board.get_piece_at(Position(0, 2)), rook)

    def test_piece_not_at_source_during_motion(self):
        board, [rook] = make_board(("rook", "white", 0, 0))
        self.arb.start_motion(board, Position(0, 0), Position(0, 3))
        # לפני הגעה — הלוח עדיין מראה אותו במקור
        self.assertIsNotNone(board.get_piece_at(Position(0, 0)))

    # --- צינון אחרי נחיתה ---
    def test_cooldown_set_after_arrival(self):
        board, [rook] = make_board(("rook", "white", 0, 0))
        self.arb.start_motion(board, Position(0, 0), Position(0, 1))
        self.arb.advance_time(STEP_DURATION_MS, board)
        p = board.get_piece_at(Position(0, 1))
        self.assertEqual(p.cooldown_remaining, COOLDOWN_BY_KIND["rook"])

    def test_cooldown_decreases_with_wait(self):
        board, [rook] = make_board(("rook", "white", 0, 0))
        self.arb.start_motion(board, Position(0, 0), Position(0, 1))
        self.arb.advance_time(STEP_DURATION_MS, board)        # נוחת, cooldown = 3000
        self.arb.advance_time(1000, board)                     # -1000
        p = board.get_piece_at(Position(0, 1))
        self.assertEqual(p.cooldown_remaining, COOLDOWN_BY_KIND["rook"] - 1000)

    # --- התנגשות אוויר-סטטי ---
    def test_captures_static_enemy(self):
        board, [wr, br] = make_board(("rook", "white", 0, 0), ("rook", "black", 0, 2))
        self.arb.start_motion(board, Position(0, 0), Position(0, 2))
        self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(0, 2)), wr)
        self.assertIsNone(board.get_piece_at(Position(0, 0)))

    def test_stops_before_friendly(self):
        board, [wr, wp] = make_board(("rook", "white", 0, 0), ("pawn", "white", 0, 2))
        self.arb.start_motion(board, Position(0, 0), Position(0, 3))
        self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(0, 1)), wr)
        self.assertEqual(board.get_piece_at(Position(0, 2)), wp)

    # --- התנגשות אוויר-אוויר ---
    def test_air_vs_air_earlier_wins_and_continues(self):
        board, [wr, br] = make_board(("rook", "white", 0, 0), ("rook", "black", 0, 3))
        self.arb.start_motion(board, Position(0, 0), Position(0, 3))  # wr ראשון
        self.arb.start_motion(board, Position(0, 3), Position(0, 0))  # br שני
        self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(0, 3)), wr)
        self.assertIsNone(board.get_piece_at(Position(0, 0)))

    def test_air_vs_air_later_loses(self):
        board, [wr, br] = make_board(("rook", "white", 0, 0), ("rook", "black", 0, 3))
        self.arb.start_motion(board, Position(0, 3), Position(0, 0))  # br ראשון
        self.arb.start_motion(board, Position(0, 0), Position(0, 3))  # wr שני
        self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(0, 0)), br)
        self.assertIsNone(board.get_piece_at(Position(0, 3)))

    # --- קפיצה הגנתית ---
    def test_jump_piece_airborne(self):
        board, [king] = make_board(("king", "white", 1, 1))
        self.arb.start_jump_motion(board, Position(1, 1))
        self.assertIsNone(board.get_piece_at(Position(1, 1)))

    def test_jump_returns_to_source_if_no_enemy(self):
        board, [king] = make_board(("king", "white", 1, 1))
        self.arb.start_jump_motion(board, Position(1, 1))
        self.arb.advance_time(STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(1, 1)), king)

    def test_jump_captures_arriving_enemy(self):
        board, [wk, br] = make_board(("king", "white", 1, 0), ("rook", "black", 1, 1))
        self.arb.start_jump_motion(board, Position(1, 0))          # wk קופץ
        self.arb.start_motion(board, Position(1, 1), Position(1, 0))  # br מגיע
        self.arb.advance_time(STEP_DURATION_MS, board)
        self.assertEqual(board.get_piece_at(Position(1, 0)), wk)
        self.assertIsNone(board.get_piece_at(Position(1, 1)))

    def test_enemy_captures_after_jump_lands(self):
        board, [wk, br] = make_board(("king", "white", 1, 0), ("rook", "black", 1, 3))
        self.arb.start_jump_motion(board, Position(1, 0))
        self.arb.advance_time(STEP_DURATION_MS, board)          # wk יורד
        self.assertEqual(board.get_piece_at(Position(1, 0)), wk)
        self.arb.start_motion(board, Position(1, 3), Position(1, 0))
        self.arb.advance_time(3 * STEP_DURATION_MS, board)     # br מגיע
        self.assertEqual(board.get_piece_at(Position(1, 0)), br)
        self.assertNotIn(wk, board._grid.values())

    # --- מלך נאכל ---
    def test_king_capture_returns_color(self):
        board, [wr, bk] = make_board(("rook", "white", 0, 0), ("king", "black", 0, 2))
        self.arb.start_motion(board, Position(0, 0), Position(0, 2))
        captured = self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertIn("black", captured)

    def test_white_king_capture_returns_white(self):
        board, [br, wk] = make_board(("rook", "black", 0, 0), ("king", "white", 0, 2))
        self.arb.start_motion(board, Position(0, 0), Position(0, 2))
        captured = self.arb.advance_time(3 * STEP_DURATION_MS, board)
        self.assertIn("white", captured)

if __name__ == "__main__":
    unittest.main()
