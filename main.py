from chinese_chess_ai.ai.evaluate import material_score
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.engine.types import Side


def main() -> None:
    state = GameState.initial()
    print("Chinese Chess Project - Week 1 Scaffold")
    print()
    print(state.render_ascii())
    print()
    print(f"Pieces on board: {state.count_pieces()}")
    print(f"Side to move: {state.side_to_move.value}")
    print(f"Material score from red perspective: {material_score(state, Side.RED)}")


if __name__ == "__main__":
    main()
