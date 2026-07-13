from rules.pawn_rules import get_pawn_destinations
from rules.rook_rules import get_rook_destinations
from rules.bishop_rules import get_bishop_destinations
from rules.queen_rules import get_queen_destinations
from rules.king_rules import get_king_destinations
from rules.knight_rules import get_knight_destinations

# מילון מרכזי שממפה בין מחרוזת של סוג הכלי (piece.kind) לבין הפונקציה המתאימה לו
MOVEMENT_RULES = {
    "pawn": get_pawn_destinations,
    "rook": get_rook_destinations,
    "bishop": get_bishop_destinations,
    "queen": get_queen_destinations,
    "king": get_king_destinations,
    "knight": get_knight_destinations
}