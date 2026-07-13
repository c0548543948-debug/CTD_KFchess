from model.position import Position

class RealTimeArbiter:
    def __init__(self):
        # זמני: נחזיק משתנה פשוט כדי שנוכל לבדוק תנועות פעילות בטסטים
        self._motion_in_progress = False

    def is_route_active(self, source: Position, target: Position) -> bool:
        """מחזיר האם יש כרגע תנועה פעילה על המסלול המשותף"""
        return self._motion_in_progress

    def start_motion(self, board, source: Position, target: Position) -> None:
        """מתחיל תנועה פיזית של כלי בזמן אמת"""
        pass

    def advance_time(self, ms: int) -> None:
        """מריץ את זמן הסימולציה קדימה במילישניות"""
        pass