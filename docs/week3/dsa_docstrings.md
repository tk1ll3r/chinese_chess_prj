# Docstring DSA - Week 3

Tài liệu này bổ sung các mẫu docstring ngắn gọn cho phần mở rộng tuần 3 của project Cờ Tướng: GUI, AI theo độ khó và LAN MVP. Mẫu được giữ thống nhất với file tuần 2.

Mẫu chung:

```python
"""
def: ...

Role in System: ...

Input/Output: ...
"""
```

## 1. Docstring về GUI

### 1.1. `GameOptions`

```python
"""
def: Lưu cấu hình khởi tạo cho một ván chơi trong giao diện.

Role in System: Cho phép menu truyền chế độ chơi, bên người chơi, độ khó AI
hoặc room code LAN vào game controller mà không phụ thuộc chi tiết UI.

Input/Output: Input là các lựa chọn từ menu. Output là một cấu hình bất biến
được dùng để dựng đúng chế độ chơi.
"""
```

### 1.2. `GameController`

```python
"""
def: Điều phối toàn bộ luồng chơi trong GUI Tkinter.

Role in System: Kết nối engine luật, AI search, network transport và board view
để xử lý click, cập nhật trạng thái, undo, restart, lịch sử nước đi và kết thúc ván.

Input/Output: Input là root Tkinter, GameOptions và callback quay về menu.
Output là trạng thái giao diện được cập nhật sau mỗi sự kiện người chơi, AI hoặc LAN.
"""
```

### 1.3. `BoardView`

```python
"""
def: Vẽ bàn cờ, quân cờ và các hiệu ứng tương tác trên canvas.

Role in System: Tách phần hiển thị khỏi logic điều khiển, giúp controller chỉ
truyền trạng thái cần vẽ như ô đang chọn, nước hợp lệ và Tướng bị chiếu.

Input/Output: Input là GameState cùng dữ liệu highlight. Output là canvas đã
được render lại theo trạng thái hiện tại.
"""
```

### 1.4. Ánh xạ `board_point` / `pixel_to_position`

```python
"""
def: Chuyển đổi giữa tọa độ bàn cờ và tọa độ pixel trên giao diện.

Role in System: Cho phép GUI đặt quân đúng vị trí và xác định ô bàn cờ gần nhất
khi người chơi click chuột.

Input/Output: Input là position hoặc cặp pixel x/y. Output là tọa độ canvas
hoặc vị trí hàng/cột hợp lệ trên bàn cờ.
"""
```

## 2. Docstring về AI search mở rộng

### 2.1. `SearchConfig`

```python
"""
def: Lưu cấu hình tìm kiếm của AI như độ sâu và trạng thái bật alpha-beta.

Role in System: Kết nối lựa chọn độ khó trong menu với thuật toán search mà
không cần sửa trực tiếp logic AI.

Input/Output: Input là lựa chọn Easy/Medium/Hard. Output là cấu hình depth và
use_alpha_beta dùng trong choose_move.
"""
```

### 2.2. `TranspositionEntry`

```python
"""
def: Lưu kết quả đánh giá một trạng thái đã duyệt trong bảng chuyển vị.

Role in System: Giúp AI tái sử dụng điểm số và nước tốt nhất của trạng thái
đã gặp, giảm số lần tính lại khi duyệt cây trò chơi.

Input/Output: Input là depth, score, loại bound và best_move. Output là bản ghi
cache phục vụ negamax và move ordering.
"""
```

### 2.3. `_ordered_moves`

```python
"""
def: Sắp xếp các nước đi hợp lệ trước khi đưa vào negamax.

Role in System: Ưu tiên nước bắt quân giá trị cao hoặc nước đã được cache để
tăng khả năng cắt tỉa alpha-beta sớm.

Input/Output: Input là GameState, danh sách Move và preferred_move tùy chọn.
Output là danh sách Move đã được sắp xếp theo mức ưu tiên.
"""
```

## 3. Docstring về networking và LAN MVP

### 3.1. `NetworkState`

```python
"""
def: Đóng gói trạng thái bàn cờ và dữ liệu phụ trợ cần đồng bộ qua mạng.

Role in System: Là dữ liệu trung gian giữa payload JSON và GameController khi
host gửi trạng thái mới cho client.

Input/Output: Input là payload đã deserialize. Output là GameState, lịch sử
nước đi, danh sách quân bị bắt và thông báo trạng thái.
"""
```

### 3.2. Serialize/deserialize protocol

```python
"""
def: Chuyển đổi Piece, Move và GameState giữa object Python và payload JSON.

Role in System: Chuẩn hóa dữ liệu truyền qua TCP để host và client có thể hiểu
cùng một trạng thái bàn cờ.

Input/Output: Input là object engine hoặc payload dict. Output là dict JSON-safe
hoặc object Python tương ứng.
"""
```

### 3.3. `NetworkTransport`, `HostTransport`, `ClientTransport`

```python
"""
def: Định nghĩa interface chung cho các kênh mạng của chế độ multiplayer.

Role in System: Tách GameController khỏi chi tiết socket, giúp GUI chỉ gọi các
hành động mức cao như start, close, submit_local_move hoặc send_move.

Input/Output: Input là thao tác mạng từ GUI. Output là contract trừu tượng để
host/client cụ thể triển khai.
"""
```

### 3.4. `LanGameServer`

```python
"""
def: Chạy TCP server có thẩm quyền cho một phòng Cờ Tướng LAN hai người.

Role in System: Host giữ trạng thái chính, kiểm tra lượt đi và nước hợp lệ,
rồi broadcast trạng thái mới cho client sau mỗi nước được chấp nhận.

Input/Output: Input là kết nối client và các message move. Output là payload
state hoặc error gửi lại cho client và GUI host.
"""
```

### 3.5. `LanGameClient`

```python
"""
def: Kết nối tới host LAN và gửi/nhận message TCP của ván cờ.

Role in System: Cho phép người chơi join gửi nước đi lên host và nhận trạng
thái bàn cờ đã được xác thực.

Input/Output: Input là host, port và Move cần gửi. Output là các callback
message, status hoặc error cho GUI.
"""
```

### 3.6. `RoomAnnouncement` và `LanRoomBroadcaster`

```python
"""
def: Mô tả và phát thông tin phòng LAN bằng UDP broadcast.

Role in System: Giúp client tìm host theo room code mà người chơi không cần
nhập IP thủ công.

Input/Output: Input là room_code, tcp_port và thông tin host. Output là packet
announcement được broadcast định kỳ trong LAN.
"""
```

### 3.7. `discover_room` / `select_room_candidate`

```python
"""
def: Thu thập thông báo phòng LAN và chọn host phù hợp với room code.

Role in System: Là bước tìm phòng trước khi client mở kết nối TCP tới host.
Hàm cũng phát hiện trường hợp không có phòng hoặc trùng room code.

Input/Output: Input là room_code, danh sách announcement và thời gian TTL.
Output là RoomAnnouncement hợp lệ hoặc lỗi RoomDiscoveryError.
"""
```

## 4. Gợi ý dùng trong báo cáo tuần 3

- `GameController` đại diện cho phần điều phối GUI, AI và LAN.
- `NetworkState` đại diện cho cấu trúc dữ liệu đồng bộ trạng thái qua mạng.
- `LanGameServer` đại diện cho mô hình host-authoritative trong LAN MVP.
- `SearchConfig` và `TranspositionEntry` đại diện cho AI theo độ khó và tối ưu search.
