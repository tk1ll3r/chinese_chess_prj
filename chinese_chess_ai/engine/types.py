from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

Position = tuple[int, int]


class Side(str, Enum):
    RED = "red"
    BLACK = "black"

    def opponent(self) -> "Side":
        return Side.BLACK if self is Side.RED else Side.RED


class PieceKind(str, Enum):
    GENERAL = "general"
    ADVISOR = "advisor"
    ELEPHANT = "elephant"
    HORSE = "horse"
    CHARIOT = "chariot"
    CANNON = "cannon"
    SOLDIER = "soldier"


_SIDE_CODE = {
    Side.RED: "R",
    Side.BLACK: "B",
}

_KIND_CODE = {
    PieceKind.GENERAL: "G",
    PieceKind.ADVISOR: "A",
    PieceKind.ELEPHANT: "E",
    PieceKind.HORSE: "H",
    PieceKind.CHARIOT: "R",
    PieceKind.CANNON: "C",
    PieceKind.SOLDIER: "S",
}


@dataclass(frozen=True, slots=True)
class Piece:
    side: Side
    kind: PieceKind

    def short_code(self) -> str:
        return f"{_SIDE_CODE[self.side]}{_KIND_CODE[self.kind]}"

