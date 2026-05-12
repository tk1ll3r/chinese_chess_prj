from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class SettingsMenu:
    """Settings menu for game configuration."""

    def __init__(
        self,
        root: tk.Tk,
        on_back: Callable[[], None],
        sound_manager: object | None = None,
    ):
        self.root = root
        self.on_back = on_back
        self.sound_manager = sound_manager

        # Configure window
        self.root.configure(bg="#f5f5f5")
        self.root.geometry("500x600")

        self.frame = tk.Frame(root, bg="#f5f5f5")
        self.frame.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Center content
        content = tk.Frame(self.frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(
            content,
            text="Settings",
            font=("Arial", 24, "bold"),
            fg="#9C27B0",
            bg="#f5f5f5"
        ).pack(pady=(0, 30))

        # Sound settings
        sound_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        sound_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            sound_frame,
            text="Sound",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 10))

        # Sound enabled checkbox
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

        # Volume slider
        volume_frame = tk.Frame(sound_frame, bg="white")
        volume_frame.pack(pady=(10, 15), padx=20, fill="x")

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

        # Animation settings
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

        # Back button
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
        """Handle sound enable/disable."""
        if self.sound_manager:
            self.sound_manager.set_enabled(self.sound_enabled_var.get())

    def _on_volume_change(self, value: str) -> None:
        """Handle volume change."""
        if self.sound_manager:
            self.sound_manager.set_volume(float(value))

    def _on_back_clicked(self) -> None:
        """Handle back button click."""
        if self.sound_manager:
            self.sound_manager.play_button()
        self.destroy()
        self.on_back()

    def destroy(self) -> None:
        """Destroy the settings menu."""
        self.frame.destroy()
