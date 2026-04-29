# Docstring DSA - Week 2

Tài liệu này tổng hợp các mẫu docstring ngắn gọn về cấu trúc dữ liệu và giải thuật
đang dùng trong project Cờ Tướng & AI tuần 2.

Mẫu chung:

```python
"""
def: ...

Role in System: ...

Input/Output: ...
"""
```

## 1. Docstring về Cấu trúc dữ liệu

### 1.1. Bàn cờ 10x9

```python
"""
def: Biểu diễn bàn cờ Cờ Tướng bằng ma trận 2 chiều 10x9.

Role in System: Là cấu trúc dữ liệu nền tảng để lưu vị trí quân cờ và hỗ trợ
truy xuất trạng thái bàn cờ theo tọa độ.

Input/Output: Input là chỉ số hàng và cột. Output là quân cờ tại ô tương ứng
hoặc giá trị rỗng nếu ô chưa có quân.
"""
```

### 1.2. Danh sách nước đi

```python
"""
def: Lưu tập các nước đi được sinh ra trong một lượt chơi.

Role in System: Hỗ trợ engine luật và AI duyệt qua các phương án nước đi có
thể thực hiện từ trạng thái hiện tại.

Input/Output: Input là các đối tượng Move được sinh ra từ bàn cờ hiện tại.
Output là danh sách nước đi phục vụ kiểm tra hợp lệ hoặc tìm kiếm AI.
"""
```

### 1.3. Lịch sử nước đi `move_history`

```python
"""
def: Lưu lịch sử các nước đi đã thực hiện theo cơ chế ngăn xếp.

Role in System: Hỗ trợ chức năng hoàn tác nước đi và quay lui trạng thái khi
thuật toán AI duyệt cây tìm kiếm.

Input/Output: Input là các bản ghi MoveRecord sau mỗi lần đi quân. Output là
trạng thái lịch sử dùng cho undo hoặc backtracking.
"""
```

### 1.4. Cấu trúc `GameState`

```python
"""
def: Lưu toàn bộ trạng thái hiện tại của ván cờ.

Role in System: Là trung tâm điều phối dữ liệu giữa phần luật chơi, AI, test
và giao diện.

Input/Output: Lưu bàn cờ, bên tới lượt, vị trí hai tướng và lịch sử nước đi.
Output là trạng thái hiện tại của hệ thống tại một thời điểm xác định.
"""
```

### 1.5. Cấu trúc `Move` và `MoveRecord`

```python
"""
def: Biểu diễn một nước đi và bản ghi chi tiết của nước đi đó.

Role in System: Giúp chuẩn hóa dữ liệu khi cập nhật trạng thái, kiểm tra luật
và hoàn tác nước đi.

Input/Output: Input là vị trí bắt đầu, vị trí kết thúc và các thông tin liên
quan. Output là dữ liệu chuẩn phục vụ engine và AI xử lý.
"""
```

## 2. Docstring về Giải thuật

### 2.1. Sinh nước đi giả hợp lệ

```python
"""
def: Sinh các nước đi theo quy tắc di chuyển của từng quân cờ.

Role in System: Tạo tập nước đi ban đầu trước khi hệ thống kiểm tra các điều
kiện an toàn tướng và luật đặc biệt.

Input/Output: Input là trạng thái bàn cờ và bên cần sinh nước đi. Output là
danh sách các nước đi giả hợp lệ.
"""
```

### 2.2. Lọc nước đi hợp lệ

```python
"""
def: Loại bỏ các nước đi dẫn đến trạng thái phạm luật.

Role in System: Đảm bảo danh sách nước đi cuối cùng chỉ gồm các nước không làm
tướng bị chiếu hoặc vi phạm luật hai tướng đối mặt.

Input/Output: Input là danh sách nước đi giả hợp lệ và trạng thái bàn cờ.
Output là danh sách nước đi hợp lệ hoàn toàn.
"""
```

### 2.3. Kiểm tra chiếu tướng

```python
"""
def: Xác định tướng của một bên có đang bị tấn công hay không.

Role in System: Hỗ trợ kiểm tra tính hợp lệ của bàn cờ và quyết định các nước
đi được phép thực hiện.

Input/Output: Input là trạng thái bàn cờ và bên cần kiểm tra. Output là giá
trị đúng/sai biểu diễn việc tướng có đang bị chiếu.
"""
```

### 2.4. Cơ chế `make_move` / `undo_move`

```python
"""
def: Áp dụng và hoàn tác nước đi trên trạng thái bàn cờ.

Role in System: Là nền tảng cho gameplay, lọc nước đi hợp lệ và quay lui khi
AI duyệt cây trạng thái.

Input/Output: Input là trạng thái hiện tại và một nước đi. Output là trạng
thái bàn cờ mới hoặc trạng thái được khôi phục sau khi hoàn tác.
"""
```

### 2.5. Hàm đánh giá heuristic

```python
"""
def: Chấm điểm một trạng thái bàn cờ bằng tương quan quân lực và vị trí.

Role in System: Cung cấp tiêu chí định lượng để AI so sánh các trạng thái và
lựa chọn nước đi tốt hơn.

Input/Output: Input là trạng thái bàn cờ và bên cần đánh giá. Output là điểm
số nguyên biểu diễn mức lợi thế của trạng thái đó.
"""
```

### 2.6. Heuristic search / Negamax

```python
"""
def: Duyệt cây trạng thái để chọn nước đi tốt nhất cho AI.

Role in System: Kết hợp sinh nước đi, đánh giá heuristic và quay lui trạng
thái để tìm ra phương án có lợi nhất trong phạm vi độ sâu cho phép.

Input/Output: Input là trạng thái bàn cờ hiện tại và cấu hình tìm kiếm.
Output là nước đi được AI lựa chọn.
"""
```

## 3. Gợi ý dùng trong báo cáo

Nếu cần đưa vào báo cáo tuần 2, có thể chọn 3 nhóm tiêu biểu:

- `GameState` đại diện cho cấu trúc dữ liệu trung tâm.
- `move_history` đại diện cho stack/backtracking.
- `evaluate_position` hoặc `choose_move` đại diện cho heuristic và AI search.
