import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from engine.model.position import Position
from client.input.controller import GameController


class FakeWSClient:
    def __init__(self):
        self.last_sent = None

    def send(self, msg):
        self.last_sent = msg


class FakeBoardMapper:
    def to_board_position(self, x, y):
        return Position(x, y)


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

    def test_build_move(self):
        result = self.controller._build_move(Position(1, 4), Position(4, 4))
        self.assertEqual(result, "e2e5")

    def test_build_jump(self):
        result = self.controller._build_jump(Position(0, 0))
        self.assertEqual(result, "a1")


if __name__ == "__main__":
    unittest.main()