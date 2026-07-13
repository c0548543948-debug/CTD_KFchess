from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    # שדות (Attributes)
    row: int
    col: int

    # --- EQUATION (מנגנון השוואה מובנה של dataclass) ---
    # ה-dataclass מייצר אוטומטית השוואת ערכים (==) בין שני אובייקטים.

    # --- READABLE PRESENTATION (ייצוג קריא בסיסי) ---
    def __str__(self) -> str:
        """הצגה פשוטה של הערכים כטקסט"""
        return f"({self.row}, {self.col})"