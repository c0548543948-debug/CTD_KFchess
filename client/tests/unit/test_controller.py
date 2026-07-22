import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from engine.model.position import Position
from engine.model.piece import Piece
from client.input.controller import GameController


def make_piece(kind="rook", color="white", row=0, col=0):
    return Piece(f"{color}_{kind}_{row}_{col}", color, kind, Position(row, col))


class FakeWSClient:
    """מחליף את WSClient האמיתי — שומר את המסר האחרון שנשלח"""
    def __init__(self):
        self.last_sent = None

    def send(self, msg):
        self.last_sent = msg


class FakeBoardMapper:
    def to_board_position(self, x, y):
        return Position(x, y)


class FakeSnapshot:
    def __init__(self, board):
        self.board = board


class TestControllerBuilders(unittest.TestCase):

    def setUp(self):
        self.ws = FakeWSClient()
        self.mapper = FakeBoardMapper()
        self.controller = GameController(
            ws_client=self.ws,
            board_mapper=self.mapper,
            get_snapshot=lambda: None
        )

    def test_pos_to_str_col_and_row(self):
        pos = Position(row=5, col=4)
        result = self.controller._pos_to_str(pos)
        self.assertEqual(result, "e6")

    def test_pos_to_str_origin(self):
        pos = Position(row=0, col=0)
        result = self.controller._pos_to_str(pos)
        self.assertEqual(result, "a1")

    def test_build_move_white_queen(self):
        piece = make_piece(kind="queen", color="white")
        result = self.controller._build_move(piece, Position(1, 4), Position(4, 4))
        self.assertEqual(result, "WQe2e5")

    def test_build_jump_black_rook(self):
        piece = make_piece(kind="rook", color="black")
        result = self.controller._build_jump(piece, Position(0, 0))
        self.assertEqual(result, "BRa1")


if __name__ == "__main__":
    unittest.main()