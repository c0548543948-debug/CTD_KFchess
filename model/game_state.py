from model.board import Board

class GameState:
    def __init__(self, board: Board):
        self.board: Board = board
        self.game_over: bool = False
        self.winner: str | None = None  # יכול להיות "white", "black" או None

    def clone(self):
        """מייצר עותק נפרד של המצב (Snapshot) כדי לחשוף למסך באופן בטוח"""
        # בשלב זה נעשה שינוי פשוט, בהמשך אם נצטרך נעמיק את השכפול
        new_state = GameState(self.board) # כאן ה-board משותף, או משוכפל בהתאם לצורך
        new_state.game_over = self.game_over
        new_state.winner = self.winner
        return new_state