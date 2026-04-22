import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chinese_chess_ai.engine.rules import (
    generate_legal_moves,
    generate_pseudo_legal_moves,
    generals_face_each_other,
    is_in_check,
)
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.engine.types import PieceKind, Side


def move_set(state: GameState, legal: bool = True) -> set[tuple[tuple[int, int], tuple[int, int]]]:
    generator = generate_legal_moves if legal else generate_pseudo_legal_moves
    return {(move.start, move.end) for move in generator(state)}


class RulesEngineTests(unittest.TestCase):
    def test_initial_position_generates_legal_moves(self) -> None:
        state = GameState.initial()
        moves = move_set(state)

        self.assertGreater(len(moves), 0)
        self.assertIn(((6, 0), (5, 0)), moves)
        self.assertIn(((9, 1), (7, 0)), moves)
        self.assertIn(((9, 1), (7, 2)), moves)

    def test_soldier_moves_before_and_after_crossing_river(self) -> None:
        before_river = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 6, 4),
            ]
        )
        before_moves = move_set(before_river)
        self.assertIn(((6, 4), (5, 4)), before_moves)
        self.assertNotIn(((6, 4), (6, 3)), before_moves)
        self.assertNotIn(((6, 4), (6, 5)), before_moves)

        after_river = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 4, 4),
            ]
        )
        after_moves = move_set(after_river)
        self.assertIn(((4, 4), (3, 4)), after_moves)
        self.assertIn(((4, 4), (4, 3)), after_moves)
        self.assertIn(((4, 4), (4, 5)), after_moves)
        self.assertNotIn(((4, 4), (5, 4)), after_moves)

    def test_horse_leg_block_rule(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.HORSE, 7, 1),
                (Side.RED, PieceKind.SOLDIER, 8, 1),
            ]
        )

        moves = move_set(state)
        self.assertNotIn(((7, 1), (9, 0)), moves)
        self.assertNotIn(((7, 1), (9, 2)), moves)
        self.assertIn(((7, 1), (5, 0)), moves)
        self.assertIn(((7, 1), (5, 2)), moves)

    def test_elephant_eye_block_and_river_rule(self) -> None:
        blocked_eye = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.ELEPHANT, 9, 2),
                (Side.RED, PieceKind.SOLDIER, 8, 3),
            ]
        )
        blocked_moves = move_set(blocked_eye)
        self.assertIn(((9, 2), (7, 0)), blocked_moves)
        self.assertNotIn(((9, 2), (7, 4)), blocked_moves)

        river_limit = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.ELEPHANT, 5, 2),
            ]
        )
        river_moves = move_set(river_limit)
        self.assertIn(((5, 2), (7, 0)), river_moves)
        self.assertIn(((5, 2), (7, 4)), river_moves)
        self.assertNotIn(((5, 2), (3, 0)), river_moves)
        self.assertNotIn(((5, 2), (3, 4)), river_moves)

    def test_cannon_requires_exactly_one_screen_to_capture(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.CANNON, 7, 1),
                (Side.RED, PieceKind.SOLDIER, 5, 1),
                (Side.BLACK, PieceKind.HORSE, 3, 1),
            ]
        )

        moves = move_set(state)
        self.assertIn(((7, 1), (3, 1)), moves)

        no_screen = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.CANNON, 7, 1),
                (Side.BLACK, PieceKind.HORSE, 3, 1),
            ]
        )
        self.assertNotIn(((7, 1), (3, 1)), move_set(no_screen))

    def test_flying_general_exposure_is_filtered_out(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 4),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 4, 4),
            ]
        )

        pseudo_moves = move_set(state, legal=False)
        legal_moves = move_set(state, legal=True)

        self.assertTrue(generals_face_each_other(GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 4),
                (Side.RED, PieceKind.GENERAL, 9, 4),
            ]
        )))
        self.assertIn(((4, 4), (4, 3)), pseudo_moves)
        self.assertIn(((4, 4), (4, 5)), pseudo_moves)
        self.assertNotIn(((4, 4), (4, 3)), legal_moves)
        self.assertNotIn(((4, 4), (4, 5)), legal_moves)

    def test_check_detection_with_chariot_attack(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.BLACK, PieceKind.CHARIOT, 1, 4),
            ],
            side_to_move=Side.RED,
        )

        self.assertTrue(is_in_check(state, Side.RED))


if __name__ == "__main__":
    unittest.main()
