import unittest
# ייבוא המחלקה שיצרנו
from model.position import Position


class TestPosition(unittest.TestCase):

    # ==========================================
    # 1. בדיקות השוואה מכל הסוגים (Equation)
    # ==========================================

    def test_equality_between_identical_objects(self):
        """בדיקה ששני אובייקטים עם אותם ערכים נחשבים שווים"""
        pos1 = Position(row=3, col=4)
        pos2 = Position(row=3, col=4)
        self.assertEqual(pos1, pos2)

    def test_inequality_between_different_rows(self):
        """בדיקה ששינוי בשורה מייצר אובייקט שונה"""
        pos1 = Position(row=3, col=4)
        pos2 = Position(row=5, col=4)
        self.assertNotEqual(pos1, pos2)

    def test_inequality_between_different_cols(self):
        """בדיקה ששינוי בעמודה מייצר אובייקט שונה"""
        pos1 = Position(row=3, col=4)
        pos2 = Position(row=3, col=1)
        self.assertNotEqual(pos1, pos2)

    def test_inequality_with_different_types(self):
        """בדיקה שאובייקט מיקום אינו שווה לטיפוסים אחרים (למשל מחרוזת או מספר)"""
        pos = Position(row=3, col=4)
        self.assertNotEqual(pos, "Position(3, 4)")
        self.assertNotEqual(pos, [3, 4])

    # ==========================================
    # 2. בדיקת ייצוג השגיאה (Readable Assertion Failures)
    # ==========================================

    def test_readable_assertion_failure_format(self):
        """
        בדיקה שמוודאת כי הייצוג הרשמי של האובייקט (repr)
        מייצר את המחרוזת המדויקת שפייתון מציג בזמן כישלון בטסטים
        """
        pos = Position(row=3, col=4)

        # הציפייה היא שהודעת השגיאה תכיל את שם המחלקה והערכים בצורה מפורשת
        expected_format = "Position(row=3, col=4)"

        self.assertEqual(repr(pos), expected_format)


if __name__ == '__main__':
    unittest.main()