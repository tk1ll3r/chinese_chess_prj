from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .background import BackgroundImage, install_background


class SettingsMenu:
    def __init__(
        self,
        root: tk.Tk,
        on_back: Callable[[], None],
        sound_manager: object | None = None,
    ):
        self.root = root
        self.on_back = on_back
        self.sound_manager = sound_manager
        self._original_geometry = ""
        self._background: BackgroundImage | None = None

        self.root.configure(bg="#1f1f1f")
        self.root.geometry("500x600")

        self.frame = tk.Frame(root, bg="#1f1f1f")
        self.frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self._background = install_background(self.frame, fallback="#1f1f1f")

        content = tk.Frame(self.frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            content,
            text="Settings",
            font=("Arial", 24, "bold"),
            fg="#9C27B0",
            bg="#f5f5f5"
        ).pack(pady=(0, 30))

        sound_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        sound_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            sound_frame,
            text="Sound",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 10))

        self.sound_enabled_var = tk.BooleanVar(value=True)
        sound_check = tk.Checkbutton(
            sound_frame,
            text="Enable sound effects",
            variable=self.sound_enabled_var,
            command=self._on_sound_toggle,
            font=("Arial", 10),
            bg="white",
            activebackground="white",
            selectcolor="#e8f5e9"
        )
        sound_check.pack(pady=5)

        test_btn = tk.Button(
            sound_frame,
            text="Test Sound",
            command=self._on_test_sound,
            font=("Arial", 9),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=10
        )
        test_btn.pack(pady=(0, 5))

        volume_frame = tk.Frame(sound_frame, bg="white")
        volume_frame.pack(pady=(10, 5), padx=20, fill="x")

        tk.Label(
            volume_frame,
            text="Volume:",
            font=("Arial", 10),
            bg="white",
            fg="#333333"
        ).pack(side="left", padx=(0, 10))

        self.volume_var = tk.DoubleVar(value=0.7)
        volume_slider = tk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.volume_var,
            command=self._on_volume_change,
            showvalue=False,
            bg="white",
            highlightthickness=0,
            troughcolor="#e0e0e0",
            activebackground="#9C27B0"
        )
        volume_slider.pack(side="left", fill="x", expand=True)

        self.music_enabled_var = tk.BooleanVar(value=True)
        music_check = tk.Checkbutton(
            sound_frame,
            text="Enable background music",
            variable=self.music_enabled_var,
            command=self._on_music_toggle,
            font=("Arial", 10),
            bg="white",
            activebackground="white",
            selectcolor="#e8f5e9"
        )
        music_check.pack(pady=(5, 15))

        display_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        display_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            display_frame,
            text="Display",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 10))

        self.fullscreen_var = tk.BooleanVar(value=False)
        fullscreen_check = tk.Checkbutton(
            display_frame,
            text="Fullscreen mode",
            variable=self.fullscreen_var,
            command=self._on_fullscreen_toggle,
            font=("Arial", 10),
            bg="white",
            activebackground="white",
            selectcolor="#e8f5e9"
        )
        fullscreen_check.pack(pady=(5, 15))

        anim_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        anim_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            anim_frame,
            text="Animations",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 10))

        self.animations_enabled_var = tk.BooleanVar(value=True)
        anim_check = tk.Checkbutton(
            anim_frame,
            text="Enable piece animations",
            variable=self.animations_enabled_var,
            font=("Arial", 10),
            bg="white",
            activebackground="white",
            selectcolor="#e8f5e9"
        )
        anim_check.pack(pady=(5, 15))

        tk.Button(
            content,
            text="Back to Menu",
            command=self._on_back_clicked,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#757575",
            fg="white",
            activebackground="#616161",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=(30, 0))

    def _on_sound_toggle(self) -> None:
        if self.sound_manager:
            self.sound_manager.set_enabled(self.sound_enabled_var.get())

    def _on_test_sound(self) -> None:
        if self.sound_manager:
            self.sound_manager.play_button()
            self.root.after(200, self.sound_manager.play_select)
            self.root.after(400, self.sound_manager.play_move)

    def _on_music_toggle(self) -> None:
        if self.sound_manager:
            self.sound_manager.set_music_enabled(self.music_enabled_var.get())

    def _on_volume_change(self, value: str) -> None:
        if self.sound_manager:
            self.sound_manager.set_volume(float(value))

    def _on_fullscreen_toggle(self) -> None:
        is_fullscreen = self.fullscreen_var.get()
        if is_fullscreen:
            self._original_geometry = self.root.geometry()
            self.root.attributes("-fullscreen", True)
        else:
            self.root.attributes("-fullscreen", False)
            if self._original_geometry:
                self.root.geometry(self._original_geometry)

    def _on_back_clicked(self) -> None:
        if self.sound_manager:
            self.sound_manager.play_button()
        self.destroy()
        self.on_back()

    def destroy(self) -> None:
        self.frame.destroy()
