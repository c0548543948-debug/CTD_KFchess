from abc import ABC, abstractmethod


# שם קלאס ב-PascalCase
class ChessPiece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position  # משתנה (פרופרטי) ב-snake_case

    @abstractmethod
    def is_valid_move(self, target_position):  # שם מתודה ב-snake_case
        pass


