from __future__ import annotations

import socket
import threading
from typing import Callable

from ..engine.moves import Move
from .protocol import decode_message, encode_message, move_to_payload

MessageCallback = Callable[[dict], None]
TextCallback = Callable[[str], None]


class LanGameClient:
    """Small TCP client used by the Tkinter LAN MVP."""

    def __init__(
        self,
        on_message: MessageCallback | None = None,
        on_status: TextCallback | None = None,
        on_error: TextCallback | None = None,
    ) -> None:
        self.on_message = on_message
        self.on_status = on_status
        self.on_error = on_error
        self._socket: socket.socket | None = None
        self._reader_thread: threading.Thread | None = None
        self._running = False

    def connect(self, host: str, port: int) -> None:
        if self._running:
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self._socket = sock
        self._running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()
        self._emit_status("Connected to the room host.")

    def send_move(self, move: Move) -> None:
        if self._socket is None:
            self._emit_error("LAN client is not connected.")
            return
        try:
            self._socket.sendall(encode_message("move", move_to_payload(move)))
        except OSError as exc:
            self._emit_error(f"Could not send LAN move: {exc}")

    def close(self) -> None:
        self._running = False
        if self._socket is None:
            return
        try:
            self._socket.close()
        except OSError:
            pass
        self._socket = None

    def _read_loop(self) -> None:
        assert self._socket is not None
        try:
            reader = self._socket.makefile("rb")
            for line in reader:
                if not self._running:
                    break
                try:
                    message = decode_message(line)
                except Exception as exc:
                    self._emit_error(str(exc))
                    continue
                if self.on_message is not None:
                    self.on_message(message)
        except OSError:
            pass
        finally:
            self._running = False
            self._emit_status("Disconnected from LAN host.")

    def _emit_status(self, message: str) -> None:
        if self.on_status is not None:
            self.on_status(message)

    def _emit_error(self, message: str) -> None:
        if self.on_error is not None:
            self.on_error(message)
