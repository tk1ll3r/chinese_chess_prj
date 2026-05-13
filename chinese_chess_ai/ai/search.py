from __future__ import annotations

from dataclasses import dataclass, field

from ..engine.moves import Move
from ..engine.state import GameState
from .pikafish_engine import PikafishEngine


@dataclass(slots=True)
class SearchConfig:
    depth: int = 5
    time_limit: float | None = None


@dataclass(slots=True)
class SearchInfo:
    depth: int = 0
    score: float = 0.0
    pv: list[Move] = field(default_factory=list)
    time_ms: float = 0.0
    nodes: int = 0


_engine: PikafishEngine | None = None


def _get_engine() -> PikafishEngine:
    global _engine
    if _engine is None:
        _engine = PikafishEngine()
    return _engine


def choose_move(state: GameState, config: SearchConfig | None = None) -> Move | None:
    if config is None:
        config = SearchConfig()
    return _get_engine().choose_move(state, depth=config.depth, time_limit=config.time_limit)


def get_search_info() -> SearchInfo:
    return SearchInfo()
