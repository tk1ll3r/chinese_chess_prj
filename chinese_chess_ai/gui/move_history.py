from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass, field

from ..engine.moves import Move
from ..engine.types import Piece, Side


@dataclass
class MoveHistory:
    moves: list[str] = field(default_factory=list)
    captured_by_red: list[str] = field(default_factory=list)
    captured_by_black: list[str] = field(default_factory=list)

    def record(
        self,
        side: Side,
        move: Move,
        captured_piece: Piece | None,
        actor: str,
        piece_display_func: object,
        side_label_func: object,
    ) -> None:
        move_number = len(self.moves) + 1
        capture_text = ""
        if captured_piece is not None:
            captured_code = piece_display_func(captured_piece)
            capture_text = f" x {captured_code}"
            if side is Side.RED:
                self.captured_by_red.append(captured_code)
            else:
                self.captured_by_black.append(captured_code)
        move_str = (
            f"{move_number}. {actor} {side_label_func(side)}: "
            f"({move.start[0]},{move.start[1]}) -> ({move.end[0]},{move.end[1]}){capture_text}"
        )
        self.moves.append(move_str)

    def remove_last_capture(self, side: Side) -> None:
        captures = self.captured_by_red if side is Side.RED else self.captured_by_black
        if captures:
            captures.pop()

    def clear(self) -> None:
        self.moves.clear()
        self.captured_by_red.clear()
        self.captured_by_black.clear()

    def is_empty(self) -> bool:
        return not self.moves
