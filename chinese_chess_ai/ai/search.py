from __future__ import annotations

from dataclasses import dataclass

from ..engine.moves import Move
from ..engine.state import GameState


@dataclass(slots=True)
class SearchConfig:
    depth: int = 2
    use_alpha_beta: bool = True


def choose_move(state: GameState, config: SearchConfig | None = None) -> Move | None:
    _ = state
    _ = config or SearchConfig()
    raise NotImplementedError(
        "Week 1 scaffold only: search will be implemented after legal move generation is stable."
    )

