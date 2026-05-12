from __future__ import annotations

from ..engine.types import PieceKind, Side

# Piece-Square Tables for positional evaluation
# Values are from Red's perspective (higher = better for Red)
# Black's values are mirrored vertically

# General (King) - prefers staying in palace, center is slightly better
PST_GENERAL = [
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 2, 3, 2, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -1, -1, -1, 0, 0, 0],
    [0, 0, 0, -2, -3, -2, 0, 0, 0],
    [0, 0, 0, -1, -1, -1, 0, 0, 0],
]

# Advisor - prefers diagonal positions in palace
PST_ADVISOR = [
    [0, 0, 0, 2, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 0, 0],
    [0, 0, 0, 2, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, -2, 0, -2, 0, 0, 0],
    [0, 0, 0, 0, -3, 0, 0, 0, 0],
    [0, 0, 0, -2, 0, -2, 0, 0, 0],
]

# Elephant - stays on own side, prefers center positions
PST_ELEPHANT = [
    [0, 0, 2, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 3, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 2, 0, 0],
    [0, 0, -2, 0, 0, 0, -2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, 0, 0, -3, 0, 0, 0, -1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -2, 0, 0, 0, -2, 0, 0],
]

# Horse - prefers center, avoids edges
PST_HORSE = [
    [0, -3, 1, 0, 0, 0, 1, -3, 0],
    [-2, 0, 3, 1, 1, 1, 3, 0, -2],
    [1, 2, 4, 3, 3, 3, 4, 2, 1],
    [0, 1, 3, 4, 4, 4, 3, 1, 0],
    [0, 1, 3, 4, 5, 4, 3, 1, 0],
    [0, -1, -3, -4, -5, -4, -3, -1, 0],
    [0, -1, -3, -4, -4, -4, -3, -1, 0],
    [-1, -2, -4, -3, -3, -3, -4, -2, -1],
    [2, 0, -3, -1, -1, -1, -3, 0, 2],
    [0, 3, -1, 0, 0, 0, -1, 3, 0],
]

# Chariot (Rook) - prefers center and advanced positions
PST_CHARIOT = [
    [6, 7, 7, 8, 8, 8, 7, 7, 6],
    [6, 8, 8, 9, 9, 9, 8, 8, 6],
    [6, 7, 7, 8, 8, 8, 7, 7, 6],
    [5, 6, 6, 7, 7, 7, 6, 6, 5],
    [4, 5, 5, 6, 6, 6, 5, 5, 4],
    [-4, -5, -5, -6, -6, -6, -5, -5, -4],
    [-5, -6, -6, -7, -7, -7, -6, -6, -5],
    [-6, -7, -7, -8, -8, -8, -7, -7, -6],
    [-6, -8, -8, -9, -9, -9, -8, -8, -6],
    [-6, -7, -7, -8, -8, -8, -7, -7, -6],
]

# Cannon - prefers center, slightly advanced
PST_CANNON = [
    [3, 3, 2, 3, 4, 3, 2, 3, 3],
    [2, 3, 3, 3, 3, 3, 3, 3, 2],
    [2, 3, 4, 4, 5, 4, 4, 3, 2],
    [0, 1, 2, 3, 3, 3, 2, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, -1, -2, -3, -3, -3, -2, -1, 0],
    [-2, -3, -4, -4, -5, -4, -4, -3, -2],
    [-2, -3, -3, -3, -3, -3, -3, -3, -2],
    [-3, -3, -2, -3, -4, -3, -2, -3, -3],
]

# Soldier (Pawn) - prefers advancing and center after crossing river
PST_SOLDIER = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 3, 4, 5, 6, 5, 4, 3, 2],
    [10, 15, 15, 20, 25, 20, 15, 15, 10],
    [-10, -15, -15, -20, -25, -20, -15, -15, -10],
    [-2, -3, -4, -5, -6, -5, -4, -3, -2],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

PST_TABLES = {
    PieceKind.GENERAL: PST_GENERAL,
    PieceKind.ADVISOR: PST_ADVISOR,
    PieceKind.ELEPHANT: PST_ELEPHANT,
    PieceKind.HORSE: PST_HORSE,
    PieceKind.CHARIOT: PST_CHARIOT,
    PieceKind.CANNON: PST_CANNON,
    PieceKind.SOLDIER: PST_SOLDIER,
}


def get_piece_square_value(kind: PieceKind, row: int, col: int, side: Side) -> float:
    """Get positional value for a piece at given position."""
    table = PST_TABLES[kind]
    value = table[row][col]
    return value if side == Side.RED else -value
