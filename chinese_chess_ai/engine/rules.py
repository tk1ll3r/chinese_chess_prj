from __future__ import annotations

from .constants import BOARD_COLS, BOARD_ROWS, PALACE_COLUMNS, PALACE_ROWS
from .moves import Move
from .state import GameState
from .types import Position, Side


def inside_board(position: Position) -> bool:
    row, col = position
    return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS


def inside_palace(side: Side, position: Position) -> bool:
    row, col = position
    return row in PALACE_ROWS[side] and col in PALACE_COLUMNS


def iter_side_positions(state: GameState, side: Side):
    for row, col, _piece in state.iter_pieces(side):
        yield row, col


def generate_pseudo_legal_moves(state: GameState) -> list[Move]:
    raise NotImplementedError(
        "Week 1 scaffold only: pseudo-legal move generation will be implemented in week 2."
    )


def generate_legal_moves(state: GameState) -> list[Move]:
    raise NotImplementedError(
        "Week 1 scaffold only: legal move filtering depends on piece generators and check detection."
    )

