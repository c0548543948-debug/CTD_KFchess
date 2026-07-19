import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.board import Board
from model.piece import Piece
from model.position import Position
from model.game_state import GameState


class TestGameState(unittest.TestCase):

    def _make_state(self):
        board = Board(4, 4)
        p = Piece("wk", "white", "king", Position(0, 0))
        board.add_piece(p)
        return GameState(board), p

    def test_initial_not_game_over(self):
        state, _ = self._make_state()
        self.assertFalse(state.game_over)

    def test_initial_winner_none(self):
        state, _ = self._make_state()
        self.assertIsNone(state.winner)

    def test_set_game_over(self):
        state, _ = self._make_state()
        state.game_over = True
        state.winner = "black"
        self.assertTrue(state.game_over)
        self.assertEqual(state.winner, "black")

    def test_clone_is_independent(self):
        state, p = self._make_state()
        clone = state.clone()
        clone.game_over = True
        clone.winner = "black"
        self.assertFalse(state.game_over)
        self.assertIsNone(state.winner)

    def test_clone_board_independent(self):
        state, p = self._make_state()
        clone = state.clone()
        # שינוי בלוח הקלון לא ישפיע על המקור
        p2 = Piece("br", "black", "rook", Position(3, 3))
        clone.board.add_piece(p2)
        self.assertIsNone(state.board.get_piece_at(Position(3, 3)))

    def test_clone_preserves_game_over(self):
        state, _ = self._make_state()
        state.game_over = True
        state.winner = "white"
        clone = state.clone()
        self.assertTrue(clone.game_over)
        self.assertEqual(clone.winner, "white")


if __name__ == "__main__":
    unittest.main()
