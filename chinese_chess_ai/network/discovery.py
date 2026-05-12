from __future__ import annotations

import json
import socket
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Iterable

from .room_code import generate_room_code, normalize_room_code

DISCOVERY_PORT = 38561
ANNOUNCE_INTERVAL_SECONDS = 1.0
ROOM_TTL_SECONDS = 4.0
LOOKUP_TIMEOUT_SECONDS = 4.0
GAME_NAME = "ChineseChess"


class RoomDiscoveryError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RoomAnnouncement:
    room_code: str
    game_name: str
    tcp_port: int
    room_id: str
    host_name: str
    source_ip: str
    observed_at: float


def make_room_announcement(
    room_code: str,
    tcp_port: int,
    room_id: str,
    host_name: str,
    source_ip: str = "",
    observed_at: float = 0.0,
) -> RoomAnnouncement:
    return RoomAnnouncement(
        room_code=normalize_room_code(room_code),
        game_name=GAME_NAME,
        tcp_port=int(tcp_port),
        room_id=room_id,
        host_name=host_name,
        source_ip=source_ip,
        observed_at=observed_at,
    )


def encode_announcement(announcement: RoomAnnouncement) -> bytes:
    payload = {
        "room_code": announcement.room_code,
        "game_name": announcement.game_name,
        "tcp_port": announcement.tcp_port,
        "room_id": announcement.room_id,
        "host_name": announcement.host_name,
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def decode_announcement(
    packet: bytes,
    source_ip: str,
    observed_at: float | None = None,
) -> RoomAnnouncement:
    payload = json.loads(packet.decode("utf-8"))
    return RoomAnnouncement(
        room_code=normalize_room_code(payload["room_code"]),
        game_name=str(payload["game_name"]),
        tcp_port=int(payload["tcp_port"]),
        room_id=str(payload["room_id"]),
        host_name=str(payload.get("host_name", "")),
        source_ip=source_ip,
        observed_at=time.monotonic() if observed_at is None else observed_at,
    )


def select_room_candidate(
    room_code: str,
    announcements: Iterable[RoomAnnouncement],
    now: float,
    ttl_seconds: float = ROOM_TTL_SECONDS,
) -> RoomAnnouncement:
    normalized_code = normalize_room_code(room_code)
    active_by_room_id: dict[str, RoomAnnouncement] = {}
    for announcement in announcements:
        if announcement.game_name != GAME_NAME or announcement.room_code != normalized_code:
            continue
        if now - announcement.observed_at > ttl_seconds:
            continue
        current = active_by_room_id.get(announcement.room_id)
        if current is None or announcement.observed_at > current.observed_at:
            active_by_room_id[announcement.room_id] = announcement

    if not active_by_room_id:
        raise RoomDiscoveryError("Room not found. The code may be wrong or the room may have expired.")
    if len(active_by_room_id) > 1:
        raise RoomDiscoveryError("More than one LAN room is using this code right now.")
    return next(iter(active_by_room_id.values()))


def claim_room_code(
    preferred_code: str | None = None,
    attempts: int = 20,
    probe_seconds: float = 0.35,
) -> str:
    for _ in range(attempts):
        room_code = normalize_room_code(preferred_code) if preferred_code else generate_room_code()
        if not _detect_collision(room_code, probe_seconds):
            return room_code
        if preferred_code is not None:
            break
    raise RoomDiscoveryError("Could not allocate a unique room code on this LAN.")


def discover_room(
    room_code: str,
    timeout_seconds: float = LOOKUP_TIMEOUT_SECONDS,
    discovery_port: int = DISCOVERY_PORT,
) -> RoomAnnouncement:
    announcements: list[RoomAnnouncement] = []
    listener = _create_listener_socket(discovery_port)
    deadline = time.monotonic() + timeout_seconds
    try:
        while time.monotonic() < deadline:
            listener.settimeout(min(0.25, max(0.01, deadline - time.monotonic())))
            try:
                packet, address = listener.recvfrom(4096)
            except socket.timeout:
                continue
            try:
                announcements.append(
                    decode_announcement(
                        packet,
                        source_ip=address[0],
                        observed_at=time.monotonic(),
                    )
                )
            except Exception:
                continue
    finally:
        listener.close()

    return select_room_candidate(room_code, announcements, now=time.monotonic())


class LanRoomBroadcaster:
    def __init__(
        self,
        room_code: str,
        tcp_port: int,
        room_id: str | None = None,
        discovery_port: int = DISCOVERY_PORT,
    ) -> None:
        self.room_code = normalize_room_code(room_code)
        self.tcp_port = int(tcp_port)
        self.room_id = room_id or uuid.uuid4().hex
        self.discovery_port = discovery_port
        self.host_name = socket.gethostname()
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _broadcast_loop(self) -> None:
        payload = encode_announcement(
            make_room_announcement(
                room_code=self.room_code,
                tcp_port=self.tcp_port,
                room_id=self.room_id,
                host_name=self.host_name,
            )
        )
        broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            while self._running:
                try:
                    broadcaster.sendto(payload, ("255.255.255.255", self.discovery_port))
                except OSError:
                    return
                time.sleep(ANNOUNCE_INTERVAL_SECONDS)
        finally:
            broadcaster.close()


def _detect_collision(room_code: str, probe_seconds: float) -> bool:
    listener = _create_listener_socket(DISCOVERY_PORT)
    deadline = time.monotonic() + probe_seconds
    try:
        while time.monotonic() < deadline:
            listener.settimeout(min(0.15, max(0.01, deadline - time.monotonic())))
            try:
                packet, address = listener.recvfrom(4096)
            except socket.timeout:
                continue
            try:
                announcement = decode_announcement(
                    packet,
                    source_ip=address[0],
                    observed_at=time.monotonic(),
                )
            except Exception:
                continue
            if announcement.room_code == room_code and announcement.game_name == GAME_NAME:
                return True
        return False
    finally:
        listener.close()


def _create_listener_socket(discovery_port: int) -> socket.socket:
    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("", discovery_port))
    return listener
