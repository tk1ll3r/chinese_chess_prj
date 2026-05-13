import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chinese_chess_ai.engine.types import Piece, PieceKind, Side
from chinese_chess_ai.engine.constants import BOARD_COLS, BOARD_ROWS
from chinese_chess_ai.gui.tk_gui import (
    BACKGROUND_IMAGE_NAME,
    CELL_SIZE,
    FIRST_IMAGE_NAME,
    IMAGE_OFFSET,
    ONSITE_BACKGROUND_IMAGE_NAME,
    PIECE_IMAGE_SIZE,
    asset_bundle_ready,
    background_asset_ready,
    background_image_path,
    board_point,
    piece_asset_code,
    piece_display_code,
    piece_label,
    pixel_to_position,
    required_asset_paths,
)


class GuiRenderingTests(unittest.TestCase):
    def test_piece_display_code_matches_canvas_labels(self) -> None:
        self.assertEqual(piece_display_code(Piece(Side.RED, PieceKind.GENERAL)), "RK")
        self.assertEqual(piece_display_code(Piece(Side.BLACK, PieceKind.GENERAL)), "BK")
        self.assertEqual(piece_display_code(Piece(Side.RED, PieceKind.CHARIOT)), "RR")
        self.assertEqual(piece_display_code(Piece(Side.BLACK, PieceKind.CANNON)), "BC")

    def test_piece_label_is_side_neutral(self) -> None:
        self.assertEqual(piece_label(Piece(Side.RED, PieceKind.HORSE)), "N")
        self.assertEqual(piece_label(Piece(Side.BLACK, PieceKind.HORSE)), "N")

    def test_piece_asset_code_matches_xqwizard_asset_names(self) -> None:
        self.assertEqual(piece_asset_code(Piece(Side.RED, PieceKind.GENERAL)), "RK")
        self.assertEqual(piece_asset_code(Piece(Side.BLACK, PieceKind.GENERAL)), "BK")
        self.assertEqual(piece_asset_code(Piece(Side.RED, PieceKind.CHARIOT)), "RR")
        self.assertEqual(piece_asset_code(Piece(Side.BLACK, PieceKind.CANNON)), "BC")

    def test_required_assets_exist(self) -> None:
        self.assertTrue(asset_bundle_ready())
        for path in required_asset_paths():
            self.assertTrue(path.exists(), str(path))

    def test_background_asset_exists(self) -> None:
        for image_name in (
            FIRST_IMAGE_NAME,
            BACKGROUND_IMAGE_NAME,
            ONSITE_BACKGROUND_IMAGE_NAME,
        ):
            with self.subTest(image_name=image_name):
                self.assertTrue(background_asset_ready(image_name))
                self.assertTrue(background_image_path(image_name).exists())
                self.assertEqual(background_image_path(image_name).name, image_name)

    def test_board_point_maps_position_to_canvas_center(self) -> None:
        expected_origin = IMAGE_OFFSET + (PIECE_IMAGE_SIZE // 2)
        self.assertEqual(board_point((0, 0)), (expected_origin, expected_origin))
        self.assertEqual(
            board_point((9, 8)),
            (
                expected_origin + (8 * CELL_SIZE),
                expected_origin + (9 * CELL_SIZE),
            ),
        )

    def test_pixel_to_position_rounds_to_nearest_board_point(self) -> None:
        x, y = board_point((6, 4))
        self.assertEqual(pixel_to_position(x + 8, y - 7), (6, 4))
        self.assertEqual(pixel_to_position(0, 0), (0, 0))
        self.assertIsNone(pixel_to_position(BOARD_COLS * CELL_SIZE, BOARD_ROWS * CELL_SIZE))
