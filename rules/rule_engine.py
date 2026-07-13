from model.board import Board
from model.position import Position
from model.piece import Piece
from rules.movement_rules import MOVEMENT_RULES

def validate_motion(board: Board, src_position: Position, dest_position: Position) -> dict:
    # שלב 1: בדיקת גבולות הלוח תחילה (כדי למנוע קריסות בהמשך)
    if not board.is_in_bounds(src_position):
        return {"IS_VALID": False, "REASON": "Source cell is out of bounds"}
    if not board.is_in_bounds(dest_position):
        return {"IS_VALID": False, "REASON": "Destination cell is out of bounds"}

    # שלב 2: בדיקה שלא זזים מאותה משבצת לאותה משבצת
    if src_position == dest_position:
        return {"IS_VALID": False, "REASON": "Target cannot be the same as source"}

    # שלב 3: בדיקה שיש בכלל כלי בתא המקור
    piece_src = board.get_piece_at(src_position)
    if piece_src is None:
        return {"IS_VALID": False, "REASON": "Source cell is empty"}

    # שלב 4: בדיקת תא היעד (אם יש שם כלי, נוודא שהוא לא חבר לצוות)
    piece_dest = board.get_piece_at(dest_position)
    if piece_dest is not None:
        if piece_src.color == piece_dest.color:
            return {"IS_VALID": False, "REASON": "Cannot capture friendly piece"}

    # שלב 5: הפעלת מנוע החוקים הספציפי של החייל
    rule_function = MOVEMENT_RULES[piece_src.kind]
    legal_destinations = rule_function(board, piece_src) # מפעילים את הפונקציה

    if dest_position not in legal_destinations:
        return {"IS_VALID": False, "REASON": f"Invalid move for {piece_src.kind}"}

    # אם הכל עבר את הסינון - המהלך תקין לחלוטין!
    return {"IS_VALID": True, "REASON": "OK"}