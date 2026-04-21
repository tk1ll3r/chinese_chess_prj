from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from .constants import BOARD_COLS, BOARD_ROWS, INITIAL_PLACEMENTS
from .moves import Move, MoveRecord
from .types import Piece, PieceKind, Position, Side

Board = list[list[Piece | None]]


def _validate_position(position: Position) -> None:
    row, col = position
    if not (0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS):
        raise ValueError(f"Position out of board bounds: {position}")


def create_empty_board() -> Board:
    return [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]


def create_initial_board() -> Board:
    board = create_empty_board()
    for side, kind, row, col in INITIAL_PLACEMENTS:
        board[row][col] = Piece(side=side, kind=kind)
    return board


@dataclass(slots=True)
class GameState:
    board: Board
    side_to_move: Side = Side.RED
    red_general_position: Position = (9, 4)
    black_general_position: Position = (0, 4)
    move_history: list[MoveRecord] = field(default_factory=list)

    @classmethod
    def initial(cls) -> "GameState":
        return cls(board=create_initial_board())

    def clone(self) -> "GameState":
        return GameState(
            board=deepcopy(self.board),
            side_to_move=self.side_to_move,
            red_general_position=self.red_general_position,
            black_general_position=self.black_general_position,
            move_history=list(self.move_history),
        )

    def piece_at(self, position: Position) -> Piece | None:
        _validate_position(position)
        row, col = position
        return self.board[row][col]

    def build_move(self, start: Position, end: Position, note: str = "") -> Move:
        _validate_position(start)
        _validate_position(end)

        piece = self.piece_at(start)
        if piece is None:
            raise ValueError(f"No piece at starting square: {start}")
        if piece.side is not self.side_to_move:
            raise ValueError(
                f"Piece at {start} belongs to {piece.side.value}, not {self.side_to_move.value}"
            )
        return Move(start=start, end=end, note=note)

    def make_move(self, move: Move) -> None:
        moved_piece = self.piece_at(move.start)
        if moved_piece is None:
            raise ValueError(f"No piece available to move from {move.start}")
        if moved_piece.side is not self.side_to_move:
            raise ValueError("Cannot move a piece that does not belong to the active side")

        captured_piece = self.piece_at(move.end)
        if captured_piece is not None and captured_piece.side is moved_piece.side:
            raise ValueError("Cannot capture a piece from the same side")

        record = MoveRecord(
            move=move,
            moved_piece=moved_piece,
            captured_piece=captured_piece,
            previous_side_to_move=self.side_to_move,
            previous_red_general=self.red_general_position,
            previous_black_general=self.black_general_position,
        )

        start_row, start_col = move.start
        end_row, end_col = move.end
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = moved_piece

        if moved_piece.kind is PieceKind.GENERAL:
            if moved_piece.side is Side.RED:
                self.red_general_position = move.end
            else:
                self.black_general_position = move.end

        self.side_to_move = self.side_to_move.opponent()
        self.move_history.append(record)

    def undo_move(self) -> Move | None:
        if not self.move_history:
            return None

        record = self.move_history.pop()
        start_row, start_col = record.move.start
        end_row, end_col = record.move.end

        self.board[start_row][start_col] = record.moved_piece
        self.board[end_row][end_col] = record.captured_piece
        self.side_to_move = record.previous_side_to_move
        self.red_general_position = record.previous_red_general
        self.black_general_position = record.previous_black_general
        return record.move

    def iter_pieces(self, side: Side | None = None):
        for row_index, row in enumerate(self.board):
            for col_index, piece in enumerate(row):
                if piece is None:
                    continue
                if side is not None and piece.side is not side:
                    continue
                yield row_index, col_index, piece

    def count_pieces(self, side: Side | None = None) -> int:
        return sum(1 for _ in self.iter_pieces(side))

    def render_ascii(self) -> str:
        lines = []
        for row in self.board:
            lines.append(" ".join(piece.short_code() if piece else "__" for piece in row))
        return "\n".join(lines)

