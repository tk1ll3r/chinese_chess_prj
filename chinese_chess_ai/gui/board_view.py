from __future__ import annotations

import tkinter as tk
import sys
from pathlib import Path
from typing import Callable

from ..engine.constants import BOARD_COLS, BOARD_ROWS
from ..engine.moves import Move
from ..engine.state import GameState
from ..engine.types import Piece, PieceKind, Position, Side

if getattr(sys, "frozen", False):
    ASSET_DIR = Path(sys._MEIPASS) / "assets" / "xqwizard_gui"
else:
    ASSET_DIR = Path(__file__).resolve().parents[2] / "assets" / "xqwizard_gui"
BOARD_IMAGE_NAME = "WHITE.GIF"
SELECTION_IMAGE_NAME = "OOS.GIF"
BASE_CELL_SIZE = 40
BASE_BOARD_WIDTH = 377
BASE_BOARD_HEIGHT = 417
BASE_PIECE_IMAGE_SIZE = 41
BASE_IMAGE_OFFSET = 7
BASE_TARGET_RADIUS = 6

CELL_SIZE = BASE_CELL_SIZE
BOARD_WIDTH = BASE_BOARD_WIDTH
BOARD_HEIGHT = BASE_BOARD_HEIGHT
PIECE_IMAGE_SIZE = BASE_PIECE_IMAGE_SIZE
IMAGE_OFFSET = BASE_IMAGE_OFFSET
TARGET_RADIUS = BASE_TARGET_RADIUS

_PIECE_ASSET_SUFFIX = {
    PieceKind.GENERAL: "K",
    PieceKind.ADVISOR: "A",
    PieceKind.ELEPHANT: "B",
    PieceKind.HORSE: "N",
    PieceKind.CHARIOT: "R",
    PieceKind.CANNON: "C",
    PieceKind.SOLDIER: "P",
}

PIECE_CHINESE_CHARS = {
    PieceKind.CHARIOT: "\u8eca",
    PieceKind.HORSE: "\u99ac",
    PieceKind.ELEPHANT: "\u8c61",
    PieceKind.ADVISOR: "\u58eb",
    PieceKind.GENERAL: {"red": "\u5e25", "black": "\u5c07"},
    PieceKind.CANNON: "\u70ae",
    PieceKind.SOLDIER: {"red": "\u5175", "black": "\u5352"},
}

def get_piece_chinese_char(piece: Piece) -> str:
    char = PIECE_CHINESE_CHARS[piece.kind]
    if isinstance(char, dict):
        return char["red"] if piece.side == Side.RED else char["black"]
    return char

def piece_label(piece: Piece) -> str:
    return _PIECE_ASSET_SUFFIX[piece.kind]

def piece_display_code(piece: Piece) -> str:
    side_prefix = "R" if piece.side is Side.RED else "B"
    return f"{side_prefix}{piece_label(piece)}"

def piece_asset_code(piece: Piece) -> str:
    side_prefix = "R" if piece.side is Side.RED else "B"
    return f"{side_prefix}{_PIECE_ASSET_SUFFIX[piece.kind]}"

def required_asset_paths() -> list[Path]:
    paths = [ASSET_DIR / BOARD_IMAGE_NAME, ASSET_DIR / SELECTION_IMAGE_NAME]
    for side_prefix in ("R", "B"):
        for suffix in _PIECE_ASSET_SUFFIX.values():
            paths.append(ASSET_DIR / f"{side_prefix}{suffix}.GIF")
    return paths

def asset_bundle_ready() -> bool:
    return all(path.exists() for path in required_asset_paths())

def board_point(position: Position) -> tuple[int, int]:
    row, col = position
    return (
        (col * BASE_CELL_SIZE) + BASE_IMAGE_OFFSET + (BASE_PIECE_IMAGE_SIZE // 2),
        (row * BASE_CELL_SIZE) + BASE_IMAGE_OFFSET + (BASE_PIECE_IMAGE_SIZE // 2),
    )

def pixel_to_position(x: int, y: int) -> Position | None:
    row = y // BASE_CELL_SIZE
    col = x // BASE_CELL_SIZE
    if not (0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS):
        return None
    return row, col

def checked_general_position(state: GameState, side: Side) -> Position:
    return state.red_general_position if side is Side.RED else state.black_general_position


def _flip_coord(row: int) -> int:
    return BOARD_ROWS - 1 - row

def _flip_position(pos: Position) -> Position:
    return (_flip_coord(pos[0]), pos[1])


class BoardView:
    def __init__(
        self,
        parent: tk.Misc,
        on_square_clicked: Callable[[Position], None],
    ) -> None:
        if not asset_bundle_ready():
            missing = [str(path) for path in required_asset_paths() if not path.exists()]
            raise FileNotFoundError("Missing GUI assets: " + ", ".join(missing))

        self.on_square_clicked = on_square_clicked
        self.scale_factor = 1
        self.board_width = BASE_BOARD_WIDTH
        self.board_height = BASE_BOARD_HEIGHT
        self.cell_size = BASE_CELL_SIZE
        self.piece_image_size = BASE_PIECE_IMAGE_SIZE
        self.image_offset = BASE_IMAGE_OFFSET
        self.target_radius = BASE_TARGET_RADIUS
        self.flip_board = False
        self.canvas = tk.Canvas(
            parent,
            width=self.board_width,
            height=self.board_height,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.bind("<Button-1>", self._on_click)

        self.board_image_source: tk.PhotoImage | None = None
        self.selection_image_source: tk.PhotoImage | None = None
        self.piece_image_sources: dict[str, tk.PhotoImage] = {}
        self.board_image: tk.PhotoImage | None = None
        self.selection_image: tk.PhotoImage | None = None
        self.piece_images: dict[str, tk.PhotoImage] = {}
        self._load_images()

        self._animating = False
        self._animation_callback_id: str | None = None

    def grid(self, **kwargs: object) -> None:
        self.canvas.grid(**kwargs)

    def _load_board_image(self) -> None:
        try:
            self.board_image_source = tk.PhotoImage(file=ASSET_DIR / BOARD_IMAGE_NAME)
            self.board_image = self.board_image_source
        except Exception:
            pass

    def configure_scale(self, scale_factor: int) -> None:
        self.scale_factor = max(1, min(scale_factor, 4))
        self.board_width = BASE_BOARD_WIDTH * self.scale_factor
        self.board_height = BASE_BOARD_HEIGHT * self.scale_factor
        self.cell_size = BASE_CELL_SIZE * self.scale_factor
        self.piece_image_size = BASE_PIECE_IMAGE_SIZE * self.scale_factor
        self.image_offset = BASE_IMAGE_OFFSET * self.scale_factor
        self.target_radius = BASE_TARGET_RADIUS * self.scale_factor

        if self.board_image_source is not None:
            self.board_image = self.board_image_source.zoom(self.scale_factor, self.scale_factor)
        if self.selection_image_source is not None:
            self.selection_image = self.selection_image_source.zoom(
                self.scale_factor,
                self.scale_factor,
            )
        self.piece_images = {
            code: image.zoom(self.scale_factor, self.scale_factor)
            for code, image in self.piece_image_sources.items()
        }
        self.canvas.config(width=self.board_width, height=self.board_height)

    def draw(
        self,
        state: GameState,
        selected_square: Position | None = None,
        legal_moves: list[Move] | tuple[Move, ...] = (),
        checked_square: Position | None = None,
        check_blink_on: bool = True,
        banner: str = "",
        flip: bool = False,
    ) -> None:
        self.flip_board = flip
        self.canvas.delete("all")
        self._draw_board()
        self._draw_selection_and_targets(selected_square, legal_moves)
        self._draw_pieces(state)
        if checked_square is not None:
            self._draw_check_highlight(checked_square, check_blink_on)
        if banner:
            self._draw_banner(banner)

    def position_from_pixel(self, x: int, y: int) -> Position | None:
        row = y // self.cell_size
        col = x // self.cell_size
        if not (0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS):
            return None
        if self.flip_board:
            row = _flip_coord(row)
        return row, col

    def _load_images(self) -> None:
        self.board_image_source = tk.PhotoImage(file=ASSET_DIR / BOARD_IMAGE_NAME)
        self.selection_image_source = tk.PhotoImage(file=ASSET_DIR / SELECTION_IMAGE_NAME)
        for side_prefix in ("R", "B"):
            for suffix in _PIECE_ASSET_SUFFIX.values():
                code = f"{side_prefix}{suffix}"
                self.piece_image_sources[code] = tk.PhotoImage(file=ASSET_DIR / f"{code}.GIF")
        self.configure_scale(1)

    def _load_board_image(self) -> None:
        try:
            self.board_image_source = tk.PhotoImage(file=ASSET_DIR / BOARD_IMAGE_NAME)
            self.board_image = self.board_image_source
        except Exception:
            pass

    def _on_click(self, event: tk.Event[tk.Canvas]) -> None:
        position = self.position_from_pixel(event.x, event.y)
        if position is not None:
            self.on_square_clicked(position)

    def _draw_board(self) -> None:
        if self.board_image is not None:
            self.canvas.create_image(0, 0, image=self.board_image, anchor="nw")

    def _draw_pieces(self, state: GameState) -> None:
        for row, col, piece in state.iter_pieces():
            r = _flip_coord(row) if self.flip_board else row
            image = self.piece_images[piece_asset_code(piece)]
            image_x, image_y = self._scaled_image_origin((r, col))
            self.canvas.create_image(image_x, image_y, image=image, anchor="nw")

    def _draw_selection_and_targets(
        self,
        selected_square: Position | None,
        legal_moves: list[Move] | tuple[Move, ...],
    ) -> None:
        if selected_square is not None and self.selection_image is not None:
            r = _flip_coord(selected_square[0]) if self.flip_board else selected_square[0]
            image_x, image_y = self._scaled_image_origin((r, selected_square[1]))
            self.canvas.create_image(image_x, image_y, image=self.selection_image, anchor="nw")

        for move in legal_moves:
            r = _flip_coord(move.end[0]) if self.flip_board else move.end[0]
            center_x, center_y = self._scaled_board_point((r, move.end[1]))
            radius = self.target_radius
            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill="#4CAF50",
                outline="#2E7D32",
                width=max(2, self.scale_factor),
            )

    def _draw_check_highlight(self, position: Position, blink_on: bool) -> None:
        r = _flip_coord(position[0]) if self.flip_board else position[0]
        center_x, center_y = self._scaled_board_point((r, position[1]))
        base_radius = max(18 * self.scale_factor, self.piece_image_size // 2)
        pulse_factor = 1.05 if blink_on else 0.95
        radius = int(base_radius * pulse_factor)
        outline = "#d60000" if blink_on else "#ff6666"
        width = max(3, 3 * self.scale_factor)
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline=outline,
            width=width,
        )

    def _draw_banner(self, banner: str) -> None:
        x = self.board_width // 2
        y = max(30, 34 * self.scale_factor)
        font_size = 14 + (2 * self.scale_factor)
        self.canvas.create_rectangle(
            x - (115 * self.scale_factor),
            y - (18 * self.scale_factor),
            x + (115 * self.scale_factor),
            y + (18 * self.scale_factor),
            fill="#fff3f3",
            outline="#d60000",
            width=max(2, self.scale_factor),
        )
        self.canvas.create_text(
            x,
            y,
            text=banner,
            fill="#a40000",
            font=("TkDefaultFont", font_size, "bold"),
        )

    def _scaled_board_point(self, position: Position) -> tuple[int, int]:
        row, col = position
        return (
            (col * self.cell_size) + self.image_offset + (self.piece_image_size // 2),
            (row * self.cell_size) + self.image_offset + (self.piece_image_size // 2),
        )

    def _scaled_image_origin(self, position: Position) -> tuple[int, int]:
        row, col = position
        return (
            (col * self.cell_size) + self.image_offset,
            (row * self.cell_size) + self.image_offset,
        )

    def animate_move(
        self,
        state: GameState,
        move: Move,
        duration_ms: int = 250,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        if self._animating:
            return

        self._animating = True
        start_x, start_y = self._scaled_board_point(
            (_flip_coord(move.start[0]) if self.flip_board else move.start[0], move.start[1])
        )
        end_x, end_y = self._scaled_board_point(
            (_flip_coord(move.end[0]) if self.flip_board else move.end[0], move.end[1])
        )

        piece = state.board[move.start[0]][move.start[1]]
        if piece is None:
            self._animating = False
            if on_complete:
                on_complete()
            return

        frames = max(1, duration_ms // 16)
        dx = (end_x - start_x) / frames
        dy = (end_y - start_y) / frames

        def animate_frame(frame: int) -> None:
            if frame >= frames:
                self._animating = False
                if on_complete:
                    on_complete()
                return

            self.canvas.delete("all")
            self._draw_board()

            for row, col, p in state.iter_pieces():
                if (row, col) == move.start:
                    continue
                r = _flip_coord(row) if self.flip_board else row
                image = self.piece_images[piece_asset_code(p)]
                image_x, image_y = self._scaled_image_origin((r, col))
                self.canvas.create_image(image_x, image_y, image=image, anchor="nw")

            current_x = start_x + (dx * frame)
            current_y = start_y + (dy * frame)
            image = self.piece_images[piece_asset_code(piece)]
            self.canvas.create_image(
                current_x - self.piece_image_size // 2,
                current_y - self.piece_image_size // 2,
                image=image,
                anchor="nw",
            )

            self._animation_callback_id = self.canvas.after(16, lambda: animate_frame(frame + 1))

        animate_frame(0)

    def animate_capture_flash(
        self,
        position: Position,
        duration_ms: int = 150,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        r = _flip_coord(position[0]) if self.flip_board else position[0]
        center_x, center_y = self._scaled_board_point((r, position[1]))
        radius = self.piece_image_size // 2

        def flash_frame(frame: int, max_frames: int = 6) -> None:
            if frame >= max_frames:
                if on_complete:
                    on_complete()
                return

            alpha = 1.0 - (frame / max_frames)
            color = f"#{int(255 * alpha):02x}{int(255 * alpha):02x}00"

            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill=color,
                outline="",
            )

            self.canvas.after(duration_ms // max_frames, lambda: flash_frame(frame + 1, max_frames))

        flash_frame(0)

    def is_animating(self) -> bool:
        return self._animating
