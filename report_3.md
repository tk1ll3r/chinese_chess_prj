# BÁO CÁO ĐỒ ÁN MÔN HỌC - TUẦN 3
(Đồ án phát triển ứng dụng) Lớp: IT003.Q21.CTTN

## Sinh viên thực hiện
Mã sinh viên: 25521829  
Họ và tên: Nguyễn Văn Thương

## Tên đề tài
**BINH PHÁP 5.0**

## 1. Giới thiệu đồ án
Đồ án xây dựng game Cờ Tướng có khả năng quản lý trạng thái ván cờ, kiểm tra luật chơi, hỗ trợ AI chọn nước đi và mở rộng sang giao diện chơi thực tế. Trong tuần 3, trọng tâm chuyển từ lõi engine tuần 2 sang hoàn thiện trải nghiệm người chơi: menu, chế độ chơi với AI, chơi 2 người cùng máy, LAN MVP, tài liệu hướng dẫn và kiểm thử mở rộng.

## 2. Cấu trúc dữ liệu và giải thuật đã sử dụng
### Cấu trúc dữ liệu
- **Ma trận 2 chiều 10x9**: biểu diễn bàn cờ theo hàng/cột, giúp truy xuất quân cờ nhanh và phù hợp với kích thước bàn Cờ Tướng.
- **Enum và dataclass**: dùng cho `Side`, `PieceKind`, `Piece`, `Move`, `MoveRecord`, `GameState`, `GameOptions`, `NetworkState`, giúp dữ liệu rõ nghĩa và hạn chế lỗi truyền sai kiểu.
- **Danh sách động (`list`)**: lưu nước đi hợp lệ, lịch sử nước đi hiển thị, danh sách quân bị bắt, danh sách thông báo phòng LAN.
- **Stack (`move_history`)**: lưu lịch sử theo cơ chế LIFO để undo và backtracking trong AI search.
- **Queue sự kiện GUI/network**: gom sự kiện từ thread LAN rồi xử lý an toàn ở luồng Tkinter chính.
- **Dictionary/hash table**: dùng cho payload JSON, tra cứu nước đi hợp lệ, bảng chuyển vị trong AI và phát hiện trùng room code LAN.
- **Socket TCP/UDP**: TCP đồng bộ nước đi giữa host-client, UDP broadcast để tìm phòng theo room code trong cùng LAN.

### Giải thuật
- **Sinh và lọc nước đi hợp lệ**: tiếp tục dùng engine luật để đảm bảo mọi chế độ chơi đều chỉ nhận nước đi đúng luật.
- **Negamax + alpha-beta pruning**: AI tìm nước đi theo độ sâu cấu hình, giảm số nhánh cần duyệt bằng cắt tỉa alpha-beta.
- **Move ordering và transposition table**: ưu tiên nước bắt quân/cache nước tốt để tăng hiệu quả tìm kiếm.
- **Serialize/deserialize trạng thái**: chuyển `GameState`, nước đi, lịch sử và quân bị bắt thành payload JSON để đồng bộ qua mạng.
- **LAN room discovery**: host broadcast thông tin phòng, client thu thập thông báo theo TTL và chọn đúng phòng theo room code.
- **Host-authoritative validation**: host kiểm tra lượt đi và nước hợp lệ trước khi cập nhật/broadcast trạng thái.
- **Ánh xạ tọa độ GUI**: đổi vị trí bàn cờ sang pixel và ngược lại để xử lý click, highlight quân được chọn và ô đi hợp lệ.

## 3. Quá trình thực hiện
### Tuần 1
- Tìm hiểu luật Cờ Tướng và xác định phạm vi kỹ thuật của đồ án.
- Tổ chức kiến trúc tách engine, AI và giao diện.
- Xây dựng khung project, các kiểu dữ liệu nền tảng và trạng thái ban đầu.

### Tuần 2
- Hoàn thiện `GameState`, bàn cờ 10x9, lượt đi, vị trí hai tướng và lịch sử nước đi.
- Cài đặt `make_move` / `undo_move` phục vụ gameplay, kiểm tra luật và backtracking.
- Xây dựng rules engine: sinh nước đi cho từng quân, xử lý Mã cản chân, Tượng cản mắt, Pháo cần ngòi, Tướng trong cung và luật hai Tướng đối mặt.
- Lọc nước đi hợp lệ bằng mô phỏng trạng thái, loại bỏ nước khiến Tướng bị chiếu.
- Khởi tạo AI heuristic bằng `material_score`, `positional_score`, `evaluate_position` và search cơ bản.

### Tuần 3
- Hoàn thiện menu chính với các lựa chọn: chơi 2 người cùng máy, chơi với AI, chơi qua LAN và thoát.
- Tích hợp chế độ chơi với AI: người chơi chọn Đỏ/Đen, chọn độ khó Easy/Medium/Hard tương ứng depth 1/2/3.
- Nâng cấp UX ván cờ: highlight quân đang chọn, highlight ô đi hợp lệ, hiển thị lượt đi, lịch sử nước đi, quân bị bắt và trạng thái kết thúc ván.
- Bổ sung UX khi bị chiếu: tô sáng Tướng bị chiếu, nhấp nháy cảnh báo và chỉ cho phép nước thoát chiếu.
- Xây dựng LAN MVP: host tạo room code ngắn, client join bằng room code, tìm phòng bằng UDP broadcast và đồng bộ bàn cờ bằng TCP.
- Thiết kế tầng `NetworkTransport` để tách GUI khỏi chi tiết host/client, giúp controller dùng chung cho local, AI và LAN.
- Cập nhật tài liệu `README.md` và `HUONG_DAN_CHOI.md` để hướng dẫn chạy game, chơi AI và chơi LAN.
- Mở rộng test cho GUI rendering, networking serialization, room code/discovery, rules, state và search.
- Bổ sung phần docstring tuần 3 theo mẫu `def / Role in System / Input/Output` cho các nhóm GUI, AI search và LAN networking.

## 4. Kết quả đạt được
- Game đã có giao diện menu và các chế độ chơi cơ bản thay vì chỉ dừng ở engine/CLI.
- Người chơi có thể chơi 2 người cùng máy, chơi với AI theo độ khó hoặc thử chế độ LAN MVP trong cùng mạng nội bộ.
- AI sử dụng lại engine sinh nước đi hợp lệ nên không đi sai luật, đồng thời có cấu hình độ sâu rõ ràng.
- LAN MVP đã có luồng host-client, room code, phát hiện phòng, xác thực nước đi ở host và đồng bộ trạng thái sau mỗi nước hợp lệ.
- Tài liệu hướng dẫn chơi và README đã được cập nhật để người dùng có thể chạy, test và hiểu giới hạn hiện tại của bản MVP.

## 5. Kiểm thử
Lệnh đã chạy:

```bash
python -m unittest discover -s tests
```

Kết quả: **29 tests pass** trong khoảng **0.3s**. Các nhóm test bao phủ trạng thái bàn cờ, luật chơi, AI search, GUI rendering và networking.

## 6. Tài liệu tham khảo
- Repo tham khảo: Dylannni/ChineseChess_XiangQi.
- Mã nguồn dự án: [tk1ll3r/chinese_chess_prj](https://github.com/tk1ll3r/chinese_chess_prj).
- Docstring tuần 2: [docs/week2/dsa_docstrings.md](docs/week2/dsa_docstrings.md).
- Docstring tuần 3: [docs/week3/dsa_docstrings.md](docs/week3/dsa_docstrings.md).

## Phụ lục 1: Demo kết quả
- **Hình 1: Menu chính** - hiển thị các chế độ chơi: local, AI, LAN và thoát.
- **Hình 2: Chế độ chơi với AI** - người chơi chọn bên và độ khó trước khi bắt đầu.
- **Hình 3: Giao diện ván cờ** - có bàn cờ, quân cờ, lịch sử nước đi, quân bị bắt, trạng thái lượt và cảnh báo chiếu.
- **Hình 4: LAN MVP** - host tạo room code, client nhập code để tham gia và bàn cờ đồng bộ sau mỗi nước.
- **Hình 5: Unit test** - toàn bộ 29 test pass, xác nhận các module cốt lõi hoạt động ổn định.

## Phụ lục 2: Docstring
Phần docstring tiếp tục dùng mẫu chuẩn:

```python
"""
def: ...

Role in System: ...

Input/Output: ...
"""
```

Tuần 3 tập trung ghi docstring cho các nhóm mới hoặc được mở rộng: `GameController`, `BoardView`, `SearchConfig`, `TranspositionEntry`, `NetworkState`, `NetworkTransport`, `LanGameServer`, `LanGameClient`, `LanRoomTransport`, `RoomAnnouncement`, cơ chế serialize/deserialize và room discovery. Nội dung chi tiết được lưu tại `docs/week3/dsa_docstrings.md`.
