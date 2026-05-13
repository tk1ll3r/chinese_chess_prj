from __future__ import annotations

import os
import select
import subprocess
import threading

from ..engine.moves import Move
from ..engine.rules import generate_legal_moves
from ..engine.state import GameState
from ..engine.types import PieceKind, Side

PIECE_TO_FEN = {
    PieceKind.GENERAL: "k",
    PieceKind.ADVISOR: "a",
    PieceKind.ELEPHANT: "b",
    PieceKind.HORSE: "n",
    PieceKind.CHARIOT: "r",
    PieceKind.CANNON: "c",
    PieceKind.SOLDIER: "p",
}


def _state_to_fen(state: GameState) -> str:
    rows = []
    for row in range(10):
        empty = 0
        fen_row = []
        for col in range(9):
            piece = state.board[row][col]
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    fen_row.append(str(empty))
                    empty = 0
                char = PIECE_TO_FEN[piece.kind]
                if piece.side is Side.RED:
                    char = char.upper()
                fen_row.append(char)
        if empty > 0:
            fen_row.append(str(empty))
        rows.append("".join(fen_row))
    board_fen = "/".join(rows)
    side = "w" if state.side_to_move is Side.RED else "b"
    return f"{board_fen} {side} - - 0 1"


def _to_uci_square(row: int, col: int) -> str:
    return chr(ord("a") + col) + chr(ord("0") + (9 - row))


def _move_to_uci(move: Move) -> str:
    return _to_uci_square(*move.start) + _to_uci_square(*move.end)


def _uci_to_move(uci: str) -> Move:
    return Move(
        start=(9 - (ord(uci[1]) - ord("0")), ord(uci[0]) - ord("a")),
        end=(9 - (ord(uci[3]) - ord("0")), ord(uci[2]) - ord("a")),
    )


_ENGINE_PATH = os.path.join(os.path.dirname(__file__), "engines", "pikafish")


class PikafishEngine:
    def __init__(self, engine_path: str | None = None):
        self._lock = threading.Lock()
        self._engine_path = engine_path or _ENGINE_PATH
        self._process: subprocess.Popen | None = None
        self._stdout_fd: int | None = None
        self._read_buf = b""
        self._start()

    def _start(self):
        self._process = subprocess.Popen(
            [self._engine_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        self._stdout_fd = self._process.stdout.fileno()
        self._init_uci()

    def _send(self, cmd: str):
        self._process.stdin.write((cmd + "\n").encode())
        self._process.stdin.flush()

    def _read_line(self, timeout: float = 30) -> str | None:
        while b"\n" not in self._read_buf:
            r, _, _ = select.select([self._stdout_fd], [], [], timeout)
            if not r:
                return None
            chunk = os.read(self._stdout_fd, 4096)
            if not chunk:
                return None
            self._read_buf += chunk
        line, self._read_buf = self._read_buf.split(b"\n", 1)
        return line.decode().strip()

    def _recv_until(self, target: str, timeout: float = 10):
        while True:
            line = self._read_line(timeout=timeout)
            if line is None:
                raise TimeoutError(f"Timed out waiting for '{target}'")
            if line == target:
                break

    def _drain(self):
        while True:
            r, _, _ = select.select([self._stdout_fd], [], [], 0.01)
            if not r:
                break
            chunk = os.read(self._stdout_fd, 4096)
            if not chunk:
                break
            self._read_buf += chunk
        if b"\n" in self._read_buf:
            lines = self._read_buf.split(b"\n")
            self._read_buf = lines[-1]

    def _init_uci(self):
        self._send("uci")
        self._recv_until("uciok")
        self._send("setoption name Threads value 1")
        self._send("setoption name Hash value 16")
        nnue_path = os.path.join(os.path.dirname(self._engine_path), "pikafish.nnue")
        nnue_path = os.path.normpath(nnue_path)
        self._send(f'setoption name EvalFile value {nnue_path}')
        self._send("isready")
        self._recv_until("readyok")

    def choose_move(
        self,
        state: GameState,
        depth: int = 5,
        time_limit: float | None = None,
    ) -> Move | None:
        with self._lock:
            self._read_buf = b""
            self._send("ucinewgame")
            self._drain()
            fen = _state_to_fen(state)
            self._send(f"position fen {fen}")

            if time_limit is not None:
                self._send(f"go movetime {int(time_limit * 1000)}")
                timeout = time_limit + 5
            else:
                self._send(f"go depth {depth}")
                timeout = 60

            best_uci = None
            while True:
                line = self._read_line(timeout=timeout)
                if line is None:
                    break
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] != "(none)":
                        best_uci = parts[1]
                    break

            if best_uci is None:
                legal = generate_legal_moves(state)
                return legal[0] if legal else None
            return _uci_to_move(best_uci)

    def evaluate(self, state: GameState) -> float:
        with self._lock:
            self._read_buf = b""
            self._send("ucinewgame")
            self._drain()
            fen = _state_to_fen(state)
            self._send(f"position fen {fen}")
            self._send("go depth 1")

            score = 0.0
            while True:
                line = self._read_line(timeout=10)
                if line is None or line.startswith("bestmove"):
                    break
                if "score cp" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "cp" and i + 1 < len(parts):
                            score = float(parts[i + 1]) / 100.0
                            break
                elif "score mate" in line:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p == "mate" and i + 1 < len(parts):
                            val = int(parts[i + 1])
                            score = 100.0 if val > 0 else -100.0
                            break
            side = state.side_to_move
            return score if side is Side.RED else -score

    def close(self):
        try:
            self._send("quit")
            self._process.stdin.close()
            self._process.wait(timeout=5)
        except Exception:
            self._process.kill()
