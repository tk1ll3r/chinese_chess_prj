from __future__ import annotations

import queue
import tkinter as tk
from dataclasses import dataclass
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
from .board_view import BoardView, checked_general_position, piece_display_code

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
        self.move_history: list[str] = []
        self.captured_by_red: list[str] = []
        self.captured_by_black: list[str] = []
        self.status_var = tk.StringVar(value="")
        self.turn_var = tk.StringVar(value="")
        self.mode_var = tk.StringVar(value="")
        self.history_var = tk.StringVar(value="No moves yet.")
        self.captured_var = tk.StringVar(value="Red captures: -\nBlack captures: -")
        self.eval_var = tk.StringVar(value="0.0")

        # Timer variables
        self.red_time_var = tk.StringVar(value="10:00")
        self.black_time_var = tk.StringVar(value="10:00")
        self.red_time_seconds = 600  # 10 minutes
        self.black_time_seconds = 600
        self.timer_running = False
        self.last_timer_update = None

        # Timer frames (will be set in _build_left_panel)
        self.red_timer_frame = None
        self.black_timer_frame = None

        self.check_blink_on = True
        self._closed = False
        self._network_events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.host_transport: HostTransport | None = None
        self.client_transport: ClientTransport | None = None

        self.frame = tk.Frame(root, bg="#2b2b2b")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # Configure 3-column layout
        self.frame.grid_columnconfigure(0, weight=0, minsize=180)  # Left panel
        self.frame.grid_columnconfigure(1, weight=1)  # Board (center)
        self.frame.grid_columnconfigure(2, weight=0, minsize=250)  # Right panel

        # Configure root background
        self.root.configure(bg="#2b2b2b")

        # Build 3-column layout
        self._build_left_panel()

        # Board container with auto-scaling
        board_container = tk.Frame(self.frame, bg="#2b2b2b")
        board_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        board_container.grid_rowconfigure(0, weight=1)
        board_container.grid_columnconfigure(0, weight=1)

        self.board_view = BoardView(board_container, self._on_square_clicked)
        self.board_view.canvas.grid(row=0, column=0)

        self._build_right_panel()

        # Initialize sound manager
        self.sound_manager = SoundManager(enabled=True)

        self.root.title("Chinese Chess")
        self.root.resizable(True, True)
        self.root.bind("<Configure>", self._on_root_configure)

        # Keyboard shortcuts
        self.root.bind("<Control-z>", lambda e: self._undo_moves())
        self.root.bind("<Control-r>", lambda e: self._restart_game())
        self.root.bind("<Escape>", lambda e: self._back_to_menu())

        self._start_network_if_needed()
        self._set_status(self._initial_status())
        self._redraw()
        self._schedule_ai_if_needed()
        self._schedule_blink()
        self._schedule_timer_update()
        self._poll_network_events()

    def destroy(self) -> None:
        self._closed = True
        self._close_network()
        self.frame.destroy()

    def _build_left_panel(self) -> None:
        """Build left panel with player info and timers."""
        left_panel = tk.Frame(self.frame, bg="#1a1a1a", width=180)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.grid_propagate(False)

        # Title
        tk.Label(
            left_panel,
            text="Players",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        ).pack(pady=(10, 20))

        # Black player (top)
        self._build_player_card(
            left_panel,
            "Black Player",
            "Player 2",
            "1500",
            self.black_time_var,
            "#1976D2",  # Blue
            is_top=True
        )

        # Separator
        tk.Frame(left_panel, bg="#3a3a3a", height=2).pack(fill="x", pady=20)

        # Red player (bottom)
        self._build_player_card(
            left_panel,
            "Red Player",
            "Player 1",
            "1500",
            self.red_time_var,
            "#d32f2f",  # Red
            is_top=False
        )

    def _build_player_card(
        self,
        parent: tk.Frame,
        label: str,
        name: str,
        elo: str,
        time_var: tk.StringVar,
        color: str,
        is_top: bool
    ) -> None:
        """Build a player info card."""
        # Player label
        tk.Label(
            parent,
            text=label,
            font=("Arial", 10),
            fg="#999999",
            bg="#1a1a1a"
        ).pack()

        # Player info card
        card = tk.Frame(parent, bg="#2a2a2a", relief="solid", borderwidth=1)
        card.pack(pady=(5, 0), padx=10, fill="x")

        # Avatar placeholder
        avatar = tk.Frame(card, bg="#3a3a3a", width=50, height=50)
        avatar.pack(pady=10)
        tk.Label(
            avatar,
            text="👤",
            font=("Arial", 20),
            fg="#666666",
            bg="#3a3a3a"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Name
        tk.Label(
            card,
            text=name,
            font=("Arial", 11, "bold"),
            fg="#ffffff",
            bg="#2a2a2a"
        ).pack()

        # ELO
        tk.Label(
            card,
            text=f"ELO: {elo}",
            font=("Arial", 9),
            fg="#999999",
            bg="#2a2a2a"
        ).pack(pady=(2, 10))

        # Timer
        timer_frame = tk.Frame(parent, bg=color, relief="solid", borderwidth=1)
        timer_frame.pack(pady=(10, 0), padx=10, fill="x")

        tk.Label(
            timer_frame,
            textvariable=time_var,
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg=color
        ).pack(pady=8)

        # Store timer frame reference
        if is_top:
            self.black_timer_frame = timer_frame
        else:
            self.red_timer_frame = timer_frame

    def _build_right_panel(self) -> None:
        """Build right panel with controls and move history."""
        right_panel = tk.Frame(self.frame, bg="#1a1a1a", width=250)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.grid_propagate(False)

        # Title
        tk.Label(
            right_panel,
            text="Game Controls",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        ).pack(pady=(10, 15))

        # Control buttons
        button_style = {
            "font": ("Arial", 10),
            "relief": "flat",
            "cursor": "hand2",
            "borderwidth": 0,
            "width": 20,
            "height": 2
        }

        tk.Button(
            right_panel,
            text="Restart",
            command=self._restart_game,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            **button_style
        ).pack(pady=5, padx=10)

        tk.Button(
            right_panel,
            text="Undo",
            command=self._undo_moves,
            bg="#2196F3",
            fg="white",
            activebackground="#1976D2",
            activeforeground="white",
            **button_style
        ).pack(pady=5, padx=10)

        tk.Button(
            right_panel,
            text="Back to Menu",
            command=self._back_to_menu,
            bg="#757575",
            fg="white",
            activebackground="#616161",
            activeforeground="white",
            **button_style
        ).pack(pady=5, padx=10)

        # Separator
        tk.Frame(right_panel, bg="#3a3a3a", height=2).pack(fill="x", pady=15)

        # Move history
        tk.Label(
            right_panel,
            text="Move History",
            font=("Arial", 12, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        ).pack(pady=(0, 10))

        # Scrollable move list
        history_frame = tk.Frame(right_panel, bg="#2a2a2a", relief="solid", borderwidth=1)
        history_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollbar
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        # Text widget for move history
        self.history_text = tk.Text(
            history_frame,
            font=("Courier", 9),
            fg="#cccccc",
            bg="#2a2a2a",
            relief="flat",
            yscrollcommand=scrollbar.set,
            wrap="word",
            state="disabled"
        )
        self.history_text.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.history_text.yview)

        # Status
        tk.Label(
            right_panel,
            text="Status",
            font=("Arial", 10, "bold"),
            fg="#ffffff",
            bg="#1a1a1a"
        ).pack(pady=(10, 5))

        status_label = tk.Label(
            right_panel,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg="#999999",
            bg="#1a1a1a",
            wraplength=230,
            justify="left"
        )
        status_label.pack(padx=10)

    def _update_move_history(self) -> None:
        """Update the scrollable move history display."""
        if hasattr(self, 'history_text'):
            self.history_text.config(state="normal")
            self.history_text.delete("1.0", "end")

            if not self.move_history:
                self.history_text.insert("1.0", "No moves yet.")
            else:
                for i, move in enumerate(self.move_history, 1):
                    self.history_text.insert("end", f"{move}\n")

            self.history_text.config(state="disabled")
            self.history_text.see("end")

    def _on_root_configure(self, event: tk.Event[tk.Misc]) -> None:
        """Handle window resize - scale board to fit available space."""
        if event.widget is not self.root or self._closed:
            return

        self.root.update_idletasks()

        # Calculate available space for board (center column)
        # Left panel: 180px, Right panel: 250px, padding: ~40px
        available_width = max(1, self.root.winfo_width() - 180 - 250 - 60)
        available_height = max(1, self.root.winfo_height() - 40)

        # Calculate scale factor to fit board in available space
        scale_w = available_width // 377  # BASE_BOARD_WIDTH
        scale_h = available_height // 417  # BASE_BOARD_HEIGHT
        scale = max(1, min(scale_w, scale_h, 4))

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
            return SearchConfig(depth=1, use_alpha_beta=True)
        if difficulty == "Hard":
            return SearchConfig(depth=3, use_alpha_beta=True)
        return SearchConfig(depth=2, use_alpha_beta=True)

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
        self.move_history = list(network_state.move_history)
        self.captured_by_red = list(network_state.captured_by_red)
        self.captured_by_black = list(network_state.captured_by_black)
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
        move_number = len(self.move_history) + 1
        capture_text = ""
        if captured_piece is not None:
            captured_code = piece_display_code(captured_piece)
            capture_text = f" x {captured_code}"
            if side is Side.RED:
                self.captured_by_red.append(captured_code)
            else:
                self.captured_by_black.append(captured_code)
        move_str = (
            f"{move_number}. {actor} {self._side_label(side)}: "
            f"({move.start[0]},{move.start[1]}) -> ({move.end[0]},{move.end[1]}){capture_text}"
        )
        self.move_history.append(move_str)

        # Update scrollable history
        self._update_move_history()

    def _schedule_ai_if_needed(self) -> None:
        if self._ai_to_move() and not self.game_over:
            self.root.after(150, self._run_ai_turn)

    def _run_ai_turn(self) -> None:
        if not self._ai_to_move() or self.game_over:
            return
        self._set_status("AI is thinking...")
        self.root.update_idletasks()
        ai_move = choose_move(self.state, self.search_config)
        if ai_move is None:
            self._check_game_over(show_dialog=True)
            return
        self._apply_move(ai_move, actor="AI")

    def _undo_moves(self) -> None:
        if self.options.mode in {"lan_host", "lan_join"}:
            self._set_status("The LAN MVP does not support synchronized undo yet. Return to the menu to start a new game.")
            return

        undo_count = 2 if self.options.mode == "ai" else 1
        undone = 0
        for _ in range(undo_count):
            if not self.state.move_history:
                break
            record = self.state.move_history[-1]
            if record.captured_piece is not None:
                self._remove_last_capture(record.previous_side_to_move)
            self.state.undo_move()
            if self.move_history:
                self.move_history.pop()
            undone += 1

        if undone == 0:
            self._set_status("No moves to undo.")
            return

        self.game_over = False
        self.selected_square = None
        self._set_status(f"Undid {undone} move(s).")
        self._redraw()

    def _remove_last_capture(self, side: Side) -> None:
        captures = self.captured_by_red if side is Side.RED else self.captured_by_black
        if captures:
            captures.pop()

    def _restart_game(self) -> None:
        if self.options.mode in {"lan_host", "lan_join"}:
            self._set_status("The LAN MVP does not support synchronized restart yet. Return to the menu and host/join again.")
            return
        self.sound_manager.play_button()
        self.state = GameState.initial()
        self.selected_square = None
        self.game_over = False
        self.move_history.clear()
        self.captured_by_red.clear()
        self.captured_by_black.clear()
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
        legal_moves = generate_legal_moves(self.state)
        if legal_moves:
            return False
        self.game_over = True
        winner = self.state.side_to_move.opponent()
        if is_in_check(self.state, self.state.side_to_move):
            message = f"Checkmate. {self._side_label(winner)} wins."
        else:
            message = f"No legal moves remain. {self._side_label(winner)} wins."
        self._set_status(message)
        self._redraw()
        if show_dialog:
            messagebox.showinfo("Game Over", message)
        return True

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
            banner="Check!" if in_check else "",
        )
        self._refresh_sidebar(in_check)

    def _refresh_sidebar(self, in_check: bool) -> None:
        self.mode_var.set(self._mode_label())
        turn = f"Current turn: {self._side_label(self.state.side_to_move)}"
        if self.options.mode in {"ai", "lan_host", "lan_join"} and self.local_side is not None:
            turn += f"\nYou: {self._side_label(self.local_side)}"
        if in_check:
            turn += "\nCheck!"
        self.turn_var.set(turn)
        self.history_var.set("\n".join(self.move_history[-10:]) if self.move_history else "No moves yet.")
        red_captures = ", ".join(self.captured_by_red) if self.captured_by_red else "-"
        black_captures = ", ".join(self.captured_by_black) if self.captured_by_black else "-"
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
            self._redraw()
        self.root.after(450, self._schedule_blink)

    def _schedule_timer_update(self) -> None:
        """Schedule timer countdown updates."""
        if self._closed:
            return
        self._update_timer()
        self.root.after(1000, self._schedule_timer_update)  # Update every second

    def _update_timer(self) -> None:
        """Update countdown timer for current player."""
        import time

        # Only count down if game is active and not waiting for AI
        if self._check_game_over(show_dialog=False):
            return

        # Don't count down during AI thinking
        if self.options.mode == "ai" and self.state.side_to_move != self.options.human_side:
            return

        # Initialize last update time
        if self.last_timer_update is None:
            self.last_timer_update = time.time()
            self.timer_running = True
            return

        # Calculate elapsed time
        current_time = time.time()
        elapsed = current_time - self.last_timer_update
        self.last_timer_update = current_time

        # Decrement timer for current player
        if self.state.side_to_move == Side.RED:
            self.red_time_seconds = max(0, self.red_time_seconds - elapsed)
            self._update_timer_display(Side.RED)
        else:
            self.black_time_seconds = max(0, self.black_time_seconds - elapsed)
            self._update_timer_display(Side.BLACK)

        # Check for time out
        if self.red_time_seconds <= 0:
            self._set_status("Time out! Black wins!")
        elif self.black_time_seconds <= 0:
            self._set_status("Time out! Red wins!")

    def _update_timer_display(self, side: Side) -> None:
        """Update timer display and color based on remaining time."""
        if side == Side.RED:
            seconds = int(self.red_time_seconds)
            minutes = seconds // 60
            secs = seconds % 60
            self.red_time_var.set(f"{minutes}:{secs:02d}")

            # Change color if < 30 seconds
            if self.red_timer_frame and seconds < 30:
                self.red_timer_frame.config(bg="#b71c1c")  # Darker red (warning)
            elif self.red_timer_frame:
                self.red_timer_frame.config(bg="#d32f2f")  # Normal red
        else:
            seconds = int(self.black_time_seconds)
            minutes = seconds // 60
            secs = seconds % 60
            self.black_time_var.set(f"{minutes}:{secs:02d}")

            # Change color if < 30 seconds
            if self.black_timer_frame and seconds < 30:
                self.black_timer_frame.config(bg="#0d47a1")  # Darker blue (warning)
            elif self.black_timer_frame:
                self.black_timer_frame.config(bg="#1976D2")  # Normal blue
