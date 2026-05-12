from __future__ import annotations

import threading
from typing import Callable

from ..engine.moves import Move
from .client import LanGameClient
from .discovery import LanRoomBroadcaster, RoomDiscoveryError, claim_room_code, discover_room
from .server import LanGameServer
from .transports import ClientTransport, HostTransport

StateCallback = Callable[[dict], None]
TextCallback = Callable[[str], None]
RoomCallback = Callable[[str], None]


class LanRoomHostTransport(HostTransport):
    def __init__(
        self,
        room_code: str | None = None,
        tcp_port: int = 0,
        on_state: StateCallback | None = None,
        on_status: TextCallback | None = None,
        on_error: TextCallback | None = None,
        on_room_code: RoomCallback | None = None,
    ) -> None:
        self._requested_room_code = room_code
        self._room_code = ""
        self._tcp_port = tcp_port
        self._on_state = on_state
        self._on_status = on_status
        self._on_error = on_error
        self._on_room_code = on_room_code
        self._server: LanGameServer | None = None
        self._broadcaster: LanRoomBroadcaster | None = None

    @property
    def room_code(self) -> str:
        return self._room_code

    def start(self) -> None:
        self._room_code = claim_room_code(self._requested_room_code or None)
        self._server = LanGameServer(
            port=self._tcp_port,
            on_state=self._on_state,
            on_status=self._on_status,
            on_error=self._on_error,
        )
        self._server.start()
        self._broadcaster = LanRoomBroadcaster(
            room_code=self._room_code,
            tcp_port=self._server.port,
        )
        self._broadcaster.start()
        if self._on_room_code is not None:
            self._on_room_code(self._room_code)
        if self._on_status is not None:
            self._on_status(f"Room created. Share code: {self._room_code}")

    def submit_local_move(self, move: Move) -> tuple[bool, str]:
        if self._server is None:
            return False, "Room is not ready."
        return self._server.submit_local_move(move)

    def close(self) -> None:
        if self._broadcaster is not None:
            self._broadcaster.stop()
            self._broadcaster = None
        if self._server is not None:
            self._server.stop()
            self._server = None


class LanRoomClientTransport(ClientTransport):
    def __init__(
        self,
        room_code: str,
        on_message: TextCallback | None = None,
        on_status: TextCallback | None = None,
        on_error: TextCallback | None = None,
    ) -> None:
        self.room_code = room_code
        self._on_message = on_message
        self._on_status = on_status
        self._on_error = on_error
        self._client: LanGameClient | None = None
        self._thread: threading.Thread | None = None
        self._closed = False

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._connect_worker, daemon=True)
        self._thread.start()

    def send_move(self, move: Move) -> None:
        if self._client is None:
            if self._on_error is not None:
                self._on_error("Not connected to a room yet.")
            return
        self._client.send_move(move)

    def close(self) -> None:
        self._closed = True
        if self._client is not None:
            self._client.close()
            self._client = None

    def _connect_worker(self) -> None:
        try:
            if self._on_status is not None:
                self._on_status(f"Searching for room {self.room_code} on the LAN...")
            announcement = discover_room(self.room_code)
            if self._closed:
                return
            self._client = LanGameClient(
                on_message=self._on_message,
                on_status=self._on_status,
                on_error=self._on_error,
            )
            self._client.connect(announcement.source_ip, announcement.tcp_port)
        except RoomDiscoveryError as exc:
            if self._on_error is not None:
                self._on_error(str(exc))
        except OSError as exc:
            if self._on_error is not None:
                self._on_error(f"Could not connect to the room host: {exc}")
