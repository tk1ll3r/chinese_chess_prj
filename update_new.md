## Cập nhật mới

### 1. Hệ thống Elo Rating
- `chinese_chess_ai/rating/elo.py` — `EloSystem` quản lý rating (K=32, default 1500)
- `record_game(winner, loser)` / `record_draw(a, b)`
- Công thức: `R_new = R + K * (S - 1/(1+10^((R_b-R_a)/400)))`

### 2. UI Panel trái
- Avatar chữ Hán (帥/將) thay icon 👤
- ELO động màu gold, hiện +/- change 3s sau game
- Thanh progress timer (ttk.Progressbar)
- Accent màu xanh (Black) / đỏ (Red)

### 3. Timer Manager
- `timer_manager.py`: thêm `red_timer_bar` / `black_timer_bar`
- Progress bar giảm dần theo thời gian

### 4. Sửa lỗi & Tái cấu trúc
- `evaluate.py`: `mobility_score` dùng try/finally bảo vệ state
- `main.py`: xoá `render_board` trùng, dùng `GameState.render_ascii()`
- `engine/__init__.py` + `chinese_chess_ai/__init__.py`: export đầy đủ
- Tách `TimerManager` và `MoveHistory` khỏi `game_controller.py`
- `game_controller.py`: 846 → 811 dòng
