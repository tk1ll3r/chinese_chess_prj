from __future__ import annotations

from abc import ABC, abstractmethod

from ..engine.moves import Move


class NetworkTransport(ABC):
    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class HostTransport(NetworkTransport, ABC):
    @property
    @abstractmethod
    def room_code(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def submit_local_move(self, move: Move) -> tuple[bool, str]:
        raise NotImplementedError


class ClientTransport(NetworkTransport, ABC):
    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def send_move(self, move: Move) -> None:
        raise NotImplementedError
