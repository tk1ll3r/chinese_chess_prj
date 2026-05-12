from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk

from ..engine.types import Side

MAX_TIME = 600


class TimerManager:
    def __init__(self) -> None:
        self.red_time_seconds = MAX_TIME
        self.black_time_seconds = MAX_TIME
        self.timer_running = False
        self.last_timer_update: float | None = None

        self.red_time_var = tk.StringVar(value="10:00")
        self.black_time_var = tk.StringVar(value="10:00")
        self.red_timer_frame: tk.Frame | None = None
        self.black_timer_frame: tk.Frame | None = None
        self.red_timer_bar: ttk.Progressbar | None = None
        self.black_timer_bar: ttk.Progressbar | None = None

    def reset(self) -> None:
        self.red_time_seconds = MAX_TIME
        self.black_time_seconds = MAX_TIME
        self.timer_running = False
        self.last_timer_update = None
        self._refresh_displays()

    def start(self) -> None:
        self.last_timer_update = time.time()
        self.timer_running = True

    def update(self, side_to_move: Side) -> str | None:
        if self.last_timer_update is None:
            return None
        now = time.time()
        elapsed = now - self.last_timer_update
        self.last_timer_update = now

        if side_to_move is Side.RED:
            self.red_time_seconds = max(0, self.red_time_seconds - elapsed)
            self._update_display(
                self.red_time_seconds, self.red_time_var, self.red_timer_frame, self.red_timer_bar,
                normal_bg="#d32f2f", warning_bg="#b71c1c",
            )
            if self.red_time_seconds <= 0:
                return "Time out! Black wins!"
        else:
            self.black_time_seconds = max(0, self.black_time_seconds - elapsed)
            self._update_display(
                self.black_time_seconds, self.black_time_var, self.black_timer_frame, self.black_timer_bar,
                normal_bg="#1976D2", warning_bg="#0d47a1",
            )
            if self.black_time_seconds <= 0:
                return "Time out! Red wins!"
        return None

    def _refresh_displays(self) -> None:
        self._update_display(
            self.red_time_seconds, self.red_time_var, self.red_timer_frame, self.red_timer_bar,
            normal_bg="#d32f2f", warning_bg="#b71c1c",
        )
        self._update_display(
            self.black_time_seconds, self.black_time_var, self.black_timer_frame, self.black_timer_bar,
            normal_bg="#1976D2", warning_bg="#0d47a1",
        )

    @staticmethod
    def _update_display(
        seconds: float,
        var: tk.StringVar,
        frame: tk.Frame | None,
        bar: ttk.Progressbar | None,
        normal_bg: str,
        warning_bg: str,
    ) -> None:
        secs = int(seconds)
        mins = secs // 60
        var.set(f"{mins}:{secs % 60:02d}")
        if frame is not None:
            frame.config(bg=warning_bg if secs < 30 else normal_bg)
        if bar is not None:
            bar["value"] = secs
