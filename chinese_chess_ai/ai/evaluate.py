from __future__ import annotations

from ..engine.constants import MATERIAL_VALUES
from ..engine.state import GameState
from ..engine.types import Side


def material_score(state: GameState, perspective: Side) -> int:
    score = 0
    for _row, _col, piece in state.iter_pieces():
        value = MATERIAL_VALUES[piece.kind]
        if piece.side is perspective:
            score += value
        else:
            score -= value
    return score

