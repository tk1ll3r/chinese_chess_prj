from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from ..audio.sound_manager import SoundManager
from ..engine.types import Side
from ..network.room_code import generate_room_code, normalize_room_code
from .fonts import configure_fonts
from .game_controller import GameController, GameOptions
from .settings_menu import SettingsMenu


def launch_gui() -> None:
    root = tk.Tk()
    configure_fonts(root)
    GameApp(root)
    root.mainloop()


class GameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Chinese Chess")
        self.root.resizable(True, True)
        self.current_controller: GameController | None = None
        self.current_settings: SettingsMenu | None = None
        self.menu_frame: tk.Frame | None = None
        self.sound_manager = SoundManager(enabled=True)
        self._start_background_music()
        self.show_main_menu()

    def _start_background_music(self) -> None:
        self.sound_manager.start_playlist()

    def show_main_menu(self) -> None:
        self._clear()
        self._start_background_music()

        self.root.configure(bg="#f5f5f5")
        self.root.geometry("500x600")

        frame = tk.Frame(self.root, bg="#f5f5f5")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        content = tk.Frame(frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")

        self.menu_frame = frame

        title_frame = tk.Frame(content, bg="#f5f5f5")
        title_frame.pack(pady=(0, 40))

        tk.Label(
            title_frame,
            text="Chinese Chess",
            font=("Arial", 48, "bold"),
            fg="#8B4513",
            bg="#f5f5f5"
        ).pack()
        tk.Label(
            title_frame,
            text="Xiangqi Game",
            font=("Arial", 16),
            fg="#666666",
            bg="#f5f5f5"
        ).pack()

        button_style = {
            "font": ("Arial", 12),
            "width": 25,
            "height": 2,
            "relief": "flat",
            "cursor": "hand2",
            "borderwidth": 0,
        }

        btn_local = tk.Button(
            content,
            text="Local Two Players",
            command=lambda: self.start_game(GameOptions(mode="local")),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            **button_style
        )
        btn_local.pack(pady=8)

        btn_ai = tk.Button(
            content,
            text="Play vs AI",
            command=self.show_ai_menu,
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            **button_style
        )
        btn_ai.pack(pady=8)

        btn_lan = tk.Button(
            content,
            text="LAN Multiplayer",
            command=self.show_lan_menu,
            bg="#FF9800",
            fg="white",
            activebackground="#F57C00",
            activeforeground="white",
            **button_style
        )
        btn_lan.pack(pady=8)

        btn_settings = tk.Button(
            content,
            text="Settings",
            command=self.show_settings_menu,
            bg="#9C27B0",
            fg="white",
            activebackground="#7B1FA2",
            activeforeground="white",
            **button_style
        )
        btn_settings.pack(pady=8)

        btn_exit = tk.Button(
            content,
            text="Exit",
            command=self.root.destroy,
            bg="#f44336",
            fg="white",
            activebackground="#d32f2f",
            activeforeground="white",
            **button_style
        )
        btn_exit.pack(pady=(20, 0))

        tk.Label(
            content,
            text="v2.0 Enhanced Edition",
            font=("Arial", 9),
            fg="#999999",
            bg="#f5f5f5"
        ).pack(pady=(30, 0))

    def show_ai_menu(self) -> None:
        self._clear()

        self.root.configure(bg="#f5f5f5")
        self.root.geometry("500x600")

        frame = tk.Frame(self.root, bg="#f5f5f5")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        content = tk.Frame(frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            content,
            text="Play vs AI",
            font=("Arial", 24, "bold"),
            fg="#2196F3",
            bg="#f5f5f5"
        ).pack(pady=(0, 30))

        side_var = tk.StringVar(value="Red")
        difficulty_var = tk.StringVar(value="Medium")

        side_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        side_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            side_frame,
            text="Choose Your Side",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 5))

        side_buttons = tk.Frame(side_frame, bg="white")
        side_buttons.pack(pady=(5, 15))

        def select_side(side: str) -> None:
            side_var.set(side)
            for btn in [btn_red, btn_black]:
                btn.config(relief="raised", bg="white", fg="#333333")
            if side == "Red":
                btn_red.config(relief="sunken", bg="#ffebee", fg="#d32f2f")
            else:
                btn_black.config(relief="sunken", bg="#e3f2fd", fg="#1976D2")

        btn_red = tk.Button(
            side_buttons,
            text="Red",
            font=("Arial", 11),
            width=12,
            height=2,
            command=lambda: select_side("Red"),
            cursor="hand2",
            relief="sunken",
            bg="#ffebee",
            fg="#d32f2f"
        )
        btn_red.pack(side="left", padx=5)

        btn_black = tk.Button(
            side_buttons,
            text="Black",
            font=("Arial", 11),
            width=12,
            height=2,
            command=lambda: select_side("Black"),
            cursor="hand2",
            relief="raised",
            bg="white",
            fg="#333333"
        )
        btn_black.pack(side="left", padx=5)

        diff_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        diff_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            diff_frame,
            text="AI Difficulty",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 5))

        diff_buttons = tk.Frame(diff_frame, bg="white")
        diff_buttons.pack(pady=(5, 15))

        def select_difficulty(diff: str) -> None:
            difficulty_var.set(diff)
            for btn in [btn_easy, btn_medium, btn_hard]:
                btn.config(relief="raised", bg="white", fg="#333333")
            if diff == "Easy":
                btn_easy.config(relief="sunken", bg="#e8f5e9", fg="#388E3C")
            elif diff == "Medium":
                btn_medium.config(relief="sunken", bg="#fff3e0", fg="#F57C00")
            else:
                btn_hard.config(relief="sunken", bg="#ffebee", fg="#d32f2f")

        btn_easy = tk.Button(
            diff_buttons,
            text="Easy",
            font=("Arial", 10),
            width=8,
            height=2,
            command=lambda: select_difficulty("Easy"),
            cursor="hand2",
            relief="raised",
            bg="white",
            fg="#333333"
        )
        btn_easy.pack(side="left", padx=3)

        btn_medium = tk.Button(
            diff_buttons,
            text="Medium",
            font=("Arial", 10),
            width=8,
            height=2,
            command=lambda: select_difficulty("Medium"),
            cursor="hand2",
            relief="sunken",
            bg="#fff3e0",
            fg="#F57C00"
        )
        btn_medium.pack(side="left", padx=3)

        btn_hard = tk.Button(
            diff_buttons,
            text="Hard",
            font=("Arial", 10),
            width=8,
            height=2,
            command=lambda: select_difficulty("Hard"),
            cursor="hand2",
            relief="raised",
            bg="white",
            fg="#333333"
        )
        btn_hard.pack(side="left", padx=3)

        def start() -> None:
            human_side = Side.RED if side_var.get() == "Red" else Side.BLACK
            self.start_game(
                GameOptions(
                    mode="ai",
                    human_side=human_side,
                    difficulty=difficulty_var.get(),
                )
            )

        btn_frame = tk.Frame(content, bg="#f5f5f5")
        btn_frame.pack(pady=(30, 0))

        tk.Button(
            btn_frame,
            text="Start Game",
            command=start,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="Back",
            command=self.show_main_menu,
            font=("Arial", 11),
            width=20,
            height=2,
            bg="#757575",
            fg="white",
            activebackground="#616161",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=5)

    def show_lan_menu(self) -> None:
        self._clear()

        self.root.configure(bg="#f5f5f5")
        self.root.geometry("500x600")

        frame = tk.Frame(self.root, bg="#f5f5f5")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        content = tk.Frame(frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            content,
            text="LAN Multiplayer",
            font=("Arial", 24, "bold"),
            fg="#FF9800",
            bg="#f5f5f5"
        ).pack(pady=(0, 20))

        info_frame = tk.Frame(content, bg="#e3f2fd", relief="solid", borderwidth=1)
        info_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            info_frame,
            text="LAN Mode",
            font=("Arial", 11, "bold"),
            bg="#e3f2fd",
            fg="#1976D2"
        ).pack(pady=(10, 5))

        tk.Label(
            info_frame,
            text="Both players must be on the same\nlocal network to connect.",
            font=("Arial", 10),
            bg="#e3f2fd",
            fg="#333333",
            justify="center"
        ).pack(pady=(0, 10))

        room_code_var = tk.StringVar(value="")
        error_var = tk.StringVar(value="")

        input_frame = tk.Frame(content, bg="white", relief="solid", borderwidth=1)
        input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            input_frame,
            text="Room Code",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(15, 5))

        entry = tk.Entry(
            input_frame,
            textvariable=room_code_var,
            font=("Arial", 14),
            justify="center",
            relief="flat",
            bg="#f5f5f5",
            fg="#333333"
        )
        entry.pack(pady=(5, 15), padx=20, fill="x")

        error_label = tk.Label(
            content,
            textvariable=error_var,
            font=("Arial", 10),
            fg="#d32f2f",
            bg="#f5f5f5",
            wraplength=400
        )
        error_label.pack(pady=5)

        def host_game() -> None:
            error_var.set("")
            room_code = generate_room_code()
            messagebox.showinfo(
                "Room Created",
                f"Your room code is:\n\n{room_code}\n\nShare this code with the other player.",
            )
            self.start_game(GameOptions(mode="lan_host", room_code=room_code))

        def join_game() -> None:
            try:
                room_code = normalize_room_code(room_code_var.get())
            except ValueError as exc:
                error_var.set(str(exc))
                return
            error_var.set("")
            self.start_game(GameOptions(mode="lan_join", room_code=room_code))

        btn_frame = tk.Frame(content, bg="#f5f5f5")
        btn_frame.pack(pady=(20, 0))

        tk.Button(
            btn_frame,
            text="Create Room",
            command=host_game,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="Join Room",
            command=join_game,
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="Back",
            command=self.show_main_menu,
            font=("Arial", 11),
            width=20,
            height=2,
            bg="#757575",
            fg="white",
            activebackground="#616161",
            activeforeground="white",
            relief="flat",
            cursor="hand2"
        ).pack(pady=(15, 0))

    def show_settings_menu(self) -> None:
        self._clear()
        self.current_settings = SettingsMenu(
            self.root,
            on_back=self.show_main_menu,
            sound_manager=self.sound_manager,
        )

    def start_game(self, options: GameOptions) -> None:
        self.sound_manager.stop_music()
        self._clear()
        self.current_controller = GameController(
            self.root,
            options,
            show_menu_callback=self.show_main_menu,
        )

    def _clear(self) -> None:
        if self.current_controller is not None:
            self.current_controller.destroy()
            self.current_controller = None
        if self.current_settings is not None:
            self.current_settings.destroy()
            self.current_settings = None
        if self.menu_frame is not None:
            self.menu_frame.destroy()
            self.menu_frame = None
        for widget in self.root.winfo_children():
            widget.destroy()
