import unittest
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from model.position import Position
from io_utils.board_parser import BoardParser, BoardPrinter


SIMPLE_BOARD = """\
wR . .
.  . .
.  . bK
"""


class TestBoardParser(unittest.TestCase):

    def test_parse_dimensions(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        self.assertEqual(board.width, 3)
        self.assertEqual(board.height, 3)

    def test_parse_white_rook(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        p = board.get_piece_at(Position(0, 0))
        self.assertIsNotNone(p)
        self.assertEqual(p.color, "white")
        self.assertEqual(p.kind, "rook")

    def test_parse_black_king(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        p = board.get_piece_at(Position(2, 2))
        self.assertIsNotNone(p)
        self.assertEqual(p.color, "black")
        self.assertEqual(p.kind, "king")

    def test_parse_empty_square(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        self.assertIsNone(board.get_piece_at(Position(0, 1)))

    def test_parse_raises_on_unknown_token(self):
        bad = "xZ . .\n.  . .\n.  . ."
        with self.assertRaises(ValueError):
            BoardParser.parse(bad)

    def test_parse_raises_on_row_width_mismatch(self):
        bad = "wR .\n. . .\n."
        with self.assertRaises(ValueError):
            BoardParser.parse(bad)

    def test_parse_empty_string_raises(self):
        with self.assertRaises(ValueError):
            BoardParser.parse("   \n  ")

    def test_all_piece_kinds(self):
        board_str = "wK wQ wR wB wN wP"
        board = BoardParser.parse(board_str)
        kinds = [board.get_piece_at(Position(0, c)).kind for c in range(6)]
        self.assertEqual(kinds, ["king", "queen", "rook", "bishop", "knight", "pawn"])


class TestBoardPrinter(unittest.TestCase):

    def test_print_matches_parse(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        printed = BoardPrinter.print_board(board)
        board2 = BoardParser.parse(printed)
        p1 = board.get_piece_at(Position(0, 0))
        p2 = board2.get_piece_at(Position(0, 0))
        self.assertEqual(p1.kind, p2.kind)
        self.assertEqual(p1.color, p2.color)

    def test_empty_square_printed_as_dot(self):
        board = BoardParser.parse(SIMPLE_BOARD)
        printed = BoardPrinter.print_board(board)
        self.assertIn(".", printed)

    def test_rook_printed_as_wR(self):
        board = BoardParser.parse("wR")
        printed = BoardPrinter.print_board(board)
        self.assertEqual(printed.strip(), "wR")

    def test_king_printed_as_bK(self):
        board = BoardParser.parse("bK")
        printed = BoardPrinter.print_board(board)
        self.assertEqual(printed.strip(), "bK")


if __name__ == "__main__":
    unittest.main()
