from model.game_state import GameState
from model.position import Position
from real_time.real_time_arbiter import RealTimeArbiter
from rules.rule_engine import validate_motion
from rules.movement_rules import MOVEMENT_RULES

class GameEngine:
    def __init__(self, game_state: GameState, arbiter: RealTimeArbiter):
        self._state = game_state
        self._arbiter = arbiter

    def get_snapshot(self) -> GameState:
        return self._state.clone()

    def move_request(self, source: Position, target: Position) -> dict:
        if self._state.game_over:
            return {"IS_ACCEPTED": False, "REASON": "GAME OVER"}
        piece = self._state.board.get_piece_at(source)
        if piece and piece.cooldown_remaining > 0:
            return {"IS_ACCEPTED": False, "REASON": "PIECE IN COOLDOWN"}
        if self._arbiter.is_route_active(self._state.board, source, target):
            return {"IS_ACCEPTED": False, "REASON": "MOTION IN PROGRESS"}
        result = validate_motion(self._state.board, source, target)
        if not result["IS_VALID"]:
            return {"IS_ACCEPTED": False, "REASON": result["REASON"]}
        self._arbiter.start_motion(self._state.board, source, target)
        return {"IS_ACCEPTED": True, "REASON": "OK"}

    def jump_request(self, source: Position) -> dict:
        """הכלי קופץ מעל הריבוע שלו — אין יעד."""
        if self._state.game_over:
            return {"IS_ACCEPTED": False, "REASON": "GAME OVER"}
        piece = self._state.board.get_piece_at(source)
        if piece is None:
            return {"IS_ACCEPTED": False, "REASON": "NO PIECE"}
        if piece.cooldown_remaining > 0:
            return {"IS_ACCEPTED": False, "REASON": "PIECE IN COOLDOWN"}
        if self._arbiter.is_piece_moving(piece):
            return {"IS_ACCEPTED": False, "REASON": "MOTION IN PROGRESS"}
        self._arbiter.start_jump_motion(self._state.board, source)
        return {"IS_ACCEPTED": True, "REASON": "OK"}

    def wait(self, ms: int) -> None:
        captured_kings = self._arbiter.advance_time(ms, self._state.board)
        for color in captured_kings:
            self.notify_king_captured(color)

    def notify_king_captured(self, loser_color: str) -> None:
        self._state.game_over = True
        self._state.winner = "black" if loser_color == "white" else "white"

    def get_valid_moves(self, source: Position) -> list:
        """
        מחזיר רשימת Position-ים שהכלי ב-source יכול לנוע אליהם.
        משתמש ישירות ב-MOVEMENT_RULES כך שלא צריך לעבור על כל הלוח.
        מחזיר רשימה ריקה אם אין כלי, הכלי בcooldown, או אין חוק.
        """
        piece = self._state.board.get_piece_at(source)
        if piece is None:
            return []
        if piece.cooldown_remaining > 0:
            return []
        rule_fn = MOVEMENT_RULES.get(piece.kind)
        if rule_fn is None:
            return []
        return rule_fn(self._state.board, piece)

    def get_active_motion_states(self) -> list[dict]:
        """
        מעביר את מידע התנועות הפעילות מהארביטר לשכבת ה-View.
        הרנדרר יקרא לפונקציה הזו כדי לדעת איפה לצייר כלים שזזים עכשיו.
        """
        return self._arbiter.get_active_motion_states()
