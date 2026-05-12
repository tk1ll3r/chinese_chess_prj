"""Chinese Chess DSA project - main package."""

from .engine import (
    Board,
    BOARD_COLS,
    BOARD_ROWS,
    GameState,
    INITIAL_PLACEMENTS,
    is_in_check,
    generate_legal_moves,
    MATERIAL_VALUES,
    Move,
    MoveRecord,
    PALACE_COLUMNS,
    PALACE_ROWS,
    Piece,
    PieceKind,
    Position,
    Side,
)

__all__ = [
    "Board",
    "BOARD_COLS",
    "BOARD_ROWS",
    "GameState",
    "INITIAL_PLACEMENTS",
    "is_in_check",
    "generate_legal_moves",
    "MATERIAL_VALUES",
    "Move",
    "MoveRecord",
    "PALACE_COLUMNS",
    "PALACE_ROWS",
    "Piece",
    "PieceKind",
    "Position",
    "Side",
]
