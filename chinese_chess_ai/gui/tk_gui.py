from __future__ import annotations

import tkinter as tk

from .board_view import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    CELL_SIZE,
    IMAGE_OFFSET,
    PIECE_IMAGE_SIZE,
    TARGET_RADIUS,
    asset_bundle_ready,
    board_point,
    piece_asset_code,
    piece_display_code,
    piece_label,
    pixel_to_position,
    required_asset_paths,
)
from .fonts import configure_fonts
from .game_controller import GameController, GameOptions
from .menu import launch_gui


class ThuongDsaGui(GameController):
    """Compatibility wrapper for callers that instantiate the old GUI class."""

    def __init__(self, root: tk.Tk) -> None:
        configure_fonts(root)
        super().__init__(root, GameOptions(mode="local"), show_menu_callback=None)
