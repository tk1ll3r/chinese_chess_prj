import unittest

from chinese_chess_ai.ai.evaluate import material_score
from chinese_chess_ai.engine.rules import inside_board, inside_palace
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.engine.types import PieceKind, Side


class GameStateTests(unittest.TestCase):
    def test_initial_state_has_expected_piece_count(self) -> None:
        state = GameState.initial()
        self.assertEqual(state.count_pieces(), 32)
        self.assertEqual(state.count_pieces(Side.RED), 16)
        self.assertEqual(state.count_pieces(Side.BLACK), 16)
        self.assertEqual(state.red_general_position, (9, 4))
        self.assertEqual(state.black_general_position, (0, 4))

    def test_make_and_undo_move_restore_state(self) -> None:
        state = GameState.initial()
        original_board = state.render_ascii()

        move = state.build_move((6, 0), (5, 0), note="Red soldier opens")
        state.make_move(move)

        moved_piece = state.piece_at((5, 0))
        self.assertIsNotNone(moved_piece)
        self.assertEqual(moved_piece.kind, PieceKind.SOLDIER)
        self.assertIsNone(state.piece_at((6, 0)))
        self.assertEqual(state.side_to_move, Side.BLACK)
        self.assertEqual(len(state.move_history), 1)

        undone = state.undo_move()
        self.assertEqual(undone, move)
        self.assertEqual(state.render_ascii(), original_board)
        self.assertEqual(state.side_to_move, Side.RED)
        self.assertEqual(len(state.move_history), 0)

    def test_initial_material_score_is_balanced(self) -> None:
        state = GameState.initial()
        self.assertEqual(material_score(state, Side.RED), 0)
        self.assertEqual(material_score(state, Side.BLACK), 0)

    def test_board_and_palace_helpers(self) -> None:
        self.assertTrue(inside_board((0, 0)))
        self.assertTrue(inside_board((9, 8)))
        self.assertFalse(inside_board((-1, 0)))
        self.assertFalse(inside_board((10, 4)))
        self.assertTrue(inside_palace(Side.BLACK, (1, 4)))
        self.assertTrue(inside_palace(Side.RED, (8, 4)))
        self.assertFalse(inside_palace(Side.RED, (6, 4)))


if __name__ == "__main__":
    unittest.main()
