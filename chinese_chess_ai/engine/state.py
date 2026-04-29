from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from .constants import BOARD_COLS, BOARD_ROWS, INITIAL_PLACEMENTS
from .moves import Move, MoveRecord
from .types import Piece, PieceKind, Position, Side

Board = list[list[Piece | None]]
Placement = tuple[Side, PieceKind, int, int]


def _validate_position(position: Position) -> None:
    """def: Kiểm tra một tọa độ có nằm trong phạm vi bàn cờ 10x9 hay không.

    Role in System: Bảo vệ các hàm truy cập trạng thái khỏi lỗi truy cập sai
    chỉ số mảng.
    Input/Output: Input là `position` dưới dạng `(row, col)`. Output là
    `None`; hàm phát sinh `ValueError` nếu tọa độ vượt biên bàn cờ.
    """
    row, col = position
    if not (0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS):
        raise ValueError(f"Position out of board bounds: {position}")


def create_empty_board() -> Board:
    """def: Tạo một bàn cờ Tướng rỗng.

    Role in System: Cung cấp ma trận nền cho các hàm khởi tạo bàn cờ và
    các trạng thái kiểm thử tùy chỉnh.
    Input/Output: Input là `None`. Output là một `Board` gồm 10 hàng, 9 cột
    và mọi ô được khởi tạo bằng `None`.
    """
    return [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]


def create_initial_board() -> Board:
    """def: Tạo bàn cờ khai cuộc chuẩn từ danh sách vị trí định nghĩa sẵn.

    Role in System: Cung cấp trạng thái mặc định khi bắt đầu một ván mới.
    Input/Output: Input là `None`. Output là một `Board` đã được đặt quân
    theo bố cục khai cuộc chuẩn của Cờ Tướng.
    """
    board = create_empty_board()
    for side, kind, row, col in INITIAL_PLACEMENTS:
        board[row][col] = Piece(side=side, kind=kind)
    return board


def create_board_from_placements(placements: list[Placement] | tuple[Placement, ...]) -> Board:
    """def: Tạo bàn cờ từ một danh sách vị trí quân cờ được chỉ định rõ.

    Role in System: Hỗ trợ dựng trạng thái có kiểm soát cho kiểm thử, gỡ lỗi
    và thử nghiệm tìm kiếm ngoài trạng thái khai cuộc chuẩn.
    Input/Output: Input là `placements`, một dãy tuple
    `(side, kind, row, col)`. Output là một `Board` đã được đặt quân.
    """
    board = create_empty_board()
    for side, kind, row, col in placements:
        _validate_position((row, col))
        board[row][col] = Piece(side=side, kind=kind)
    return board


@dataclass(slots=True)
class GameState:
    """def: Lưu trữ toàn bộ trạng thái có thể thay đổi của một thế cờ.

    Role in System: Đóng vai trò mô hình trung tâm được chia sẻ giữa engine
    luật, AI tìm kiếm, kiểm thử và giao diện người dùng.
    Input/Output: Lưu `board`, `side_to_move`, vị trí hai tướng và
    `move_history`. Đối tượng sẽ bị thay đổi bởi các hàm áp dụng nước đi.
    """
    board: Board
    side_to_move: Side = Side.RED
    red_general_position: Position = (9, 4)
    black_general_position: Position = (0, 4)
    move_history: list[MoveRecord] = field(default_factory=list)

    @classmethod
    def initial(cls) -> "GameState":
        """def: Tạo trạng thái mới ở vị trí khai cuộc chuẩn.

        Role in System: Là điểm vào mặc định để bắt đầu một ván cờ thông thường.
        Input/Output: Input là `None`. Output là một `GameState` được khởi
        tạo với bàn cờ mặc định và bên đỏ đi trước.
        """
        return cls(board=create_initial_board())

    @classmethod
    def from_placements(
        cls,
        placements: list[Placement] | tuple[Placement, ...],
        side_to_move: Side = Side.RED,
    ) -> "GameState":
        """def: Tạo một trạng thái tùy chỉnh từ bố cục bàn cờ chỉ định sẵn.

        Role in System: Cho phép dựng các thế cờ trọng tâm để kiểm tra luật,
        gỡ lỗi và kiểm thử cho heuristic search.
        Input/Output: Input là `placements` và tùy chọn `side_to_move`.
        Output là một `GameState` có lưu đúng vị trí hai tướng.
        """
        board = create_board_from_placements(placements)
        red_general = None
        black_general = None

        for side, kind, row, col in placements:
            if kind is not PieceKind.GENERAL:
                continue
            if side is Side.RED:
                red_general = (row, col)
            else:
                black_general = (row, col)

        if red_general is None or black_general is None:
            raise ValueError("Both generals must be present when creating a custom game state")

        return cls(
            board=board,
            side_to_move=side_to_move,
            red_general_position=red_general,
            black_general_position=black_general,
        )

    def clone(self) -> "GameState":
        """def: Tạo một bản sao tách biệt của trạng thái hiện tại.

        Role in System: Cung cấp một ảnh chụp an toàn khi nơi gọi cần một
        trạng thái khác có thể thay đổi độc lập.
        Input/Output: Input là `self`. Output là một `GameState` mới với dữ
        liệu bàn cờ, lượt đi và lịch sử nước đi đã được sao chép.
        """
        return GameState(
            board=deepcopy(self.board),
            side_to_move=self.side_to_move,
            red_general_position=self.red_general_position,
            black_general_position=self.black_general_position,
            move_history=list(self.move_history),
        )

    def piece_at(self, position: Position) -> Piece | None:
        """def: Trả về quân cờ đang nằm tại một tọa độ trên bàn cờ.

        Role in System: Là hàm đọc dữ liệu trung tâm được dùng trong sinh
        nước đi, kiểm tra hợp lệ, cập nhật trạng thái và đánh giá bàn cờ.
        Input/Output: Input là `position` dưới dạng `(row, col)`. Output là
        `Piece` tại ô đó hoặc `None` nếu ô đang trống.
        """
        _validate_position(position)
        row, col = position
        return self.board[row][col]

    def build_move(self, start: Position, end: Position, note: str = "") -> Move:
        """def: Kiểm tra và tạo một nước đi cho bên đang tới lượt.

        Role in System: Chuẩn hóa bước tạo nước đi trước khi nước đó được
        đối chiếu với danh sách hợp lệ hoặc áp dụng lên bàn cờ.
        Input/Output: Input là `start`, `end` và `note` tùy chọn. Output là
        một đối tượng `Move` nếu ô bắt đầu chứa quân của bên đang đi.
        """
        _validate_position(start)
        _validate_position(end)

        piece = self.piece_at(start)
        if piece is None:
            raise ValueError(f"No piece at starting square: {start}")
        if piece.side is not self.side_to_move:
            raise ValueError(
                f"Piece at {start} belongs to {piece.side.value}, not {self.side_to_move.value}"
            )
        return Move(start=start, end=end, note=note)

    def make_move(self, move: Move) -> None:
        """def: Áp dụng một nước đi lên trạng thái bàn cờ hiện tại.

        Role in System: Thực hiện chuyển trạng thái phục vụ gameplay, lọc
        nước đi hợp lệ và mở rộng cây tìm kiếm heuristic.
        Input/Output: Input là `move` dưới dạng `Move` đã được kiểm tra.
        Output là `None`; hàm sẽ thay đổi bàn cờ, vị trí tướng, bên đi và
        thêm một `MoveRecord` vào lịch sử.
        """
        moved_piece = self.piece_at(move.start)
        if moved_piece is None:
            raise ValueError(f"No piece available to move from {move.start}")
        if moved_piece.side is not self.side_to_move:
            raise ValueError("Cannot move a piece that does not belong to the active side")

        captured_piece = self.piece_at(move.end)
        if captured_piece is not None and captured_piece.side is moved_piece.side:
            raise ValueError("Cannot capture a piece from the same side")

        record = MoveRecord(
            move=move,
            moved_piece=moved_piece,
            captured_piece=captured_piece,
            previous_side_to_move=self.side_to_move,
            previous_red_general=self.red_general_position,
            previous_black_general=self.black_general_position,
        )

        start_row, start_col = move.start
        end_row, end_col = move.end
        self.board[start_row][start_col] = None
        self.board[end_row][end_col] = moved_piece

        if moved_piece.kind is PieceKind.GENERAL:
            if moved_piece.side is Side.RED:
                self.red_general_position = move.end
            else:
                self.black_general_position = move.end

        self.side_to_move = self.side_to_move.opponent()
        self.move_history.append(record)

    def undo_move(self) -> Move | None:
        """def: Hoàn tác nước đi vừa được thực hiện gần nhất.

        Role in System: Cho phép quay lui khi lọc nước đi hợp lệ và khi AI
        tìm kiếm mà không cần dựng lại toàn bộ bàn cờ từ đầu.
        Input/Output: Input là `self`. Output là `Move` vừa được hoàn tác,
        hoặc `None` nếu ngăn xếp lịch sử đang rỗng.
        """
        if not self.move_history:
            return None

        record = self.move_history.pop()
        start_row, start_col = record.move.start
        end_row, end_col = record.move.end

        self.board[start_row][start_col] = record.moved_piece
        self.board[end_row][end_col] = record.captured_piece
        self.side_to_move = record.previous_side_to_move
        self.red_general_position = record.previous_red_general
        self.black_general_position = record.previous_black_general
        return record.move

    def iter_pieces(self, side: Side | None = None):
        """def: Duyệt qua toàn bộ quân cờ, có thể lọc theo từng bên.

        Role in System: Hỗ trợ engine luật, đánh giá, thống kê và kiểm thử
        bằng một cơ chế duyệt nhất quán trên ma trận bàn cờ.
        Input/Output: Input là `side` tùy chọn. Output là iterator của các
        tuple `(row, col, piece)`.
        """
        for row_index, row in enumerate(self.board):
            for col_index, piece in enumerate(row):
                if piece is None:
                    continue
                if side is not None and piece.side is not side:
                    continue
                yield row_index, col_index, piece

    def count_pieces(self, side: Side | None = None) -> int:
        """def: Đếm số quân cờ hiện có trên bàn.

        Role in System: Cung cấp thông tin tổng hợp nhanh cho phần tóm tắt,
        chẩn đoán và kiểm tra tính hợp lý của trạng thái.
        Input/Output: Input là `side` tùy chọn. Output là một số nguyên đếm.
        """
        return sum(1 for _ in self.iter_pieces(side))

    def render_ascii(self) -> str:
        """def: Biểu diễn bàn cờ hiện tại dưới dạng văn bản nhiều dòng.

        Role in System: Cung cấp cách hiển thị nhẹ để gỡ lỗi, in ra console
        và dùng trong các bài test hồi quy.
        Input/Output: Input là `self`. Output là chuỗi `str` nhiều dòng mô
        tả trạng thái bàn cờ.
        """
        lines = []
        for row in self.board:
            lines.append(" ".join(piece.short_code() if piece else "__" for piece in row))
        return "\n".join(lines)
