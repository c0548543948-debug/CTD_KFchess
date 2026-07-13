import unittest
from model.board import Board
from model.position import Position
from model.piece import Piece
from model.game_state import GameState
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine


class TestGameEngine(unittest.TestCase):

    def setUp(self):
        self.board = Board(width=8, height=8)
        self.state = GameState(self.board)
        self.arbiter = RealTimeArbiter()
        self.engine = GameEngine(self.state, self.arbiter)

    def test_reject_move_when_game_is_over(self):
        """בדיקה שהמנוע דוחה כל בקשה מיד אם המשחק הסתיים"""
        self.state.game_over = True

        res = self.engine.move_request(Position(row=1, col=3), Position(row=2, col=3))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "GAME OVER")

    def test_reject_move_when_motion_in_progress(self):
        """בדיקה שהמנוע חוסם מהלך אם הארביטר מדווח על תנועה פעילה במסלול"""
        # נדמה מצב שיש תנועה פעילה בארביטר
        self.arbiter._motion_in_progress = True

        res = self.engine.move_request(Position(row=1, col=3), Position(row=2, col=3))
        self.assertFalse(res["IS_ACCEPTED"])
        self.assertEqual(res["REASON"], "MOTION IN PROGRESS")

    def test_king_capture_triggers_game_over(self):
        """בדיקה שהודעה על אכילת מלך מעבירה את המשחק למצב סיום ומגדירה מנצח"""
        self.engine.notify_king_captured(loser_color="white")

        self.assertTrue(self.state.game_over)
        self.assertEqual(self.state.winner, "black")  # המפסיד לבן, לכן המנצח שחור

    def test_get_snapshot_returns_clone(self):
        """בדיקה שפונקציית הסנאפשוט מחזירה עותק נפרד לקריאה בלבד"""
        snapshot = self.engine.get_snapshot()
        self.assertFalse(snapshot.game_over)

        # נשנה את מצב המנוע המקורי
        self.state.game_over = True

        # נוודא שהסנאפשוט שיצא קודם נשאר קפוא ולא השתנה
        self.assertFalse(snapshot.game_over)