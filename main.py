from __future__ import annotations

import sys

from chinese_chess_ai.ai.evaluate import evaluate_position, material_score
from chinese_chess_ai.ai.search import SearchConfig, choose_move
from chinese_chess_ai.engine.rules import generate_legal_moves, is_in_check
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.engine.types import Piece, Position, Side


def print_engine_summary() -> None:
    state = GameState.initial()
    legal_moves = generate_legal_moves(state)
    print("Thuong DSA Engine Summary")
    print()
    print(state.render_ascii())
    print()
    print(f"Pieces on board: {state.count_pieces()}")
    print(f"Side to move: {state.side_to_move.value}")
    print(f"Material score from red perspective: {material_score(state, Side.RED)}")
    print(f"Evaluation for side to move: {evaluate_position(state)}")
    print(f"Red in check: {is_in_check(state, Side.RED)}")
    print(f"Black in check: {is_in_check(state, Side.BLACK)}")
    print(f"Legal opening moves: {len(legal_moves)}")


def format_move(move: Position | tuple[Position, Position] | object) -> str:
    if hasattr(move, "start") and hasattr(move, "end"):
        start = getattr(move, "start")
        end = getattr(move, "end")
    else:
        start, end = move  # type: ignore[misc]
    return f"({start[0]},{start[1]}) -> ({end[0]},{end[1]})"


def parse_move_input(raw: str) -> tuple[Position, Position] | None:
    cleaned = raw.replace("->", " ").replace(",", " ").replace("-", " ")
    parts = cleaned.split()
    if len(parts) != 4 or not all(part.isdigit() for part in parts):
        return None
    start = (int(parts[0]), int(parts[1]))
    end = (int(parts[2]), int(parts[3]))
    return start, end


def prompt_mode() -> tuple[str, Side | None, SearchConfig | None]:
    print("Select mode:")
    print("  1. Engine summary")
    print("  2. Two-player CLI")
    print("  3. Play vs AI")
    print("  4. Thuong DSA GUI")

    while True:
        choice = input("Mode [1/2/3/4]: ").strip() or "1"
        if choice == "1":
            return "summary", None, None
        if choice == "2":
            return "pvp", None, None
        if choice == "3":
            human_side = prompt_side()
            return "ai", human_side.opponent(), prompt_difficulty()
        if choice == "4":
            return "gui", None, None
        print("Please choose 1, 2, 3, or 4.")


def prompt_side() -> Side:
    while True:
        raw = input("Play as [red/black] (default: red): ").strip().lower()
        if raw in {"", "red", "r"}:
            return Side.RED
        if raw in {"black", "b"}:
            return Side.BLACK
        print("Please enter red or black.")


def prompt_difficulty() -> SearchConfig:
    print("Difficulty:")
    print("  1. easy   (depth 1)")
    print("  2. medium (depth 2)")
    print("  3. hard   (depth 3)")

    while True:
        raw = input("Difficulty [1/2/3] (default: 2): ").strip() or "2"
        if raw == "1":
            return SearchConfig(depth=1, use_alpha_beta=True)
        if raw == "2":
            return SearchConfig(depth=2, use_alpha_beta=True)
        if raw == "3":
            return SearchConfig(depth=3, use_alpha_beta=True)
        print("Please choose 1, 2, or 3.")


def print_help(ai_enabled: bool) -> None:
    print("Commands:")
    print("  6 0 5 0        move using row/col coordinates")
    print("  6,0 5,0        same move with commas")
    print("  6,0->5,0       same move with arrow")
    print("  moves          list legal moves")
    print("  undo           undo the last move")
    print("  help           show commands")
    print("  quit           exit the game")
    if ai_enabled:
        print("  In AI mode, undo removes both the AI move and your last move when possible.")


def print_legal_moves(state: GameState, legal_moves: list[object]) -> None:
    print(f"Legal moves for {state.side_to_move.value}:")
    for index, move in enumerate(legal_moves, start=1):
        print(f"  {index:>2}. {format_move(move)}")


def describe_capture(piece: Piece | None) -> str:
    if piece is None:
        return ""
    return f" capturing {piece.short_code()}"


def undo_moves(state: GameState, count: int) -> None:
    undone = 0
    for _ in range(count):
        move = state.undo_move()
        if move is None:
            break
        undone += 1
    if undone == 0:
        print("No moves to undo.")
    else:
        print(f"Undid {undone} move(s).")


def play_cli(ai_side: Side | None = None, search_config: SearchConfig | None = None) -> None:
    state = GameState.initial()
    ai_enabled = ai_side is not None
    print_help(ai_enabled)

    while True:
        legal_moves = generate_legal_moves(state)
        print()
        print(render_board(state))
        print(f"Side to move: {state.side_to_move.value}")
        if is_in_check(state, state.side_to_move):
            print(f"{state.side_to_move.value} is currently in check.")
        print(f"Legal moves available: {len(legal_moves)}")

        if not legal_moves:
            winner = state.side_to_move.opponent()
            print(f"No legal moves remain. Winner: {winner.value}")
            return

        if ai_enabled and state.side_to_move is ai_side:
            ai_move = choose_move(state, search_config)
            if ai_move is None:
                print("AI found no legal move.")
                return
            captured_piece = state.piece_at(ai_move.end)
            print(f"AI plays {format_move(ai_move)}{describe_capture(captured_piece)}")
            state.make_move(ai_move)
            continue

        raw = input("Enter move or command: ").strip()
        command = raw.lower()

        if command in {"quit", "exit"}:
            print("Exiting game.")
            return
        if command == "help":
            print_help(ai_enabled)
            continue
        if command == "moves":
            print_legal_moves(state, legal_moves)
            continue
        if command == "undo":
            undo_moves(state, 2 if ai_enabled else 1)
            continue

        parsed = parse_move_input(raw)
        if parsed is None:
            print("Invalid input. Use 'row col row col' or type 'help'.")
            continue

        legal_lookup = {(move.start, move.end): move for move in legal_moves}
        selected_move = legal_lookup.get(parsed)
        if selected_move is None:
            print("That move is not legal in the current position. Type 'moves' to list options.")
            continue

        captured_piece = state.piece_at(selected_move.end)
        print(f"Played {format_move(selected_move)}{describe_capture(captured_piece)}")
        state.make_move(selected_move)


def main() -> None:
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "summary":
            print_engine_summary()
            return
        if command == "cli":
            play_cli()
            return
        if command == "ai":
            play_cli(ai_side=Side.BLACK, search_config=SearchConfig(depth=2, use_alpha_beta=True))
            return
        if command == "gui":
            from chinese_chess_ai.gui.tk_gui import launch_gui

            launch_gui()
            return
        if command == "menu":
            mode, ai_side, search_config = prompt_mode()
            if mode == "summary":
                print_engine_summary()
                return
            if mode == "pvp":
                play_cli()
                return
            if mode == "gui":
                from chinese_chess_ai.gui.tk_gui import launch_gui

                launch_gui()
                return
            play_cli(ai_side=ai_side, search_config=search_config)
            return

    if sys.stdin is not None and not sys.stdin.isatty():
        print_engine_summary()
        return

    from chinese_chess_ai.gui.tk_gui import launch_gui

    launch_gui()


if __name__ == "__main__":
    main()
