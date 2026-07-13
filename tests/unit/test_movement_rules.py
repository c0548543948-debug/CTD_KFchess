import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.movement_rules import MOVEMENT_RULES


# 2. הוסיפי את המחלקה הזו ממש בסוף הקובץ:
class TestMovementRulesRegistry(unittest.TestCase):

    def test_all_chess_pieces_are_registered(self):
        """בדיקה שכל 6 סוגי הכלים קיימים במילון המרכזי ומחוברים לפונקציות אמיתיות"""
        expected_kinds = {"pawn", "rook", "bishop", "queen", "king", "knight"}

        # בודק שכל המפתחות הצפויים קיימים במילון
        self.assertEqual(set(MOVEMENT_RULES.keys()), expected_kinds)

        # בודק שכל הערכים הם אכן פונקציות הניתנות לזימון (callable) ולא None או זבל
        for kind, rule_function in MOVEMENT_RULES.items():
            self.assertTrue(callable(rule_function), f"Rule for {kind} is not a valid function!")