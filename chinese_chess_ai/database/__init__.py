from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from ..engine.state import GameState
from ..engine.types import Side


@dataclass
class GameRecord:
    """Record of a complete game."""
    red_player: str
    black_player: str
    moves: List[str]  # Move strings in format "(r,c)-(r,c)"
    result: str  # "Red wins", "Black wins", "Draw"
    date: str
    event: str = ""


class GameDatabase:
    """Simple game database for saving/loading games."""

    def __init__(self, db_dir: str | Path | None = None):
        if db_dir is None:
            db_dir = Path(__file__).parent.parent.parent / "data" / "games"
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(parents=True, exist_ok=True)

    def save_game(self, record: GameRecord) -> str:
        """Save a game record to file. Returns filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_{timestamp}.txt"
        filepath = self.db_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"[Event \"{record.event}\"]\n")
            f.write(f"[Date \"{record.date}\"]\n")
            f.write(f"[Red \"{record.red_player}\"]\n")
            f.write(f"[Black \"{record.black_player}\"]\n")
            f.write(f"[Result \"{record.result}\"]\n")
            f.write("\n")
            for i, move in enumerate(record.moves, 1):
                f.write(f"{i}. {move}\n")

        return filename

    def load_game(self, filename: str) -> GameRecord | None:
        """Load a game record from file."""
        filepath = self.db_dir / filename
        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse headers
            red_player = ""
            black_player = ""
            result = ""
            date_str = ""
            event = ""
            moves = []

            for line in lines:
                line = line.strip()
                if line.startswith("[Red"):
                    red_player = line.split('"')[1]
                elif line.startswith("[Black"):
                    black_player = line.split('"')[1]
                elif line.startswith("[Result"):
                    result = line.split('"')[1]
                elif line.startswith("[Date"):
                    date_str = line.split('"')[1]
                elif line.startswith("[Event"):
                    event = line.split('"')[1]
                elif line and not line.startswith("["):
                    # Parse move
                    parts = line.split(". ", 1)
                    if len(parts) == 2:
                        moves.append(parts[1])

            return GameRecord(
                red_player=red_player,
                black_player=black_player,
                moves=moves,
                result=result,
                date=date_str,
                event=event,
            )
        except Exception:
            return None

    def list_games(self) -> List[str]:
        """List all saved games."""
        return sorted([f.name for f in self.db_dir.glob("game_*.txt")], reverse=True)
