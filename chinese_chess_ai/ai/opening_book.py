from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..engine.state import GameState
from ..engine.moves import Move


class OpeningBook:
    """Simple opening book for Chinese Chess."""

    def __init__(self, book_path: str | Path | None = None):
        self.book: Dict[str, List[tuple[str, float]]] = {}
        if book_path is None:
            book_path = Path(__file__).parent.parent.parent / "data" / "opening_book.json"
        self.book_path = Path(book_path)
        self._load_book()

    def _load_book(self) -> None:
        """Load opening book from JSON file."""
        if not self.book_path.exists():
            return
        try:
            with open(self.book_path, "r", encoding="utf-8") as f:
                self.book = json.load(f)
        except Exception:
            self.book = {}

    def _position_key(self, state: GameState) -> str:
        """Generate a unique key for the current position."""
        board_str = ""
        for row in state.board:
            for piece in row:
                if piece is None:
                    board_str += "."
                else:
                    side_char = "R" if piece.side.name == "RED" else "B"
                    kind_char = piece.kind.name[0]
                    board_str += f"{side_char}{kind_char}"
        return board_str + f"_{state.side_to_move.name}"

    def get_book_move(self, state: GameState) -> Move | None:
        """Get a move from the opening book if available."""
        key = self._position_key(state)
        if key not in self.book:
            return None

        # Get moves with weights
        moves_data = self.book[key]
        if not moves_data:
            return None

        # For now, just return the first (best) move
        # In future, could use weighted random selection
        move_str, _weight = moves_data[0]
        return self._parse_move(move_str)

    def _parse_move(self, move_str: str) -> Move | None:
        """Parse move string like '(0,3)-(2,3)' into Move object."""
        try:
            parts = move_str.split("-")
            start_str = parts[0].strip("()")
            end_str = parts[1].strip("()")
            start_row, start_col = map(int, start_str.split(","))
            end_row, end_col = map(int, end_str.split(","))
            return Move(start=(start_row, start_col), end=(end_row, end_col))
        except Exception:
            return None

    def add_position(self, state: GameState, move: Move, weight: float = 1.0) -> None:
        """Add a position and move to the opening book."""
        key = self._position_key(state)
        move_str = f"({move.start[0]},{move.start[1]})-({move.end[0]},{move.end[1]})"

        if key not in self.book:
            self.book[key] = []

        # Check if move already exists
        for i, (existing_move, existing_weight) in enumerate(self.book[key]):
            if existing_move == move_str:
                # Update weight
                self.book[key][i] = (move_str, existing_weight + weight)
                return

        # Add new move
        self.book[key].append((move_str, weight))
        # Sort by weight (descending)
        self.book[key].sort(key=lambda x: x[1], reverse=True)

    def save_book(self) -> None:
        """Save opening book to JSON file."""
        self.book_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.book_path, "w", encoding="utf-8") as f:
            json.dump(self.book, f, indent=2, ensure_ascii=False)
