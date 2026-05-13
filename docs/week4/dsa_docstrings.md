# Docstring DSA - Week 4

Tài liệu này bổ sung các mẫu docstring ngắn gọn cho phần mở rộng tuần 4 của project Cờ Tướng: ElephantEye UCCI engine, ELO Rating, Timer Manager, Board Flip và MoveHistory. Mẫu được giữ thống nhất với file tuần 2 và tuần 3.

Mẫu chung:

```python
"""
def: ...

Role in System: ...

Input/Output: ...
"""
```

## 1. Docstring về Cấu trúc dữ liệu

### 1.1. Biểu diễn FEN (FEN String)

```python
"""
def: Mã hóa toàn bộ bàn cờ 10×9 thành chuỗi văn bản theo chuẩn Forsyth–Edwards Notation.

Role in System: Là cấu trúc dữ liệu trung gian để giao tiếp giữa game Python và ElephantEye
engine (C++) qua UCCI protocol. Cho phép engine ngoài tái tạo trạng thái bàn cờ chính xác
mà không cần import code Python.

Input/Output: Input là ma trận 10×9 (2D Array) chứa Piece hoặc None. Output là chuỗi FEN
gồm board layout (10 hàng cách nhau bằng /, ô trống gộp thành số), bên đi tiếp (w/b),
và các trường phụ "- - 0 1".
"""
```

### 1.2. `RatingChange`

```python
"""
def: Lưu kết quả thay đổi ELO rating sau một ván đấu.

Role in System: Ghi lại rating cũ, mới và độ chênh lệch (delta) của cả hai người chơi
sau mỗi trận. Dùng để hiển thị thông báo +/- trên giao diện.

Input/Output: Chứa player_rating, opponent_rating, player_new_rating, opponent_new_rating,
player_delta và opponent_delta. Output là bản ghi bất biến (dataclass) phục vụ UI.
"""
```

### 1.3. `MoveHistory`

```python
"""
def: Lưu lịch sử nước đi và danh sách quân bị bắt của ván cờ.

Role in System: Cung cấp dữ liệu hiển thị cho UI panel bên trái và hỗ trợ chức năng
undo. Dùng Stack (list) để lưu các nước đi theo thứ tự thời gian, mỗi nước là một
string mô tả số thứ tự, bên đi, tọa độ và quân bị bắt (nếu có).

Input/Output: Input là Move, Side, captured_piece từ game controller sau mỗi nước
đi hợp lệ. Output là danh sách move strings và captured lists cho UI render.
"""
```

## 2. Docstring về Giải thuật

### 2.1. Mã hóa FEN (`_state_to_fen`)

```python
"""
def: Chuyển đổi ma trận 2 chiều 10×9 thành chuỗi FEN.

Role in System: Duyệt 2D Array từ trên xuống, gộp ô trống liên tiếp thành số,
chuyển PieceKind thành ký tự (chữ hoa = Đỏ, chữ thường = Đen), nối các hàng
bằng '/'. Đây là bước tiền xử lý bắt buộc trước khi gọi ElephantEye.

Input/Output: Input là GameState (chứa board 10×9). Output là string FEN ví dụ:
"rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1".
"""
```

### 2.2. Giao thức UCCI (`EleeyeEngine`)

#### 2.2.1. Khởi tạo và bắt tay (`__init__`, `_start`, `_init_ucci`)

```python
"""
def: Khởi động tiến trình ElephantEye (C++) và thực hiện bắt tay UCCI protocol.

Role in System: Mở subprocess pipe (đọc/ghi qua stdin/stdout) tới binary ElephantEye.
Gửi lệnh "ucci" và chờ "ucciok", sau đó cấu hình hash size và chờ "readyok".
Dùng mutex (threading.Lock) để đảm bảo an toàn khi nhiều luồng gọi đồng thời.

Input/Output: Input là đường dẫn engine binary. Output là subprocess Popen sẵn sàng
nhận lệnh position/go.
"""
```

#### 2.2.2. `_send` / `_read_line` / `_recv_until` / `_drain`

```python
"""
def: Giao tiếp dòng lệnh với ElephantEye qua stdin/stdout pipe.

Role in System: _send ghi lệnh + newline vào stdin. _read_line đọc từ stdout bằng
select + os.read (non-blocking I/O) với timeout, dùng buffer nhị phân. _recv_until
đọc liên tục đến khi gặp dòng target. _drain xóa bộ đệm đọc để đồng bộ trạng thái.
Đây là cơ chế pipe-based IPC cơ bản giữa Python và tiến trình C++.

Input/Output: Input là lệnh UCCI string. Output là dòng phản hồi từ engine hoặc
TimeoutError nếu quá thời gian chờ.
"""
```

#### 2.2.3. `choose_move` / `_search`

```python
"""
def: Gọi ElephantEye tìm nước đi tốt nhất cho trạng thái hiện tại.

Role in System: Chuyển GameState → FEN, gửi lệnh "position fen ..." + "go depth/time",
đọc kết quả "bestmove ..." từ stdout. Nếu engine lỗi (BrokenPipeError), tự động
khởi động lại và thử lại. Fallback về nước hợp lệ đầu tiên nếu engine không trả
kết quả. Đây là giao diện giữa game Python và thuật toán AI C++ (DFS + alpha-beta
+ transposition table + iterative deepening của ElephantEye).

Input/Output: Input là GameState, depth (int) hoặc time_limit (float giây). Output là
Move được engine chọn hoặc None nếu không còn nước đi.
"""
```

#### 2.2.4. `evaluate` / `_quick_eval`

```python
"""
def: Đánh giá thế cờ nhanh qua ElephantEye ở depth 1.

Role in System: Gửi "go depth 1" và phân tích dòng "score" trong output để lấy
điểm đánh giá. Dùng blocking lock hoặc non-blocking tùy tham số. Kết quả là
float dương nếu Đỏ lợi, âm nếu Đen lợi. Đây là hàm heuristic evaluation gọi
engine ngoài, thay thế evaluate tự viết ở tuần 2-3.

Input/Output: Input là GameState, blocking (bool). Output là float (centipawn/100)
hoặc None nếu không acquire được lock (non-blocking mode).
"""
```

### 2.3. ELO Rating (`EloSystem`)

#### 2.3.1. Công thức kỳ vọng (`expected_score`)

```python
"""
def: Tính xác suất kỳ vọng người chơi A thắng người chơi B dựa trên chênh lệch rating.

Role in System: Dùng công thức E_a = 1 / (1 + 10^((R_b - R_a) / 400)). Đây là
hàm sigmoid (logistic) chuẩn hóa chênh lệch rating về khoảng [0, 1]. Nếu hai
người bằng điểm, E = 0.5. Chênh lệch 400 điểm → E ≈ 0.91.

Input/Output: Input là rating_a và rating_b (int). Output là float trong [0, 1].
"""
```

#### 2.3.2. Cập nhật rating (`update_rating`)

```python
"""
def: Tính rating mới sau một trận đấu theo công thức ELO.

Role in System: R_new = R + K × (S - E), với K = 32, S = 1 (thắng) / 0.5 (hòa) / 0 (thua).
Đây là thuật toán cập nhật động dùng hệ số K để điều chỉnh mức độ ảnh hưởng
của mỗi trận. Rating được lưu trong Hash Table (Dict[str, int]).

Input/Output: Input là player_rating, opponent_rating (int) và score (float 0/0.5/1).
Output là rating mới (int) đã làm tròn.
"""
```

#### 2.3.3. `record_game` / `record_draw`

```python
"""
def: Ghi nhận kết quả thắng/thua hoặc hòa và cập nhật rating cho cả hai người chơi.

Role in System: Tính rating mới cho cả winner và loser (hoặc hòa), lưu vào
Hash Table ratings theo player_id, trả về RatingChange chứa delta để UI hiển thị.
Dùng List (hoặc dict) để quản lý nhiều người chơi.

Input/Output: Input là winner_id, loser_id (hoặc player_a_id, player_b_id).
Output là RatingChange dataclass với rating cũ, mới và chênh lệch.
"""
```

### 2.4. Timer Countdown (`TimerManager`)

#### 2.4.1. `reset` / `start`

```python
"""
def: Khởi tạo và bắt đầu bộ đếm giờ cho mỗi bên.

Role in System: reset đưa thời gian hai bên về 10:00 (600 giây), tắt trạng thái
chạy. start ghi timestamp hiện tại (time.time()) để bắt đầu đếm. Dùng biến
thời gian thực float thay vì threading.Timer để tránh trôi đồng hồ.

Input/Output: Input là không có. Output là trạng thái timer sẵn sàng chạy.
"""
```

#### 2.4.2. `update`

```python
"""
def: Cập nhật thời gian còn lại của bên đang đi mỗi frame.

Role in System: Tính elapsed = now - last_timestamp (sai số ~16ms cho 60 FPS),
trừ vào thời gian bên đang đi. Cập nhật StringVar và Progressbar trên UI.
Khi hết giờ (≤ 0), trả về thông báo "Time out!" để kết thúc ván.
Đây là thuật toán countdown real-time dùng timestamp polling.

Input/Output: Input là side_to_move (Side.RED / Side.BLACK). Output là string
thông báo hết giờ hoặc None nếu vẫn còn thời gian.
"""
```

### 2.5. Board Flip (`_flip_coord` / `_flip_position`)

```python
"""
def: Biến đổi tọa độ hàng để xoay bàn cờ 180° khi chơi bên Đen.

Role in System: Phép biến hình (row, col) → (9 - row, 8 - col) [thực tế chỉ lật
hàng vì cột không đổi do đối xứng]. Khi người chơi cầm quân Đen, toàn bộ tọa
độ render được lật để quân Đen ở dưới và quân Đỏ ở trên. Áp dụng cho: vị trí
quân, ô đang chọn, nước đi hợp lệ, và highlight chiếu tướng.

Input/Output: Input là row (int) hoặc Position (row, col). Output là tọa độ đã
biến đổi dùng cho canvas render.
"""
```

### 2.6. MoveHistory

#### 2.6.1. `record`

```python
"""
def: Ghi lại một nước đi và quân bị bắt (nếu có) vào lịch sử.

Role in System: Mỗi nước đi hợp lệ được ghi thành string format:
"<số>. <tên> <bên>: (r1,c1) -> (r2,c2) x <quân bị bắt>".
Dùng List (stack) để lưu moves và captured_by_red/captured_by_black.
Nếu có quân bị bắt, thêm vào danh sách quân bị bắt tương ứng.

Input/Output: Input là side, Move, captured_piece, actor name, và các hàm hiển
thị piece/side. Output là string đã thêm vào self.moves list.
"""
```

#### 2.6.2. `remove_last_capture` / `clear`

```python
"""
def: Xóa quân bị bắt cuối cùng (khi undo) hoặc xóa toàn bộ lịch sử.

Role in System: Khi undo một nước đi, quân bị bắt cần được đưa lại về bàn cờ,
vì vậy phải xóa khỏi danh sách captured tương ứng. clear reset toàn bộ moves
và captured lists cho ván mới.

Input/Output: Input là side (cho remove_last_capture). Output là list được cập
nhật (pop hoặc clear).
"""
```

## 3. Tổng hợp DSA cho tuần 4

| CTDL/Giải thuật | Ứng dụng | File |
|---|---|---|
| **FEN String** | Mã hóa board → string giao tiếp ElephantEye | `eleeye_engine.py:_state_to_fen` |
| **Hash Table (Dict)** | Lưu ELO rating theo player_id | `elo.py:EloSystem._ratings` |
| **Stack (List)** | Lưu lịch sử nước đi cho undo/UI | `move_history.py:MoveHistory.moves` |
| **Subprocess Pipe** | IPC giữa Python và C++ (stdin/stdout) | `eleeye_engine.py:EleeyeEngine` |
| **UCCI Protocol** | Giao thức điều khiển engine Cờ Tướng | `eleeye_engine.py` |
| **ELO Rating** | Tính điểm dùng logistic + K-factor | `elo.py:EloSystem` |
| **Timestamp Polling** | Đếm ngược real-time dùng time.time() | `timer_manager.py:TimerManager` |
| **Phép biến hình (Coordinate Transform)** | Lật tọa độ 180° cho bên Đen | `board_view.py:_flip_coord` |
| **DFS + Alpha-Beta Pruning** | Tìm kiếm trên cây trò chơi (ElephantEye C++) | engine ngoài |
| **Move Ordering (Heuristic)** | Ưu tiên nước ăn quân, killer moves | engine ngoài |
| **Transposition Table (Memoization)** | Cache kết quả vị thế đã duyệt (Zobrist hash) | engine ngoài |
| **Iterative Deepening DFS** | Tăng dần depth, fallback khi hết thời gian | engine ngoài |
| **Cycle Detection** | Phát hiện repetition / perpetual check | engine ngoài |
| **Lazy Evaluation** | Đánh giá 4 mức từ thô → tinh, dừng sớm | engine ngoài |
| **Piece-Square Tables** | Bảng điểm vị trí 10×9 cho từng quân | engine ngoài |
| **Selective Extension** | Mở rộng depth khi bị chiếu hoặc chỉ 1 nước | engine ngoài |

## 4. Gợi ý dùng trong báo cáo tuần 4

- `_state_to_fen` đại diện cho FEN Encoding — biểu diễn trạng thái bàn cờ dạng string.
- `EleeyeEngine.choose_move` đại diện cho giao tiếp UCCI và gọi AI C++.
- `EloSystem` đại diện cho Hash Table và công thức ELO (logistic + K-factor).
- `TimerManager.update` đại diện cho timestamp polling và countdown real-time.
- `_flip_coord` đại diện cho phép biến hình tọa độ (board flip).
- `MoveHistory` đại diện cho Stack lưu lịch sử nước đi và undo.
- ElephantEye (engine ngoài) đại diện cho DFS + alpha-beta pruning, transposition table, iterative deepening, lazy evaluation và các kỹ thuật tối ưu search trên cây trò chơi.
