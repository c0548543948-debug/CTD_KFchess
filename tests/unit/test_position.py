import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.position import Position

class TestPosition(unittest.TestCase):

    def test_equality(self):
        self.assertEqual(Position(1, 2), Position(1, 2))
        self.assertNotEqual(Position(1, 2), Position(2, 1))

    def test_hashable(self):
        d = {Position(0, 0): "a", Position(1, 1): "b"}
        self.assertEqual(d[Position(0, 0)], "a")
        self.assertEqual(d[Position(1, 1)], "b")

    def test_usable_in_set(self):
        s = {Position(0, 0), Position(0, 0), Position(1, 1)}
        self.assertEqual(len(s), 2)

if __name__ == "__main__":
    unittest.main()
