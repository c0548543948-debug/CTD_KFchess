import ChessPiece
class Queen(ChessPiece):
    def is_valid_move(self, target_position):
        # פייתון מאפשרת לעשות unpacking קצר וחמוד למיקומים
        current_row, current_col = self.position
        target_row, target_col = target_position