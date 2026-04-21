from __future__ import annotations

from dataclasses import dataclass

from .types import Piece, Position, Side


@dataclass(frozen=True, slots=True)
class Move:
    start: Position
    end: Position
    note: str = ""


@dataclass(frozen=True, slots=True)
class MoveRecord:
    move: Move
    moved_piece: Piece
    captured_piece: Piece | None
    previous_side_to_move: Side
    previous_red_general: Position
    previous_black_general: Position

