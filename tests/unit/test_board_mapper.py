import unittest
from model.position import Position
from input.board_mapper import BoardMapper


class TestBoardMapper(unittest.TestCase):

    def setUp(self):
        # נבדוק את הממפה עם גודל משבצת סטנדרטי של 100 פיקסלים
        self.mapper = 100
        self.board_mapper = BoardMapper(cell_size=self.mapper)

    def test_pixel_to_board_position_corners_and_centers(self):
        """בדיקת המרה מפיקסלים למשבצת לוח בנקודות שונות בתוך התא"""
        # 1. לחיצה במרכז המשבצת (1, 1) -> פיקסלים (150, 150)
        pos_center = self.board_mapper.to_board_position(150, 150)
        self.assertEqual(pos_center, Position(row=1, col=1))

        # 2. לחיצה בפינה השמאלית העליונה הקיצונית של התא (0, 0) -> פיקסלים (0, 0)
        pos_top_left = self.board_mapper.to_board_position(0, 0)
        self.assertEqual(pos_top_left, Position(row=0, col=0))

        # 3. לחיצה בפינה הימנית התחתונה של התא (0, 0) -> פיקסלים (99, 99)
        pos_bottom_right = self.board_mapper.to_board_position(99, 99)
        self.assertEqual(pos_bottom_right, Position(row=0, col=0))

    def test_pixel_to_board_position_exact_boundaries(self):
        """בדיקה שלחיצות בדיוק על קווי הגבול של המשבצות עוברות לתא הבא"""
        # פיקסל 100 בדיוק צריך לקפוץ ישירות לעמודה/שורה 1 ולא להישאר ב-0
        pos_boundary = self.board_mapper.to_board_position(100, 100)
        self.assertEqual(pos_boundary, Position(row=1, col=1))

        # פיקסל 199 הוא עדיין עמודה 1, אבל פיקסל 200 הוא כבר עמודה 2
        self.assertEqual(self.board_mapper.to_board_position(199, 150), Position(row=1, col=1))
        self.assertEqual(self.board_mapper.to_board_position(200, 150), Position(row=1, col=2))

    def test_board_position_to_pixel_coordinates(self):
        """בדיקת המרה הפוכה ממשבצת לוח חזרה לקואורדינטות פיקסלים"""
        # המיקום (0, 0) צריך להחזיר את פיקסל ההתחלה שלו (0, 0)
        pixel_origin = self.board_mapper.to_pixel_coordinates(Position(row=0, col=0))
        self.assertEqual(pixel_origin, (0, 0))

        # המיקום (2, 3) צריך להיות בפיקסל X=300 (עמודה 3), Y=200 (שורה 2)
        pixel_pos = self.board_mapper.to_pixel_coordinates(Position(row=2, col=3))
        self.assertEqual(pixel_pos, (300, 200))

    def test_custom_cell_size(self):
        """ודאות שהממפה עובד בצורה תקינה גם אם נגדיר לו גודל משבצת שונה (למשל 80)"""
        custom_mapper = BoardMapper(cell_size=80)

        # בלוח של 80 פיקסלים למשבצת, פיקסל 120 ב-X צריך להיות עמודה 1 (120 // 80)
        # ופיקסל 200 ב-Y צריך להיות שורה 2 (200 // 80)
        pos = custom_mapper.to_board_position(120, 200)
        self.assertEqual(pos, Position(row=2, col=1))

        # המרה הפוכה עבור תא (2, 1) בגודל 80 פיקסלים -> X=80, Y=160
        pixels = custom_mapper.to_pixel_coordinates(Position(row=2, col=1))
        self.assertEqual(pixels, (80, 160))