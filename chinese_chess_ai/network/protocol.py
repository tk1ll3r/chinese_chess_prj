from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from ..engine.moves import Move
from ..engine.state import Board, GameState
from ..engine.types import Piece, PieceKind, Side

PROTOCOL_VERSION = 1


@dataclass(frozen=True, slots=True)
class NetworkState:
    state: GameState
    move_history: tuple[str, ...]
    captured_by_red: tuple[str, ...]
    captured_by_black: tuple[str, ...]
    status: str = ""


def piece_to_payload(piece: Piece | None) -> dict[str, str] | None:
    if piece is None:
        return None
    return {"side": piece.side.value, "kind": piece.kind.value}


def piece_from_payload(payload: dict[str, str] | None) -> Piece | None:
    if payload is None:
        return None
    return Piece(side=Side(payload["side"]), kind=PieceKind(payload["kind"]))


def move_to_payload(move: Move) -> dict[str, list[int]]:
    return {
        "start": [move.start[0], move.start[1]],
        "end": [move.end[0], move.end[1]],
    }


def move_from_payload(payload: dict[str, Any]) -> Move:
    start = payload["start"]
    end = payload["end"]
    return Move(start=(int(start[0]), int(start[1])), end=(int(end[0]), int(end[1])))


def serialize_state(
    state: GameState,
    move_history: list[str] | tuple[str, ...] | None = None,
    captured_by_red: list[str] | tuple[str, ...] | None = None,
    captured_by_black: list[str] | tuple[str, ...] | None = None,
    status: str = "",
) -> dict[str, Any]:
    return {
        "version": PROTOCOL_VERSION,
        "board": [[piece_to_payload(piece) for piece in row] for row in state.board],
        "side_to_move": state.side_to_move.value,
        "red_general_position": list(state.red_general_position),
        "black_general_position": list(state.black_general_position),
        "move_history": list(move_history or ()),
        "captured_by_red": list(captured_by_red or ()),
        "captured_by_black": list(captured_by_black or ()),
        "status": status,
    }


def deserialize_state(payload: dict[str, Any]) -> NetworkState:
    board: Board = []
    for row in payload["board"]:
        board.append([piece_from_payload(piece_payload) for piece_payload in row])

    red_general = tuple(payload["red_general_position"])
    black_general = tuple(payload["black_general_position"])
    state = GameState(
        board=board,
        side_to_move=Side(payload["side_to_move"]),
        red_general_position=(int(red_general[0]), int(red_general[1])),
        black_general_position=(int(black_general[0]), int(black_general[1])),
    )
    return NetworkState(
        state=state,
        move_history=tuple(str(item) for item in payload.get("move_history", ())),
        captured_by_red=tuple(str(item) for item in payload.get("captured_by_red", ())),
        captured_by_black=tuple(str(item) for item in payload.get("captured_by_black", ())),
        status=str(payload.get("status", "")),
    )


def encode_message(message_type: str, payload: dict[str, Any] | None = None) -> bytes:
    message = {
        "version": PROTOCOL_VERSION,
        "type": message_type,
        "payload": payload or {},
    }
    return (json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8")


def decode_message(raw_line: bytes | str) -> dict[str, Any]:
    if isinstance(raw_line, bytes):
        raw_line = raw_line.decode("utf-8")
    message = json.loads(raw_line)
    if int(message.get("version", 0)) != PROTOCOL_VERSION:
        raise ValueError("Unsupported LAN protocol version")
    if "type" not in message:
        raise ValueError("LAN message is missing a type")
    return message

