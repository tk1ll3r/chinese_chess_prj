from __future__ import annotations

from .types import PieceKind, Side

BOARD_ROWS = 10
BOARD_COLS = 9
EMPTY_CELL = None

PALACE_COLUMNS = (3, 4, 5)
PALACE_ROWS = {
    Side.BLACK: (0, 1, 2),
    Side.RED: (7, 8, 9),
}

INITIAL_PLACEMENTS = (
    (Side.BLACK, PieceKind.CHARIOT, 0, 0),
    (Side.BLACK, PieceKind.HORSE, 0, 1),
    (Side.BLACK, PieceKind.ELEPHANT, 0, 2),
    (Side.BLACK, PieceKind.ADVISOR, 0, 3),
    (Side.BLACK, PieceKind.GENERAL, 0, 4),
    (Side.BLACK, PieceKind.ADVISOR, 0, 5),
    (Side.BLACK, PieceKind.ELEPHANT, 0, 6),
    (Side.BLACK, PieceKind.HORSE, 0, 7),
    (Side.BLACK, PieceKind.CHARIOT, 0, 8),
    (Side.BLACK, PieceKind.CANNON, 2, 1),
    (Side.BLACK, PieceKind.CANNON, 2, 7),
    (Side.BLACK, PieceKind.SOLDIER, 3, 0),
    (Side.BLACK, PieceKind.SOLDIER, 3, 2),
    (Side.BLACK, PieceKind.SOLDIER, 3, 4),
    (Side.BLACK, PieceKind.SOLDIER, 3, 6),
    (Side.BLACK, PieceKind.SOLDIER, 3, 8),
    (Side.RED, PieceKind.CHARIOT, 9, 0),
    (Side.RED, PieceKind.HORSE, 9, 1),
    (Side.RED, PieceKind.ELEPHANT, 9, 2),
    (Side.RED, PieceKind.ADVISOR, 9, 3),
    (Side.RED, PieceKind.GENERAL, 9, 4),
    (Side.RED, PieceKind.ADVISOR, 9, 5),
    (Side.RED, PieceKind.ELEPHANT, 9, 6),
    (Side.RED, PieceKind.HORSE, 9, 7),
    (Side.RED, PieceKind.CHARIOT, 9, 8),
    (Side.RED, PieceKind.CANNON, 7, 1),
    (Side.RED, PieceKind.CANNON, 7, 7),
    (Side.RED, PieceKind.SOLDIER, 6, 0),
    (Side.RED, PieceKind.SOLDIER, 6, 2),
    (Side.RED, PieceKind.SOLDIER, 6, 4),
    (Side.RED, PieceKind.SOLDIER, 6, 6),
    (Side.RED, PieceKind.SOLDIER, 6, 8),
)

MATERIAL_VALUES = {
    PieceKind.GENERAL: 10000,
    PieceKind.ADVISOR: 20,
    PieceKind.ELEPHANT: 20,
    PieceKind.HORSE: 45,
    PieceKind.CHARIOT: 90,
    PieceKind.CANNON: 50,
    PieceKind.SOLDIER: 10,
}

