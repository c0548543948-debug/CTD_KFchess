import unittest
from unittest.mock import MagicMock
from model.position import Position
from model.piece import Piece
from model.board import Board
from input.board_mapper import BoardMapper
from input.controller import GameController


class TestGameController(unittest.TestCase):

    def setUp(self):
        # 1. ניצור מנוע משחק מדומה (Mock) כדי לעקוב אחרי הקריאות אליו
        self.mock_engine = MagicMock()

        # 2. ניצור לוח אמיתי פשוט (8x8) ונלביש אותו על סנאפשוט מדומה של המנוע
        self.board = Board(width=8, height=8)
        self.mock_snapshot = MagicMock()
        self.mock_snapshot.board = self.board
        self.mock_engine.get_snapshot.return_value = self.mock_snapshot

        # 3. נאתחל את ה-Mapper וה-Controller עם גודל משבצת של 100 פיקסלים
        self.mapper = BoardMapper(cell_size=100)
        self.controller = GameController(self.mock_engine, self.mapper)

    def test_first_click_on_empty_cell_is_ignored(self):
        """חוק 9: התעלמות מלחיצה ראשונה על תא ריק"""
        # לחיצה על (150, 150) שמתורגמת לתא (1, 1) שהוא ריק
        self.controller.handle_click(150, 150)

        self.assertIsNone(self.controller.selected_position)
        self.mock_engine.move_request.assert_not_called()

    def test_first_click_on_piece_selects_it(self):
        """חוק 4: לחיצה ראשונה על תא עם כלי מסמנת אותו"""
        # נניח חייל לבן במשבצת (1, 1)
        pawn = Piece(piece_id="w_pawn_1", kind="pawn", color="white", cell=Position(1, 1))
        self.board.add_piece(pawn)

        # לחיצה בפיקסלים של משבצת (1, 1)
        self.controller.handle_click(150, 150)

        # נוודא שהבקר מסמן את המיקום הנכון
        self.assertEqual(self.controller.selected_position, Position(1, 1))
        self.mock_engine.move_request.assert_not_called()

    def test_second_click_inside_board_sends_command_and_clears_selection(self):
        """חוק 5 ו-6: לחיצה שנייה בתוך הלוח שולחת פקודה ומנקה את הסימון מיידית"""
        # נניח חייל ב-(1, 1) ונסמן אותו בלחיצה ראשונה
        pawn = Piece(piece_id="w_pawn_1", kind="pawn", color="white", cell=Position(1, 1))
        self.board.add_piece(pawn)
        self.controller.handle_click(150, 150)  # לחיצה ראשונה

        # לחיצה שנייה ליעד (250, 150) שמתורגמת ל-(1, 2)
        self.controller.handle_click(250, 150)  # לחיצה שנייה

        # 1. המנוע היה צריך לקבל בקשת תנועה מהמקור ליעד
        self.mock_engine.move_request.assert_called_once_with(Position(1, 1), Position(1, 2))
        # 2. הסימון חייב להתנקות
        self.assertIsNone(self.controller.selected_position)

    def test_click_outside_board_ignored_when_no_selection(self):
        """חוק 7: אם אין כלי מסומן, מתעלמים לחלוטין מלחיצות מחוץ ללוח"""
        # לחיצה במיקום (950, 150) - מחוץ לגבולות הלוח (עמודה 9)
        self.controller.handle_click(950, 150)

        self.assertIsNone(self.controller.selected_position)
        self.mock_engine.move_request.assert_not_called()

    def test_click_outside_board_cancels_selection_when_piece_is_selected(self):
        """חוק 8: אם יש כלי מסומן, לחיצה מחוץ ללוח מבטלת את הסימון ולא שולחת פקודה"""
        # נשים כלי ב-(1, 1) ונסמן אותו
        pawn = Piece(piece_id="w_pawn_1", kind="pawn", color="white", cell=Position(1, 1))
        self.board.add_piece(pawn)
        self.controller.handle_click(150, 150)

        # נלחץ מחוץ ללוח ב- (850, 150) - עמודה 8 (מחוץ ללוח ברוחב 8)
        self.controller.handle_click(850, 150)

        # הסימון צריך להתבטל
        self.assertIsNone(self.controller.selected_position)
        # שום פקודה לא נשלחה למנוע
        self.mock_engine.move_request.assert_not_called()

    def test_pixel_to_cell_mapping_edge_cases(self):
        """בדיקת גבולות תרגום הפיקסלים על ידי ה-BoardMapper"""
        # פיקסל 0 ו-99 צריכים להתמפות לאינדקס 0
        pos_min = self.mapper.to_board_position(0, 99)
        self.assertEqual(pos_min, Position(row=0, col=0))

        # פיקסל 100 צריך להתמפות לאינדקס 1
        pos_edge = self.mapper.to_board_position(100, 100)
        self.assertEqual(pos_edge, Position(row=1, col=1))