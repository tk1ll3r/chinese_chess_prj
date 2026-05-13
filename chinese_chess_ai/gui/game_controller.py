from __future__ import annotations

import queue
import random
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal
from tkinter import messagebox, ttk

from ..ai.evaluate import evaluate_position
from ..ai.search import SearchConfig, choose_move
from ..audio.sound_manager import SoundManager
from ..engine.moves import Move
from ..engine.rules import generate_legal_moves, is_in_check
from ..engine.state import GameState
from ..engine.types import Piece, Position, Side
from ..network.lan_room_transport import LanRoomClientTransport, LanRoomHostTransport
from ..network.protocol import deserialize_state
from ..network.transports import ClientTransport, HostTransport
from ..rating.elo import EloSystem
from .background import BackgroundImage, ONSITE_BACKGROUND_IMAGE_NAME, install_background
from .board_view import BoardView, checked_general_position, piece_display_code
from .move_history import MoveHistory
from .timer_manager import TimerManager

GameMode = Literal["local", "ai", "lan_host", "lan_join"]


@dataclass(frozen=True, slots=True)
class GameOptions:
    mode: GameMode = "local"
    human_side: Side = Side.RED
    difficulty: str = "Medium"
    room_code: str = ""


class GameController:
    def __init__(
        self,
        root: tk.Tk,
        options: GameOptions,
        show_menu_callback: Callable[[], None] | None = None,
        sound_manager: SoundManager | None = None,
    ) -> None:
        self.root = root
        self.options = options
        self.show_menu_callback = show_menu_callback
        self.state = GameState.initial()
        self.selected_square: Position | None = None
        self.game_over = False
        self.ai_side = options.human_side.opponent()
        self.search_config = self._difficulty_to_config(options.difficulty)
        self.local_side: Side | None = self._initial_local_side()
        self.room_code = options.room_code
        self.move_history = MoveHistory()
        self.timer = TimerManager()
        self.elo = EloSystem()
        self.red_player_name = "Player 1"
        self.black_player_name = "Player 2"
        self.elo_red_var = tk.StringVar(value=str(self.elo.get_rating("red")))
        self.elo_black_var = tk.StringVar(value=str(self.elo.get_rating("black")))
        self.elo_delta_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")
        self.turn_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="")
        self.history_var = tk.StringVar(value="No moves yet.")
        self.captured_var = tk.StringVar(value="Red captures: -\nBlack captures: -")
        self.eval_var = tk.StringVar(value="0.0")

        self.check_blink_on = True
        self._closed = False
        self._blink_after_id: str | None = None
        self._timer_after_id: str | None = None
        self._ai_after_id: str | None = None
        self._ai_poll_after_id: str | None = None
        self._ai_request_id = 0
        self._ai_thinking = False
        self._ai_thread: threading.Thread | None = None
        self._ai_results: queue.Queue[tuple[int, Move | None, str | None]] = queue.Queue()
        self._network_events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.host_transport: HostTransport | None = None
        self.client_transport: ClientTransport | None = None
        self._load_avatar_images()

        # Use shared SoundManager if provided, otherwise create one
        if sound_manager is not None:
            self.sound_manager = sound_manager
        else:
            self.sound_manager = SoundManager(enabled=True)

        # Set a generous default window size and position
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1400, screen_w - 100)
        win_h = min(960, screen_h - 100)
        x = (screen_w - win_w) // 2
        y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{x}+{y}")
        self.root.update_idletasks()

        self.frame = tk.Frame(root, bg="#1f1f1f")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)
        self._background: BackgroundImage | None = install_background(
            self.frame,
            fallback="#1f1f1f",
            image_name=ONSITE_BACKGROUND_IMAGE_NAME,
        )

        # Configure 2-column layout (left panel + board; right panel overlays)
        self.frame.grid_columnconfigure(0, weight=0, minsize=140)  # Left panel
        self.frame.grid_columnconfigure(1, weight=1)  # Board fills all remaining space

        # Configure root background
        self.root.configure(bg="#1f1f1f")

        # Configure ttk styles for timer bars
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Red.Horizontal.TProgressbar", background="#d32f2f", troughcolor="#1a1a1a", bordercolor="#1a1a1a", lightcolor="#d32f2f", darkcolor="#d32f2f")
        style.configure("Black.Horizontal.TProgressbar", background="#1976D2", troughcolor="#1a1a1a", bordercolor="#1a1a1a", lightcolor="#1976D2", darkcolor="#1976D2")

        self._build_left_panel()

        # Board container with auto-scaling
        board_container = tk.Frame(self.frame, bg="#2b2b2b")
        board_container.grid(row=0, column=1, padx=10, pady=10)
        board_container.grid_rowconfigure(0, weight=1)
        board_container.grid_columnconfigure(0, weight=1)

        self.board_view = BoardView(board_container, self._on_square_clicked)
        self.board_view.canvas.grid(row=0, column=0)

        # Right panel as overlay (hidden by default, slides in/out)
        self._panel_visible = False
        self._panel_animating = False
        self._build_right_panel_overlay()

        # Start with correct scale factor before first draw (avoids flash)
        self._apply_best_scale()

        self.root.title("Đại hải trình")
        self.root.resizable(True, True)

        # Keyboard shortcuts
        self._bind_root_events()
        self._start_network_if_needed()
        self._set_status(self._initial_status())
        self._redraw()
        self._schedule_ai_if_needed()
        self._schedule_blink()
        self._schedule_timer_update()
        self._poll_network_events()

    def destroy(self) -> None:
        self._closed = True
        self._cancel_ai_work()
        self._cancel_scheduled_callbacks()
        self._unbind_root_events()
        self._close_network()
        try:
            self.frame.destroy()
        except Exception:
            pass

    def _cancel_scheduled_callbacks(self) -> None:
        for attr in (
            "_blink_after_id",
            "_timer_after_id",
            "_ai_after_id",
            "_ai_poll_after_id",
        ):
            after_id = getattr(self, attr)
            if after_id is not None:
                try:
                    self.root.after_cancel(after_id)
                except Exception:
                    pass
                setattr(self, attr, None)

    def _cancel_ai_work(self) -> None:
        self._ai_request_id += 1
        self._ai_thinking = False
        for attr in ("_ai_after_id", "_ai_poll_after_id"):
            after_id = getattr(self, attr)
            if after_id is not None:
                try:
                    self.root.after_cancel(after_id)
                except Exception:
                    pass
                setattr(self, attr, None)

    def _bind_root_events(self) -> None:
        self.root.bind("<Configure>", self._on_root_configure)
        self.root.bind("<Control-z>", lambda e: self._undo_moves())
        self.root.bind("<Control-r>", lambda e: self._restart_game())
        self.root.bind("<Escape>", lambda e: self._back_to_menu())

    def _unbind_root_events(self) -> None:
        try:
            self.root.unbind("<Configure>")
            self.root.unbind("<Control-z>")
            self.root.unbind("<Control-r>")
            self.root.unbind("<Escape>")
        except Exception:
            pass

    def _load_avatar_images(self) -> None:
        self._avatar_files: list[Path] = []
        pics_dir = Path(__file__).parent.parent.parent / "assets" / "picture"
        if pics_dir.exists():
            self._avatar_files = sorted(
                p for p in pics_dir.iterdir()
                if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif"}
            )
        self._avatar_cache: dict[str, tk.PhotoImage] = {}
        self._current_avatars: dict[str, tk.PhotoImage | None] = {"red": None, "black": None}
        self._pick_random_avatars()

    def _pick_random_avatars(self) -> None:
        self._current_avatars = {"red": None, "black": None}
        if len(self._avatar_files) < 2:
            return
        try:
            from PIL import Image, ImageTk
            chosen = random.sample(self._avatar_files, 2)
            for side, path in zip(("red", "black"), chosen):
                if str(path) not in self._avatar_cache:
                    img = Image.open(path).resize((82, 82), Image.LANCZOS)
                    self._avatar_cache[str(path)] = ImageTk.PhotoImage(img)
                self._current_avatars[side] = self._avatar_cache[str(path)]
        except Exception:
            pass

    def _build_left_panel(self) -> None:
        left_panel = tk.Frame(self.frame, bg="#1a1a1a", width=140)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(3, 3), pady=6)
        left_panel.grid_propagate(False)

        # Top spacer to center cards vertically
        top_spacer = tk.Frame(left_panel, bg="#1a1a1a")
        top_spacer.pack(fill="both", expand=True)

        self._build_player_card(
            left_panel, "BLACK",
            self.black_player_name, self.elo_black_var,
            self.timer.black_time_var,
            accent="#1976D2", is_top=True,
        )

        separator = tk.Frame(left_panel, bg="#333333", height=1)
        separator.pack(fill="x", padx=12, pady=6)

        self._build_player_card(
            left_panel, "RED",
            self.red_player_name, self.elo_red_var,
            self.timer.red_time_var,
            accent="#d32f2f", is_top=False,
        )

        # Bottom spacer to center cards vertically
        bottom_spacer = tk.Frame(left_panel, bg="#1a1a1a")
        bottom_spacer.pack(fill="both", expand=True)

    def _build_player_card(
        self,
        parent: tk.Frame,
        side_label: str,
        name: str,
        elo_var: tk.StringVar,
        time_var: tk.StringVar,
        accent: str,
        is_top: bool,
    ) -> None:
        card = tk.Frame(parent, bg="#252525", highlightbackground=accent, highlightthickness=1)
        card.pack(padx=8, fill="x", pady=(0, 5))

        side_key = "black" if is_top else "red"
        avatar_img = self._current_avatars.get(side_key)

        avatar_bg = tk.Frame(card, bg="#333333", width=82, height=82)
        avatar_bg.pack(pady=(10, 4))
        avatar_bg.pack_propagate(False)

        if avatar_img:
            tk.Label(
                avatar_bg,
                image=avatar_img,
                bg="#333333",
            ).place(relx=0.5, rely=0.5, anchor="center")
        else:
            tk.Label(
                avatar_bg,
                text="?",
                font=("Arial", 28, "bold"),
                fg=accent,
                bg="#333333",
            ).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            card,
            text=name,
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#252525",
        ).pack(pady=(2, 0))

        elo_frame = tk.Frame(card, bg="#252525")
        elo_frame.pack(pady=(2, 4))

        tk.Label(
            elo_frame,
            text="ELO ",
            font=("Arial", 8),
            fg="#888888",
            bg="#252525",
        ).pack(side="left")

        tk.Label(
            elo_frame,
            textvariable=elo_var,
            font=("Arial", 11, "bold"),
            fg="#ffd700",
            bg="#252525",
        ).pack(side="left")

        self.elo_delta_label = tk.Label(
            elo_frame,
            textvariable=self.elo_delta_var,
            font=("Arial", 9, "bold"),
            fg="#4CAF50",
            bg="#252525",
        )
        self.elo_delta_label.pack(side="left", padx=(4, 0))

        timer_frame = tk.Frame(card, bg=accent, highlightthickness=0)
        timer_frame.pack(fill="x", padx=0, pady=(6, 0))

        tk.Label(
            timer_frame,
            textvariable=time_var,
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg=accent,
        ).pack(pady=(3, 1))

        timer_bar = ttk.Progressbar(
            card,
            orient="horizontal",
            length=140,
            mode="determinate",
            style=f"{'Black' if is_top else 'Red'}.Horizontal.TProgressbar",
        )
        timer_bar.pack(pady=(1, 8), padx=8, fill="x")
        timer_bar["maximum"] = 600
        timer_bar["value"] = 600

        if is_top:
            self.timer.black_timer_frame = timer_frame
            self.timer.black_timer_bar = timer_bar
        else:
            self.timer.red_timer_frame = timer_frame
            self.timer.red_timer_bar = timer_bar

    def _build_right_panel_overlay(self) -> None:
        """Right panel as an overlay that slides in/out from the right edge."""
        PANEL_WIDTH = 120
        self._right_panel_width = PANEL_WIDTH

        self.right_panel = tk.Frame(self.frame, bg="#1a1a1a", width=PANEL_WIDTH)
        self.right_panel.grid_propagate(False)

        # Toggle button (always visible, small tab on the right edge)
        self._toggle_btn = tk.Label(
            self.frame,
            text="\u25c0",
            font=("Arial", 14, "bold"),
            fg="#cccccc",
            bg="#333333",
            cursor="hand2",
            relief="flat",
            padx=4, pady=20,
        )
        self._toggle_btn.bind("<Button-1>", lambda e: self._toggle_right_panel())

        # Control buttons
        btn_style = {
            "font": ("Arial", 8),
            "relief": "flat",
            "cursor": "hand2",
            "borderwidth": 0,
            "height": 1
        }

        tk.Button(
            self.right_panel,
            text="Restart",
            command=self._restart_game,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            **btn_style
        ).pack(fill="x", padx=6, pady=(8, 3))

        tk.Button(
            self.right_panel,
            text="Undo",
            command=self._undo_moves,
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            **btn_style
        ).pack(fill="x", padx=6, pady=3)

        tk.Button(
            self.right_panel,
            text="Menu",
            command=self._back_to_menu,
            bg="#757575",
            fg="white",
            activebackground="#616161",
            activeforeground="white",
            **btn_style
        ).pack(fill="x", padx=6, pady=3)

        # Separator
        tk.Frame(self.right_panel, bg="#3a3a3a", height=2).pack(fill="x", pady=8)

        # Move history
        tk.Label(
            self.right_panel,
            text="Moves",
            font=("Arial", 9, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        ).pack(pady=(0, 5))

        history_frame = tk.Frame(self.right_panel, bg="#2a2a2a", relief="solid", borderwidth=1)
        history_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_text = tk.Text(
            history_frame,
            font=("Courier", 8),
            fg="#cccccc",
            bg="#2a2a2a",
            relief="flat",
            yscrollcommand=scrollbar.set,
            wrap="word",
            state="disabled"
        )
        self.history_text.pack(fill="both", expand=True, padx=3, pady=3)
        scrollbar.config(command=self.history_text.yview)

        # Status
        status_label = tk.Label(
            self.right_panel,
            textvariable=self.status_var,
            font=("Arial", 7),
            fg="#999999",
            bg="#1a1a1a",
            wraplength=PANEL_WIDTH - 10,
            justify="left"
        )
        status_label.pack(padx=5, pady=(0, 5))

        # Position panel and toggle button off-screen initially
        self._place_overlay(visible=False)

    def _place_overlay(self, visible: bool) -> None:
        fw = self.frame.winfo_width() or self.root.winfo_width()
        panel_x = fw - self._right_panel_width if visible else fw
        self.right_panel.place(x=panel_x, y=0, width=self._right_panel_width, rely=0, relheight=1)
        toggle_x = fw - self._right_panel_width - 18 if visible else fw - 18
        self._toggle_btn.place(x=toggle_x, y=0, rely=0.5, anchor="w")
        self._toggle_btn.config(text="\u25b6" if not visible else "\u25c0")

    def _toggle_right_panel(self) -> None:
        if self._panel_animating:
            return
        self._panel_animating = True
        if self._panel_visible:
            self._slide_out()
        else:
            self._slide_in()

    def _slide_in(self) -> None:
        fw = self.frame.winfo_width()
        start_x = fw
        end_x = fw - self._right_panel_width
        steps = 8
        step_size = (end_x - start_x) / steps

        def animate(step: int = 0, x: float | None = None) -> None:
            if self._closed:
                self._panel_animating = False
                return
            if x is None:
                x = start_x
            if step < steps:
                x = start_x + step_size * (step + 1)
                self.right_panel.place(x=int(x), y=0, width=self._right_panel_width, rely=0, relheight=1)
                toggle_x = int(x) - 18
                self._toggle_btn.place(x=toggle_x, y=0, rely=0.5, anchor="w")
                self.root.after(12, lambda: animate(step + 1, x))
            else:
                self.right_panel.place(x=int(end_x), y=0, width=self._right_panel_width, rely=0, relheight=1)
                toggle_x = int(end_x) - 18
                self._toggle_btn.place(x=toggle_x, y=0, rely=0.5, anchor="w")
                self._toggle_btn.config(text="\u25c0")
                self._panel_visible = True
                self._panel_animating = False
        animate()

    def _slide_out(self) -> None:
        fw = self.frame.winfo_width()
        start_x = fw - self._right_panel_width
        end_x = fw
        steps = 8
        step_size = (end_x - start_x) / steps

        def animate(step: int = 0, x: float | None = None) -> None:
            if self._closed:
                self._panel_animating = False
                return
            if x is None:
                x = start_x
            if step < steps:
                x = start_x + step_size * (step + 1)
                self.right_panel.place(x=int(x), y=0, width=self._right_panel_width, rely=0, relheight=1)
                toggle_x = int(x) - 18
                self._toggle_btn.place(x=toggle_x, y=0, rely=0.5, anchor="w")
                self.root.after(12, lambda: animate(step + 1, x))
            else:
                self.right_panel.place_forget()
                toggle_x = fw - 18
                self._toggle_btn.place(x=toggle_x, y=0, rely=0.5, anchor="w")
                self._toggle_btn.config(text="\u25b6")
                self._panel_visible = False
                self._panel_animating = False
        animate()

    def _update_move_history(self) -> None:
        if hasattr(self, 'history_text'):
            self.history_text.config(state="normal")
            self.history_text.delete("1.0", "end")

            if self.move_history.is_empty():
                self.history_text.insert("1.0", "No moves yet.")
            else:
                for move in self.move_history.moves:
                    self.history_text.insert("end", f"{move}\n")

            self.history_text.config(state="disabled")
            self.history_text.see("end")

    def _apply_best_scale(self) -> None:
        self.root.update_idletasks()
        panel_w = 140 + 20
        available_width = max(1, self.root.winfo_width() - panel_w)
        available_height = max(1, self.root.winfo_height() - 16)
        scale_w = available_width // 377
        scale_h = available_height // 417
        scale = max(1, min(scale_w, scale_h))
        self.board_view.configure_scale(scale)

    def _on_root_configure(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is not self.root or self._closed:
            return

        # Reposition overlay elements on resize
        self._place_overlay(visible=self._panel_visible)

        panel_w = 140 + 20
        available_width = max(1, self.root.winfo_width() - panel_w)
        available_height = max(1, self.root.winfo_height() - 16)
        scale_w = available_width // 377
        scale_h = available_height // 417
        scale = max(1, min(scale_w, scale_h))

        if scale != self.board_view.scale_factor:
            self.board_view.configure_scale(scale)
            self._redraw()

    def _initial_local_side(self) -> Side | None:
        if self.options.mode == "local":
            return None
        if self.options.mode == "ai":
            return self.options.human_side
        if self.options.mode == "lan_host":
            return Side.RED
        return None

    def _initial_status(self) -> str:
        if self.options.mode == "local":
            return "Two players on one machine."
        if self.options.mode == "ai":
            return f"You play {self._side_label(self.options.human_side)}. AI difficulty: {self._difficulty_label()}."
        if self.options.mode == "lan_host":
            room_text = f" Room code: {self.room_code}." if self.room_code else ""
            return f"Host plays Red. Waiting for the Black player to join over LAN.{room_text}"
        room_text = f" {self.room_code}" if self.room_code else ""
        return f"Searching for room{room_text} on the LAN."

    def _difficulty_to_config(self, difficulty: str) -> SearchConfig:
        if difficulty == "Easy":
            return SearchConfig(time_limit=1.0)
        if difficulty == "Hard":
            return SearchConfig(time_limit=4.0)
        return SearchConfig(time_limit=2.0)

    def _start_network_if_needed(self) -> None:
        if self.options.mode == "lan_host":
            self.host_transport = LanRoomHostTransport(
                room_code=self.room_code or None,
                tcp_port=0,
                on_state=lambda payload: self._network_events.put(("state", payload)),
                on_status=lambda message: self._network_events.put(("status", message)),
                on_error=lambda message: self._network_events.put(("error", message)),
                on_room_code=lambda code: self._network_events.put(("room_code", code)),
            )
            try:
                self.host_transport.start()
                self.room_code = self.host_transport.room_code
            except RuntimeError as exc:
                self._set_status(str(exc))
        elif self.options.mode == "lan_join":
            self.client_transport = LanRoomClientTransport(
                room_code=self.room_code,
                on_message=lambda message: self._network_events.put(("message", message)),
                on_status=lambda message: self._network_events.put(("status", message)),
                on_error=lambda message: self._network_events.put(("error", message)),
            )
            self.client_transport.start()

    def _poll_network_events(self) -> None:
        if self._closed:
            return
        while True:
            try:
                event_type, payload = self._network_events.get_nowait()
            except queue.Empty:
                break
            if event_type == "state" and isinstance(payload, dict):
                self._apply_network_state(payload)
            elif event_type == "message" and isinstance(payload, dict):
                self._handle_client_message(payload)
            elif event_type == "room_code":
                self.room_code = str(payload)
                self._set_status(f"Room created. Share code: {self.room_code}")
                self._redraw()
                if self.room_code != self.options.room_code:
                    messagebox.showinfo(
                        "Room Created",
                        f"Share this room code with the other player:\n\n{self.room_code}",
                    )
            elif event_type == "status":
                self._set_status(str(payload))
            elif event_type == "error":
                self._set_status(str(payload))
        self.root.after(80, self._poll_network_events)

    def _handle_client_message(self, message: dict) -> None:
        message_type = message.get("type")
        payload = message.get("payload", {})
        if message_type == "hello":
            self.local_side = Side(payload["side"])
            self._set_status(f"You play {self._side_label(self.local_side)}.")
            self._redraw()
        elif message_type == "state":
            self._apply_network_state(payload)
        elif message_type == "error":
            self._set_status(str(payload.get("message", "LAN error.")))

    def _apply_network_state(self, payload: dict) -> None:
        network_state = deserialize_state(payload)
        self.state = network_state.state
        self.move_history.moves = list(network_state.move_history)
        self.move_history.captured_by_red = list(network_state.captured_by_red)
        self.move_history.captured_by_black = list(network_state.captured_by_black)
        self.selected_square = None
        if network_state.status:
            self._set_status(network_state.status)
        self._redraw()
        self._check_game_over(show_dialog=False)

    def _close_network(self) -> None:
        if self.client_transport is not None:
            self.client_transport.close()
            self.client_transport = None
        if self.host_transport is not None:
            self.host_transport.close()
            self.host_transport = None

    def _on_square_clicked(self, clicked_square: Position) -> None:
        if self.game_over:
            return
        if not self._human_can_move():
            self._set_status("It is not your turn.")
            return

        clicked_piece = self.state.piece_at(clicked_square)
        if self.selected_square == clicked_square:
            self.selected_square = None
            self._redraw()
            return

        if self.selected_square is None:
            if clicked_piece is None or clicked_piece.side is not self.state.side_to_move:
                self._set_status("Select one of the pieces belonging to the side to move.")
                self.sound_manager.play_illegal()
                return
            self.selected_square = clicked_square
            self._set_status("Piece selected. Choose one of the highlighted target squares.")
            self.sound_manager.play_select()
            self._redraw()
            return

        chosen_move = next(
            (move for move in self._legal_moves_from_selected() if move.end == clicked_square),
            None,
        )
        if chosen_move is not None:
            self._request_move(chosen_move)
            return

        if clicked_piece is not None and clicked_piece.side is self.state.side_to_move:
            self.selected_square = clicked_square
            self._set_status("Selected piece changed.")
            self.sound_manager.play_select()
            self._redraw()
            return

        if is_in_check(self.state, self.state.side_to_move):
            self._set_status("You are in check. You must play a move that gets out of check.")
        else:
            self._set_status("That move is not legal.")
        self.sound_manager.play_illegal()

    def _request_move(self, move: Move) -> None:
        if self.options.mode == "lan_host":
            if self.host_transport is None:
                self._set_status("LAN host is not ready.")
                return
            ok, detail = self.host_transport.submit_local_move(move)
            if not ok:
                self._set_status(detail)
            return
        if self.options.mode == "lan_join":
            if self.client_transport is None:
                self._set_status("LAN client is not ready.")
                return
            self.selected_square = None
            self.client_transport.send_move(move)
            self._set_status("Move sent to host.")
            self._redraw()
            return

        self._apply_move(move, actor="AI" if self._ai_to_move() else "Player")

    def _apply_move(self, move: Move, actor: str) -> None:
        moving_side = self.state.side_to_move
        captured_piece = self.state.piece_at(move.end)

        # Play sound based on move type
        if captured_piece is not None:
            self.sound_manager.play_capture()
        else:
            self.sound_manager.play_move()

        self.state.make_move(move)
        self.selected_square = None
        self._record_move(moving_side, move, captured_piece, actor)

        # Check for check/checkmate
        if is_in_check(self.state, self.state.side_to_move):
            legal_moves = generate_legal_moves(self.state)
            if not legal_moves:
                self.sound_manager.play_checkmate()
            else:
                self.sound_manager.play_check()

        self._redraw()

        if self._check_game_over(show_dialog=True):
            return
        self._schedule_ai_if_needed()

    def _record_move(
        self,
        side: Side,
        move: Move,
        captured_piece: Piece | None,
        actor: str,
    ) -> None:
        self.move_history.record(side, move, captured_piece, actor, piece_display_code, self._side_label)
        self._update_move_history()

    def _schedule_ai_if_needed(self) -> None:
        if self._closed or self._ai_thinking or self._ai_after_id is not None:
            return
        if self._ai_to_move() and not self.game_over:
            self._ai_after_id = self.root.after(150, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        self._ai_after_id = None
        if self._closed or self._ai_thinking or not self._ai_to_move() or self.game_over:
            return
        self._ai_request_id += 1
        request_id = self._ai_request_id
        state_snapshot = self.state.clone()
        search_config = self.search_config
        self._ai_thinking = True
        self._set_status("AI is thinking...")
        self._redraw()

        def worker() -> None:
            move: Move | None = None
            error: str | None = None
            try:
                move = choose_move(state_snapshot, search_config)
            except Exception as exc:
                error = str(exc)
            self._ai_results.put((request_id, move, error))

        self._ai_thread = threading.Thread(target=worker, daemon=True)
        self._ai_thread.start()
        self._ai_poll_after_id = self.root.after(50, self._poll_ai_result)

    def _poll_ai_result(self) -> None:
        if self._closed:
            return

        current_result: tuple[int, Move | None, str | None] | None = None
        while True:
            try:
                result = self._ai_results.get_nowait()
            except queue.Empty:
                break
            if result[0] == self._ai_request_id:
                current_result = result
                break

        if current_result is None:
            if self._ai_thinking:
                self._ai_poll_after_id = self.root.after(50, self._poll_ai_result)
            else:
                self._ai_poll_after_id = None
            return

        self._ai_poll_after_id = None
        self._ai_thinking = False
        _request_id, ai_move, error = current_result

        if error is not None:
            self._set_status(f"AI error: {error}")
            return
        if not self._ai_to_move() or self.game_over:
            return
        if ai_move is None:
            self._check_game_over(show_dialog=True)
            return

        legal_move = next(
            (
                move
                for move in generate_legal_moves(self.state)
                if move.start == ai_move.start and move.end == ai_move.end
            ),
            None,
        )
        if legal_move is None:
            self._set_status("AI move was no longer legal. Retrying...")
            self._schedule_ai_if_needed()
            return

        self._apply_move(legal_move, actor="AI")

    def _undo_moves(self) -> None:
        if self.options.mode in {"lan_host", "lan_join"}:
            self._set_status("The LAN MVP does not support synchronized undo yet. Return to the menu to start a new game.")
            return

        self._cancel_ai_work()
        undo_count = 2 if self.options.mode == "ai" else 1
        undone = 0
        for _ in range(undo_count):
            if not self.state.move_history:
                break
            record = self.state.move_history[-1]
            if record.captured_piece is not None:
                self.move_history.remove_last_capture(record.previous_side_to_move)
            self.state.undo_move()
            if self.move_history.moves:
                self.move_history.moves.pop()
            undone += 1

        if undone == 0:
            self._set_status("No moves to undo.")
            return

        self.game_over = False
        self.selected_square = None
        self._set_status(f"Undid {undone} move(s).")
        self._redraw()

    def _restart_game(self) -> None:
        if self.options.mode in {"lan_host", "lan_join"}:
            self._set_status("The LAN MVP does not support synchronized restart yet. Return to the menu and host/join again.")
            return
        self._cancel_ai_work()
        self.sound_manager.play_button()
        self._pick_random_avatars()
        self.state = GameState.initial()
        self.selected_square = None
        self.game_over = False
        self.move_history.clear()
        self.timer.reset()
        self.elo_red_var.set(str(self.elo.get_rating("red")))
        self.elo_black_var.set(str(self.elo.get_rating("black")))
        self.elo_delta_var.set("")
        self._set_status(self._initial_status())
        self._redraw()
        self._schedule_ai_if_needed()

    def _back_to_menu(self) -> None:
        if self.show_menu_callback is not None:
            self.show_menu_callback()
        else:
            self.destroy()

    def _legal_moves_from_selected(self) -> list[Move]:
        if self.selected_square is None:
            return []
        return [
            move
            for move in generate_legal_moves(self.state)
            if move.start == self.selected_square
        ]

    def _human_can_move(self) -> bool:
        if self.options.mode == "local":
            return True
        if self.options.mode == "ai":
            return self.state.side_to_move is self.options.human_side
        if self.options.mode in {"lan_host", "lan_join"}:
            return self.local_side is not None and self.state.side_to_move is self.local_side
        return False

    def _ai_to_move(self) -> bool:
        return self.options.mode == "ai" and self.state.side_to_move is self.ai_side

    def _check_game_over(self, show_dialog: bool) -> bool:
        if self.game_over:
            return True
        legal_moves = generate_legal_moves(self.state)
        if legal_moves:
            return False
        self.game_over = True
        winner = self.state.side_to_move.opponent()
        if is_in_check(self.state, self.state.side_to_move):
            message = f"Checkmate. {self._side_label(winner)} wins."
        else:
            message = f"No legal moves remain. {self._side_label(winner)} wins."

        if winner is Side.RED:
            change = self.elo.record_game("red", "black")
            elo_msg = f"  ELO change: Red {change.player_delta:+d}, Black {change.opponent_delta:+d}"
        else:
            change = self.elo.record_game("black", "red")
            elo_msg = f"  ELO change: Black {change.player_delta:+d}, Red {change.opponent_delta:+d}"
        self.elo_red_var.set(str(self.elo.get_rating("red")))
        self.elo_black_var.set(str(self.elo.get_rating("black")))
        self.elo_delta_var.set(f"({change.player_delta:+d})")
        self.root.after(3000, lambda: self.elo_delta_var.set(""))

        self._set_status(message + elo_msg)
        self._redraw()
        if show_dialog:
            messagebox.showinfo("Game Over", message + elo_msg)
        return True

    def _should_flip_board(self) -> bool:
        if self.options.mode == "local":
            return False
        if self.options.mode == "ai":
            return self.options.human_side == Side.BLACK
        if self.options.mode in {"lan_host", "lan_join"}:
            return self.local_side == Side.BLACK
        return False

    def _redraw(self) -> None:
        in_check = is_in_check(self.state, self.state.side_to_move)
        checked_square = (
            checked_general_position(self.state, self.state.side_to_move) if in_check else None
        )
        self.board_view.draw(
            state=self.state,
            selected_square=self.selected_square,
            legal_moves=self._legal_moves_from_selected(),
            checked_square=checked_square,
            check_blink_on=self.check_blink_on,
            banner="Nguy hiểm, hải tặc đang bắt Luffy!" if in_check else "",
            flip=self._should_flip_board(),
        )
        self._refresh_sidebar(in_check)

    def _refresh_sidebar(self, in_check: bool) -> None:
        self.mode_var.set(self._mode_label())
        turn = f"Current turn: {self._side_label(self.state.side_to_move)}"
        if self.options.mode in {"ai", "lan_host", "lan_join"} and self.local_side is not None:
            turn += f"\nYou: {self._side_label(self.local_side)}"
        if in_check:
            turn += "\nNguy hiểm, hải tặc đang bắt Luffy!"
        self.turn_var.set(turn)
        self.history_var.set("\n".join(self.move_history.moves[-10:]) if self.move_history.moves else "No moves yet.")
        red_captures = ", ".join(self.move_history.captured_by_red) if self.move_history.captured_by_red else "-"
        black_captures = ", ".join(self.move_history.captured_by_black) if self.move_history.captured_by_black else "-"
        self.captured_var.set(f"Red captures: {red_captures}\nBlack captures: {black_captures}")

    def _mode_label(self) -> str:
        if self.options.mode == "local":
            return "Mode: Local Two Players"
        if self.options.mode == "ai":
            return f"Mode: Play vs AI ({self._difficulty_label()})"
        if self.options.mode == "lan_host":
            return f"Mode: LAN Host ({self.room_code or 'creating...'})"
        return f"Mode: LAN Join ({self.room_code or 'searching...'})"

    def _set_status(self, message: str) -> None:
        self.status_var.set(f"{message}\nEvaluation: {evaluate_position(self.state)}")

    def _side_label(self, side: Side) -> str:
        return "Red" if side is Side.RED else "Black"

    def _difficulty_label(self) -> str:
        return {"Easy": "Easy", "Medium": "Medium", "Hard": "Hard"}.get(
            self.options.difficulty,
            self.options.difficulty,
        )

    def _schedule_blink(self) -> None:
        if self._closed:
            return
        self.check_blink_on = not self.check_blink_on
        if is_in_check(self.state, self.state.side_to_move):
            self.board_view.update_check_highlight(
                checked_general_position(self.state, self.state.side_to_move),
                self.check_blink_on,
            )
        self._blink_after_id = self.root.after(450, self._schedule_blink)

    def _schedule_timer_update(self) -> None:
        if self._closed:
            return
        self._update_timer()
        self._timer_after_id = self.root.after(1000, self._schedule_timer_update)

    def _update_timer(self) -> None:
        if self._check_game_over(show_dialog=False):
            return

        if self.options.mode == "ai" and self.state.side_to_move != self.options.human_side:
            return

        if self.timer.last_timer_update is None:
            self.timer.start()
            return

        result = self.timer.update(self.state.side_to_move)
        if result is not None:
            self._set_status(result)
