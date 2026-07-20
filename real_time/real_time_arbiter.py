from __future__ import annotations
from model.position import Position
from model.board import Board
from model.motion import Motion
from config import COOLDOWN_BY_KIND, DEFAULT_COOLDOWN

class RealTimeArbiter:
    def __init__(self):
        self._active_motions: list[Motion] = []

    def is_piece_moving(self, piece) -> bool:
        return any(m.piece == piece and not m.is_finished for m in self._active_motions)

    def _piece_has_any_motion(self, piece) -> bool:
        """
        בודקת אם לכלי יש תנועה ב-_active_motions — גם אם היא כבר הסתיימה (is_finished=True).

        למה זה שונה מ-is_piece_moving?
        בתוך אותו tick, ייתכן שגם המלך וגם התוקף מסיימים את התנועה שלהם.
        is_piece_moving מחזיר False למלך (כי is_finished=True),
        ואז התוקף "תופס" את המלך גם שהוא בעצם ברח באותה שנייה.
        הפונקציה הזו מחזירה True גם לתנועות שסיימו אבל טרם הוסרו מהרשימה,
        כך שהמלך נחשב כ"ברח" עד שה-_handle_arrival שלו מסיים לעבד אותו.
        """
        return any(m.piece == piece for m in self._active_motions)

    def is_route_active(self, board: Board, source: Position, target: Position) -> bool:
        piece = board.get_piece_at(source)
        if not piece:
            return False
        return self.is_piece_moving(piece)

    def start_motion(self, board: Board, source: Position, target: Position) -> None:
        piece = board.get_piece_at(source)
        if not piece:
            return
        self._active_motions.append(Motion(piece, target, is_jump=False))

    def start_jump_motion(self, board: Board, source: Position) -> None:
        """הכלי קופץ למעלה מעל הריבוע שלו — source == target, משך STEP_DURATION_MS."""
        piece = board.get_piece_at(source)
        if not piece:
            return
        board.remove_piece_at(source)
        self._active_motions.append(Motion(piece, source, is_jump=True))

    def advance_time(self, ms: int, board: Board) -> list[str]:
        """מחזירה רשימת צבעי מלכים שנאכלו."""
        captured_kings: list[str] = []
        remaining_ms = ms

        for pos in list(board._grid.keys()):
            piece = board.get_piece_at(pos)
            if piece and piece.cooldown_remaining > 0:
                piece.cooldown_remaining = max(0, piece.cooldown_remaining - ms)

        tick_size = 100
        while remaining_ms > 0:
            current_tick = min(tick_size, remaining_ms)
            remaining_ms -= current_tick

            for motion in self._active_motions:
                if not motion.is_finished:
                    motion.advance_time(current_tick)

            self._resolve_collisions(board, captured_kings)

            for motion in list(self._active_motions):
                if motion.is_finished:
                    self._handle_arrival(motion, board, captured_kings)
                    if motion in self._active_motions:
                        self._active_motions.remove(motion)

        return captured_kings

    def _resolve_collisions(self, board: Board, captured_kings: list[str]) -> None:
        motions_to_remove = set()
        motions_to_arrive_instantly = set()

        for motion in self._active_motions:
            if motion in motions_to_remove or motion in motions_to_arrive_instantly or motion.is_finished:
                continue

            next_pos = motion.get_next_physical_position()
            if not next_pos:
                continue  # כלים קופצים (is_jump, 0 צעדים) — רק מגיבים, לא יוזמים

            jump_captor = None
            air_enemy = None
            air_friend = None

            for other in self._active_motions:
                if (other == motion or other.is_finished
                        or other in motions_to_remove or other in motions_to_arrive_instantly):
                    continue

                # כלי "באוויר" ב-next_pos רק אם הוא עבר לפחות צעד אחד מהמקור שלו.
                # אם הוא בצעד 0 (עדיין על הלוח במקורו), לא מדובר בהתנגשות אווירית —
                # הוא יטופל ע"י הבדיקה הסטטית למטה.
                other_in_air_at_next = (
                    other.get_current_physical_position() == next_pos
                    and other.get_current_physical_step_idx() > 0
                )
                hits = other_in_air_at_next or other.get_next_physical_position() == next_pos
                if not hits:
                    continue

                idx_self = self._active_motions.index(motion)
                idx_other = self._active_motions.index(other)

                if other.piece.color == motion.piece.color:
                    if idx_self > idx_other:
                        air_friend = other
                    break
                else:
                    if other.is_jump:
                        jump_captor = other  # כלי קופץ תופס את motion
                        break
                    elif idx_self < idx_other:
                        air_enemy = other  # motion מנצח, other מפסיד
                        break

            if jump_captor:
                board.remove_piece_at(motion.source)
                if motion.piece.kind == "king":
                    captured_kings.append(motion.piece.color)
                motions_to_remove.add(motion)
                motions_to_arrive_instantly.add(jump_captor)
                continue

            if air_friend:
                motion.force_stop_at_step(motion.get_current_physical_step_idx())
                motions_to_arrive_instantly.add(motion)
                continue

            if air_enemy:
                board.remove_piece_at(air_enemy.source)
                if air_enemy.piece.kind == "king":
                    captured_kings.append(air_enemy.piece.color)
                motions_to_remove.add(air_enemy)
                continue

            static = board.get_piece_at(next_pos)
            if not static:
                continue

            # אם הכלי שנמצא ב-next_pos בעצם זזה כרגע —
            # הוא לא "סטטי" אמיתי, הוא עוזב את המשבצת הזו.
            # מתעלמים ממנו כאן; _handle_arrival יטפל בזה כשA יגיע.
            if self.is_piece_moving(static):
                continue

            idx = motion.get_current_physical_step_idx()
            if static.color == motion.piece.color:
                motion.force_stop_at_step(idx)
            else:
                board.remove_piece_at(next_pos)
                if static.kind == "king":
                    captured_kings.append(static.color)
                motion.force_stop_at_step(idx + 1)
            motions_to_arrive_instantly.add(motion)

        for m in motions_to_arrive_instantly:
            self._handle_arrival(m, board, captured_kings)
            if m in self._active_motions:
                self._active_motions.remove(m)

        for m in motions_to_remove:
            if m in self._active_motions:
                self._active_motions.remove(m)

    def get_active_motion_states(self) -> list[dict]:
        """
        מחזיר רשימה של dict אחד לכל תנועה פעילה שלא הסתיימה.
        כל dict מכיל:
          "piece"   - אובייקט הכלי שזזה
          "row"     - מיקום שורה עשרוני (0.0 עד 7.0) בנקודת הזמן הנוכחית
          "col"     - מיקום עמודה עשרוני
          "is_jump" - האם זו קפיצה הגנתית (True) או הליכה רגילה (False)
        """
        result = []
        for motion in self._active_motions:
            if not motion.is_finished:
                # get_interpolated_position מחזיר (float_row, float_col)
                # שמחושב מה-elapsed_time ומהמסלול
                row, col = motion.get_interpolated_position()

                # jump_fraction: כמה מהקפיצה עבר (0.0 = התחלה, 1.0 = סוף)
                # משמש לחישוב גובה פרבולי בrenderer
                if motion.is_jump and motion.total_duration_ms > 0:
                    jump_fraction = motion.elapsed_time / motion.total_duration_ms
                else:
                    jump_fraction = 0.0

                result.append({
                    "piece": motion.piece,
                    "row": row,
                    "col": col,
                    "is_jump": motion.is_jump,
                    "jump_fraction": jump_fraction
                })
        return result

    def _handle_arrival(self, motion: Motion, board: Board, captured_kings: list[str]) -> None:
        # תיקון 2: לפני הסרת הכלי ממקור — בדוק שהכלי שם הוא אכן הכלי שלנו.
        # אם כלי אחר כבר נחת על המשבצת הזו בינתיים, אל תמחק אותו.
        if motion.source != motion.target:
            piece_at_source = board.get_piece_at(motion.source)
            if piece_at_source is not None and piece_at_source.id == motion.piece.id:
                board.remove_piece_at(motion.source)

        target_piece = board.get_piece_at(motion.target)
        if target_piece and target_piece.color != motion.piece.color:
            if self._piece_has_any_motion(target_piece):
                # הכלי היריב ברח — יש לו תנועה ב-_active_motions
                # (גם אם is_finished=True — עדיין לא עובד ב-_handle_arrival שלו)
                # מסירים את הרישום הישן שלו מהלוח כדי שהתוקף יוכל לנחות.
                board.remove_piece_at(motion.target)
            else:
                # הכלי היריב עמד במקום — נאכל כרגיל
                board.remove_piece_at(motion.target)
                if target_piece.kind == "king":
                    captured_kings.append(target_piece.color)

        motion.piece.cell = motion.target
        if board.get_piece_at(motion.target) is None:
            board.add_piece(motion.piece)

        new_type_for_pawn_arrive_to_lastRow="queen"
        if motion.piece.kind in ("pawn", "p"):
            if (motion.piece.color == "white" and motion.target.row == 0) or \
               (motion.piece.color == "black" and motion.target.row == board.height - 1):
                motion.piece._kind = new_type_for_pawn_arrive_to_lastRow

        motion.piece.cooldown_remaining = COOLDOWN_BY_KIND.get(motion.piece.kind, DEFAULT_COOLDOWN)
