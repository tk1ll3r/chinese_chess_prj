from __future__ import annotations

import socket
import threading
from dataclasses import dataclass
from typing import Callable

from ..engine.moves import Move
from ..engine.rules import generate_legal_moves
from ..engine.state import GameState
from ..engine.types import Piece, PieceKind, Side
from .protocol import decode_message, encode_message, move_from_payload, serialize_state

NetworkCallback = Callable[[dict], None]
TextCallback = Callable[[str], None]

_PIECE_CODE = {
    PieceKind.GENERAL: "K",
    PieceKind.ADVISOR: "A",
    PieceKind.ELEPHANT: "B",
    PieceKind.HORSE: "N",
    PieceKind.CHARIOT: "R",
    PieceKind.CANNON: "C",
    PieceKind.SOLDIER: "P",
}


@dataclass(slots=True)
class _ClientSlot:
    conn: socket.socket
    address: tuple[str, int]
    side: Side


class LanGameServer:
    """Authoritative TCP server for a small two-player LAN game."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        on_state: NetworkCallback | None = None,
        on_status: TextCallback | None = None,
        on_error: TextCallback | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.on_state = on_state
        self.on_status = on_status
        self.on_error = on_error
        self.state = GameState.initial()
        self.move_history: list[str] = []
        self.captured_by_red: list[str] = []
        self.captured_by_black: list[str] = []
        self._server_socket: socket.socket | None = None
        self._clients: list[_ClientSlot] = []
        self._lock = threading.RLock()
        self._running = False
        self._accept_thread: threading.Thread | None = None

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            self.port = int(server_socket.getsockname()[1])
            self._server_socket = server_socket
            self._running = True

        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()
        self._emit_status("Host room is ready. Waiting for another player to join.")
        self._emit_state("Host room started")

    def stop(self) -> None:
        with self._lock:
            self._running = False
            sockets = [slot.conn for slot in self._clients]
            self._clients.clear()
            if self._server_socket is not None:
                sockets.append(self._server_socket)
                self._server_socket = None
        for sock in sockets:
            try:
                sock.close()
            except OSError:
                pass

    def submit_local_move(self, move: Move) -> tuple[bool, str]:
        return self._submit_move(move, Side.RED)

    def _accept_loop(self) -> None:
        while self._running:
            try:
                assert self._server_socket is not None
                conn, address = self._server_socket.accept()
            except OSError:
                return

            with self._lock:
                if len(self._clients) >= 1:
                    try:
                        conn.sendall(encode_message("error", {"message": "The room is already full."}))
                    finally:
                        conn.close()
                    continue
                slot = _ClientSlot(conn=conn, address=address, side=Side.BLACK)
                self._clients.append(slot)

            self._send(slot, "hello", {"side": slot.side.value, "host_side": Side.RED.value})
            self._send(slot, "state", self._state_payload("Guest joined the room."))
            self._emit_status("Guest joined the room.")
            threading.Thread(target=self._client_loop, args=(slot,), daemon=True).start()

    def _client_loop(self, slot: _ClientSlot) -> None:
        try:
            reader = slot.conn.makefile("rb")
            for line in reader:
                try:
                    message = decode_message(line)
                    self._handle_client_message(slot, message)
                except Exception as exc:
                    self._send(slot, "error", {"message": str(exc)})
        except OSError:
            pass
        finally:
            with self._lock:
                self._clients = [client for client in self._clients if client is not slot]
            try:
                slot.conn.close()
            except OSError:
                pass
            self._emit_status("Guest disconnected from the room.")

    def _handle_client_message(self, slot: _ClientSlot, message: dict) -> None:
        if message["type"] != "move":
            self._send(slot, "error", {"message": "Unsupported LAN message"})
            return
        move = move_from_payload(message["payload"])
        ok, detail = self._submit_move(move, slot.side)
        if not ok:
            self._send(slot, "error", {"message": detail})

    def _submit_move(self, move: Move, side: Side) -> tuple[bool, str]:
        with self._lock:
            if self.state.side_to_move is not side:
                return False, "It is not your turn."

            legal_lookup = {(legal.start, legal.end): legal for legal in generate_legal_moves(self.state)}
            selected_move = legal_lookup.get((move.start, move.end))
            if selected_move is None:
                return False, "That move is not legal."

            captured_piece = self.state.piece_at(selected_move.end)
            self.state.make_move(selected_move)
            self._record_move(side, selected_move, captured_piece)
            payload = self._state_payload("Board synchronized")

        self._broadcast("state", payload)
        self._emit_state("Board synchronized")
        return True, "OK"

    def _record_move(self, side: Side, move: Move, captured_piece: Piece | None) -> None:
        move_number = len(self.move_history) + 1
        capture_text = ""
        if captured_piece is not None:
            captured_code = _piece_display_code(captured_piece)
            capture_text = f" x {captured_code}"
            if side is Side.RED:
                self.captured_by_red.append(captured_code)
            else:
                self.captured_by_black.append(captured_code)
        self.move_history.append(
            f"{move_number}. {_side_label(side)}: ({move.start[0]},{move.start[1]}) -> "
            f"({move.end[0]},{move.end[1]}){capture_text}"
        )

    def _state_payload(self, status: str) -> dict:
        return serialize_state(
            self.state,
            move_history=self.move_history,
            captured_by_red=self.captured_by_red,
            captured_by_black=self.captured_by_black,
            status=status,
        )

    def _broadcast(self, message_type: str, payload: dict) -> None:
        with self._lock:
            clients = list(self._clients)
        for slot in clients:
            self._send(slot, message_type, payload)

    def _send(self, slot: _ClientSlot, message_type: str, payload: dict) -> None:
        try:
            slot.conn.sendall(encode_message(message_type, payload))
        except OSError:
            self._emit_error("Could not send LAN data to the client.")

    def _emit_state(self, status: str) -> None:
        if self.on_state is not None:
            self.on_state(self._state_payload(status))

    def _emit_status(self, message: str) -> None:
        if self.on_status is not None:
            self.on_status(message)

    def _emit_error(self, message: str) -> None:
        if self.on_error is not None:
            self.on_error(message)


def _piece_display_code(piece: Piece) -> str:
    side_prefix = "R" if piece.side is Side.RED else "B"
    return f"{side_prefix}{_PIECE_CODE[piece.kind]}"


def _side_label(side: Side) -> str:
    return "Red" if side is Side.RED else "Black"
