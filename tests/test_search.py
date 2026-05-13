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

        chosen_move = choose_move(state, SearchConfig(depth=6))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertIn((chosen_move.start, chosen_move.end), legal_moves)

    def test_search_does_not_mutate_state(self) -> None:
        state = GameState.initial()
        original_board = state.render_ascii()
        original_side = state.side_to_move
        original_history_length = len(state.move_history)

        _ = choose_move(state, SearchConfig(depth=6))

        self.assertEqual(state.render_ascii(), original_board)
        self.assertEqual(state.side_to_move, original_side)
        self.assertEqual(len(state.move_history), original_history_length)

    def test_search_returns_legal_move_with_timeout(self) -> None:
        state = GameState.initial()
        opening_move = next(
            move
            for move in generate_legal_moves(state)
            if (move.start, move.end) == ((6, 4), (5, 4))
        )
        state.make_move(opening_move)
        original_board = state.render_ascii()
        original_side = state.side_to_move
        original_history_length = len(state.move_history)
        legal_moves = {(move.start, move.end) for move in generate_legal_moves(state)}

        chosen_move = choose_move(state, SearchConfig(depth=4))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertIn((chosen_move.start, chosen_move.end), legal_moves)
        self.assertEqual(state.render_ascii(), original_board)
        self.assertEqual(state.side_to_move, original_side)
        self.assertEqual(len(state.move_history), original_history_length)

    def test_search_prefers_profitable_capture(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.SOLDIER, 3, 4),
                (Side.RED, PieceKind.CHARIOT, 5, 0),
                (Side.BLACK, PieceKind.HORSE, 2, 0),
            ],
            side_to_move=Side.RED,
        )

        chosen_move = choose_move(state, SearchConfig(depth=8))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertEqual((chosen_move.start, chosen_move.end), ((5, 0), (2, 0)))

    def test_search_returns_legal_move_from_complex_position(self) -> None:
        state = GameState.from_placements(
            [
                (Side.BLACK, PieceKind.GENERAL, 0, 3),
                (Side.RED, PieceKind.GENERAL, 9, 4),
                (Side.RED, PieceKind.CHARIOT, 5, 0),
                (Side.BLACK, PieceKind.HORSE, 2, 0),
                (Side.BLACK, PieceKind.SOLDIER, 3, 4),
            ],
            side_to_move=Side.RED,
        )
        legal_moves = {(move.start, move.end) for move in generate_legal_moves(state)}

        chosen_move = choose_move(state, SearchConfig(depth=6))

        self.assertIsNotNone(chosen_move)
        assert chosen_move is not None
        self.assertIn((chosen_move.start, chosen_move.end), legal_moves)


if __name__ == "__main__":
    unittest.main()
