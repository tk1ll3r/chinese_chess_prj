# Chinese Chess Project

Chinese Chess/Xiangqi project with a rules engine, enhanced AI search, Tkinter GUI, sound effects, and LAN multiplayer mode.

## Features

### Core Gameplay
- Opening menu:
  - Chơi 2 người cùng máy
  - Chơi với AI
  - Chơi 2 người qua LAN
  - Settings
  - Thoát
- Local two-player mode with alternating turns, restart, undo, and back to menu
- AI mode with side selection and difficulty:
  - Easy: depth 1
  - Medium: depth 2
  - Hard: depth 3
- Check UX:
  - Highlights the checked general with pulse effect
  - Blinking red outline and `Chiếu tướng!` banner
  - Warns: `Bạn đang bị chiếu, phải đi nước thoát chiếu!`
- Gameplay UX:
  - Highlights selected piece
  - Highlights legal destinations
  - Shows current turn, move history, captured pieces, and game-over status
  - Keyboard shortcuts: Ctrl+Z (undo), Ctrl+R (restart), Escape (back to menu)

### Enhanced Features (New!)
- **Sound Effects**: 7 sound effects for moves, captures, checks, checkmate, selection, illegal moves, and button clicks
- **Visual Animations**: Smooth piece movement, capture flash effects, improved check pulse animation
- **Advanced AI**:
  - Piece-square tables for positional evaluation
  - Mobility and king safety evaluation
  - Quiescence search for tactical positions
  - Killer move heuristic for better move ordering
  - Iterative deepening support
- **Opening Book**: Simple opening book system for common opening moves
- **Settings Menu**: Volume control, sound toggle, animation settings
- **Game Database**: Save and load games in simple text format

### LAN Multiplayer
- Host creates a short room code
- Join uses only the room code in the UI
- The LAN transport discovers rooms with UDP broadcast and then connects to the matching host
- Host is authoritative and validates every move
- Board state synchronizes after each accepted move

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

Start the GUI menu:

```bash
python3 main.py
```

Equivalent explicit command:

```bash
python3 main.py gui
```

Run the CLI modes:

```bash
python3 main.py cli
python3 main.py ai
python3 main.py summary
```

Run all tests:

```bash
python3 -m unittest discover -s tests
```

## How To Play

Hướng dẫn chi tiết bằng tiếng Việt có trong
[`HUONG_DAN_CHOI.md`](HUONG_DAN_CHOI.md).

### 2 Người Cùng Máy

1. Run `python3 main.py`.
2. Choose `Chơi 2 người cùng máy`.
3. Click a piece of the side to move, then click a highlighted destination.
4. Use `Restart`, `Undo`, or `Back to Menu` from the sidebar.

### Chơi Với AI

1. Run `python3 main.py`.
2. Choose `Chơi với AI`.
3. Select your side: `Red` or `Black`.
4. Select AI difficulty: `Easy`, `Medium`, or `Hard`.
5. Start the game. If you choose Black, AI Red moves first.

The AI uses the existing engine legal-move generator, so it only plays legal
moves.

### LAN Multiplayer MVP

Host:

1. Run `python3 main.py`.
2. Choose `Chơi 2 người qua LAN`.
3. Click `Create Room`.
4. Share the generated room code.
5. The host plays Red.

Join:

1. Run `python3 main.py` on another machine in the same LAN.
2. Choose `Chơi 2 người qua LAN`.
3. Enter the shared room code.
4. Click `Join Room`.
5. The joining player plays Black.

LAN notes:

- The host validates moves and broadcasts the board after each accepted move.
- The MVP supports basic play over TCP on a local network.
- The room code works only on the same LAN in the MVP build.
- Discovery uses LAN broadcast, so this is not Internet matchmaking yet.
- Undo/restart are disabled in LAN mode for now; return to menu and host/join a
  new game when needed.

## Project Structure

```text
chinese_chess_ai/
├── ai/
│   ├── evaluate.py          # Enhanced evaluation with PST, mobility, king safety
│   ├── search.py            # Negamax with quiescence, killer moves, iterative deepening
│   ├── piece_square_tables.py  # Positional evaluation tables
│   └── opening_book.py      # Opening book system
├── audio/
│   └── sound_manager.py     # Sound effects manager
├── database/
│   └── __init__.py          # Game save/load system
├── engine/
│   ├── constants.py
│   ├── moves.py
│   ├── rules.py
│   ├── state.py
│   └── types.py
├── gui/
│   ├── board_view.py        # Board rendering with animations
│   ├── game_controller.py   # Game logic with sound integration
│   ├── menu.py
│   ├── settings_menu.py     # Settings UI
│   └── tk_gui.py
└── network/
    ├── client.py
    ├── protocol.py
    └── server.py

assets/
├── sounds/                   # Sound effect files (.wav)
└── xqwizard_gui/            # Board and piece images

data/
├── opening_book.json        # Opening book database
└── games/                   # Saved games directory
```

## Implementation Notes

- GUI and network code call the engine/rules layer instead of duplicating chess rules
- `generate_legal_moves()` filters out moves that leave the moving side in check
- `is_in_check()` drives the check warning and board highlight
- Enhanced AI evaluation includes piece-square tables, mobility, and king safety
- Quiescence search extends tactical sequences (captures and checks)
- Sound system gracefully falls back if pygame is unavailable
- `NetworkTransport` abstracts multiplayer transport away from the game controller
- `LanRoomTransport` discovers LAN rooms by broadcast and keeps TCP board sync after each move

## New Features Details

### Sound System
- 7 sound effects: move, capture, check, checkmate, select, illegal, button
- Volume control via settings menu
- Graceful fallback if pygame unavailable
- Lazy loading for performance

### Enhanced AI
- **Evaluation improvements**: Piece-square tables, mobility scoring, king safety
- **Search enhancements**: Quiescence search, killer move heuristic, iterative deepening
- **Opening book**: Simple JSON-based opening book for common positions
- Significantly stronger play at same depth

### Visual Improvements
- Smooth piece movement animations (250ms)
- Capture flash effects
- Improved check highlight with pulse effect
- Better visual feedback

### Settings & Persistence
- Settings menu for sound and animation control
- Game database for saving/loading games
- Opening book system for AI improvement

## Performance

- AI depth 3 with enhancements: ~1-2s per move
- Quiescence search adds tactical awareness without significant slowdown
- Transposition table and killer moves improve pruning efficiency
- Target: 60fps for animations
