from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import Callable

from ..audio.sound_manager import SoundManager
from ..engine.types import Side
from ..network.room_code import generate_room_code, normalize_room_code
from .background import (
    BACKGROUND_IMAGE_NAME,
    FIRST_IMAGE_NAME,
    BackgroundImage,
    assets_dir,
    create_cover_photo,
    install_background,
)
from .fonts import configure_fonts
from .game_controller import GameController, GameOptions
from .settings_menu import SettingsMenu

try:
    from PIL import Image, ImageOps, ImageTk, ImageEnhance
except Exception:
    Image = None
    ImageOps = None
    ImageTk = None
    ImageEnhance = None


def launch_gui() -> None:
    root = tk.Tk()
    configure_fonts(root)
    GameApp(root)
    root.mainloop()


class GameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Đại hải trình")
        self.root.resizable(True, True)
        self.current_controller: GameController | None = None
        self.current_settings: SettingsMenu | None = None
        self.menu_frame: tk.Frame | None = None
        self.menu_background: BackgroundImage | None = None
        self._canvas_photo: tk.PhotoImage | None = None
        self._khung_src = None
        self._khung_photos: dict[int, tuple] = {}
        self._hovered_index: int | None = None
        self.sound_manager = SoundManager(enabled=True)
        self.sound_manager.start_playlist()
        self.show_splash()

    def show_splash(self) -> None:
        self._clear()
        self.root.configure(bg="#000000")
        self.root.geometry("900x540")

        frame = tk.Frame(self.root, bg="#000000")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(frame, bd=0, highlightthickness=0, bg="#000000", cursor="hand2")
        canvas.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.menu_frame = frame

        def draw(_event: tk.Event[tk.Canvas] | None = None) -> None:
            width = max(1, canvas.winfo_width())
            height = max(1, canvas.winfo_height())
            canvas.delete("all")
            self._canvas_photo = create_cover_photo(FIRST_IMAGE_NAME, (width, height))
            if self._canvas_photo is not None:
                canvas.create_image(0, 0, image=self._canvas_photo, anchor="nw")
            else:
                canvas.create_rectangle(0, 0, width, height, fill="#000000", outline="")

        canvas.bind("<Configure>", draw)
        canvas.bind("<Button-1>", lambda _event: self.show_main_menu())
        self.root.bind("<Return>", lambda _event: self.show_main_menu())
        self.root.bind("<space>", lambda _event: self.show_main_menu())
        self.root.after_idle(draw)

    def _build_menu_shell(self) -> tuple[tk.Frame, tk.Frame]:
        self.root.configure(bg="#1f1f1f")
        self.root.geometry("500x600")

        frame = tk.Frame(self.root, bg="#1f1f1f")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.menu_background = install_background(frame, fallback="#1f1f1f")

        content = tk.Frame(frame, bg="#f5f5f5")
        content.place(relx=0.5, rely=0.5, anchor="center")
        self.menu_frame = frame
        return frame, content

    def show_main_menu(self) -> None:
        self._clear()
        self.sound_manager.set_volume(0.5)
        self.sound_manager.start_playlist()
        self._khung_photos.clear()
        self._hovered_index = None
        if Image is not None:
            kp = assets_dir() / "khung.jpg"
            if kp.exists():
                try:
                    self._khung_src = Image.open(kp).convert("RGBA")
                except Exception:
                    self._khung_src = None

        self.root.configure(bg="#1f1f1f")
        self.root.geometry("900x540")

        frame = tk.Frame(self.root, bg="#1f1f1f")
        frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(frame, bd=0, highlightthickness=0, bg="#1f1f1f")
        canvas.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.menu_frame = frame

        buttons: tuple[tuple[str, str, Callable[[], None]], ...] = (
            ("Local Two Players", "#2e7d32", lambda: self.start_game(GameOptions(mode="local"))),
            ("Play vs AI", "#1565c0", self.show_ai_menu),
            ("LAN Multiplayer", "#ef6c00", self.show_lan_menu),
            ("Settings", "#7b1fa2", self.show_settings_menu),
            ("Exit", "#b71c1c", self.root.destroy),
        )

        def draw(_event: tk.Event[tk.Canvas] | None = None) -> None:
            width = max(1, canvas.winfo_width())
            height = max(1, canvas.winfo_height())
            canvas.delete("all")
            self._canvas_photo = create_cover_photo(BACKGROUND_IMAGE_NAME, (width, height))
            if self._canvas_photo is not None:
                canvas.create_image(0, 0, image=self._canvas_photo, anchor="nw")
            else:
                canvas.create_rectangle(0, 0, width, height, fill="#1f1f1f", outline="")

            title_y = max(72, int(height * 0.16))
            try:
                tf = ("Times New Roman", 52, "bold")
                sf = ("Times New Roman", 26, "bold")
            except Exception:
                tf = ("Arial", 52, "bold")
                sf = ("Arial", 26, "bold")
            canvas.create_text(
                width // 2 + 2, title_y + 2,
                text="Đại hải trình",
                fill="#555555",
                font=tf,
            )
            canvas.create_text(
                width // 2, title_y,
                text="Đại hải trình",
                fill="#ffffff",
                font=tf,
            )
            canvas.create_text(
                width // 2, title_y + 60,
                text="Van Thuong",
                fill="#ffffff",
                font=sf,
            )


            button_width = min(330, max(250, int(width * 0.42)))
            button_height = 46
            gap = 13
            total_height = (button_height * len(buttons)) + (gap * (len(buttons) - 1))
            start_y = max(title_y + 92, (height - total_height) // 2 + 38)
            left = (width - button_width) // 2

            for index, (label, color, command) in enumerate(buttons):
                top = start_y + (index * (button_height + gap))
                tag = f"menu_button_{index}"
                img_tag = f"btn_img_{index}"
                txt_tag = f"btn_txt_{index}"

                use_khung = self._khung_src is not None and Image is not None
                if use_khung:
                    try:
                        fitted = ImageOps.fit(self._khung_src, (button_width, button_height), method=Image.Resampling.LANCZOS)
                        normal = ImageTk.PhotoImage(fitted)
                        bright = ImageEnhance.Brightness(fitted).enhance(1.25)
                        hover = ImageTk.PhotoImage(bright)
                        self._khung_photos[index] = (normal, hover)
                        img = hover if self._hovered_index == index else normal
                        canvas.create_image(left, top + 1, image=img, anchor="nw", tags=(tag, img_tag))
                    except Exception:
                        use_khung = False
                if not use_khung:
                    canvas.create_rectangle(left, top, left + button_width, top + button_height,
                                            fill=color, outline="#ffe0a3", width=2, tags=(tag,))

                canvas.create_text(
                    width // 2, top + (button_height // 2),
                    text=label,
                    fill="#3e2723" if use_khung else "#ffffff",
                    font=("Georgia", 13, "bold") if use_khung else ("Arial", 13, "bold"),
                    tags=(tag, txt_tag),
                )

                canvas.tag_bind(tag, "<Button-1>", lambda _event, cmd=command: cmd())
                canvas.tag_bind(tag, "<Enter>", lambda _event, idx=index: self._on_btn_enter(idx, canvas))
                canvas.tag_bind(tag, "<Leave>", lambda _event, idx=index: self._on_btn_leave(idx, canvas))

            canvas.create_text(
                width // 2,
                min(height - 24, start_y + total_height + 34),
                text="v2.0 Enhanced Edition",
                fill="#f8f1dc",
                font=("Arial", 9),
            )

        canvas.bind("<Configure>", draw)
        self.root.after_idle(draw)

    def _on_btn_enter(self, idx: int, canvas: tk.Canvas) -> None:
        self._hovered_index = idx
        canvas.config(cursor="hand2")
        if idx in self._khung_photos:
            canvas.itemconfig(f"btn_img_{idx}", image=self._khung_photos[idx][1])

    def _on_btn_leave(self, idx: int, canvas: tk.Canvas) -> None:
        self._hovered_index = None
        canvas.config(cursor="")
        if idx in self._khung_photos:
            canvas.itemconfig(f"btn_img_{idx}", image=self._khung_photos[idx][0])

    def show_ai_menu(self) -> None:
        self._clear()

        _frame, content = self._build_menu_shell()

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

        _frame, content = self._build_menu_shell()

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
        self.sound_manager.set_volume(0.25)
        self._clear()
        self.current_controller = GameController(
            self.root,
            options,
            show_menu_callback=self.show_main_menu,
            sound_manager=self.sound_manager,
        )

    def _clear(self) -> None:
        self.root.attributes("-fullscreen", False)
        self.root.update_idletasks()
        self.root.unbind("<Return>")
        self.root.unbind("<space>")
        self._canvas_photo = None
        if self.current_controller is not None:
            self.current_controller.destroy()
            self.current_controller = None
        if self.current_settings is not None:
            self.current_settings.destroy()
            self.current_settings = None
        if self.menu_frame is not None:
            self.menu_frame.destroy()
            self.menu_frame = None
            self.menu_background = None
        remaining = self.root.winfo_children()
        for widget in remaining:
            try:
                widget.destroy()
            except Exception:
                pass
