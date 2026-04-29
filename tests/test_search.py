import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chinese_chess_ai.ai.search import SearchConfig, choose_move
from chinese_chess_ai.engine.rules import generate_legal_moves
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.engine.types import PieceKind, Side


class SearchTests(unittest.TestCase):
    def test_choose_move_returns_legal_move_from_initial_position(self) -> None:
        state = GameState.initial()
        legal_moves = {(move.start, move.end) for move in generate_legal_moves(state)}

        chosen_move = choose_move(state, SearchConfig(depth=1, use_alpha_beta=True))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertIn((chosen_move.start, chosen_move.end), legal_moves)

    def test_search_does_not_mutate_state(self) -> None:
        state = GameState.initial()
        original_board = state.render_ascii()
        original_side = state.side_to_move
        original_history_length = len(state.move_history)

        _ = choose_move(state, SearchConfig(depth=2, use_alpha_beta=True))

        self.assertEqual(state.render_ascii(), original_board)
        self.assertEqual(state.side_to_move, original_side)
        self.assertEqual(len(state.move_history), original_history_length)

    def test_search_prefers_profitable_capture(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 4),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 6, 4),
                (Side.RED, PieceKind.CHARIOT, 5, 0),
                (Side.BLACK, PieceKind.HORSE, 2, 0),
            ],
            side_to_move=Side.RED,
        )

        chosen_move = choose_move(state, SearchConfig(depth=1, use_alpha_beta=True))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertEqual((chosen_move.start, chosen_move.end), ((5, 0), (2, 0)))

    def test_alpha_beta_matches_plain_negamax(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 4),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 6, 4),
                (Side.RED, PieceKind.CHARIOT, 5, 0),
                (Side.BLACK, PieceKind.HORSE, 2, 0),
                (Side.BLACK, PieceKind.SOLDIER, 5, 3),
            ],
            side_to_move=Side.RED,
        )

        with_alpha_beta = choose_move(state, SearchConfig(depth=2, use_alpha_beta=True))
        without_alpha_beta = choose_move(state, SearchConfig(depth=2, use_alpha_beta=False))

        self.assertIsNotNone(with_alpha_beta)
        self.assertIsNotNone(without_alpha_beta)
        assert with_alpha_beta is not None
        assert without_alpha_beta is not None
        self.assertEqual((with_alpha_beta.start, with_alpha_beta.end), (without_alpha_beta.start, without_alpha_beta.end))


if __name__ == "__main__":
    unittest.main()
