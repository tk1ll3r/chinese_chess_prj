from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Literal

from ..engine.constants import MATERIAL_VALUES
from ..engine.moves import Move
from ..engine.rules import generate_legal_moves
from ..engine.state import GameState
from ..engine.types import Position
from .evaluate import evaluate_position

MATE_SCORE = 1_000_000
StateKey = tuple[object, tuple[tuple[object | None, ...], ...]]


@dataclass(slots=True)
class SearchConfig:
    """def: Lưu các tham số cấu hình có thể thay đổi của thuật toán tìm kiếm.

    Role in System: Cho phép nơi gọi điều khiển độ sâu tìm kiếm và việc bật
    tắt cắt tỉa mà không cần sửa mã cài đặt thuật toán.
    Input/Output: Lưu các giá trị cấu hình `depth` và `use_alpha_beta`.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    depth: int = 2
    use_alpha_beta: bool = True


@dataclass(slots=True)
class TranspositionEntry:
    depth: int
    score: float
    flag: Literal["exact", "lower", "upper"]
    best_move: Move | None = None


def choose_move(state: GameState, config: SearchConfig | None = None) -> Move | None:
    """def: Chọn nước đi hợp lệ tốt nhất cho trạng thái hiện tại.

    Role in System: Là điểm vào chính của AI, kết nối phần sinh nước đi,
    đánh giá heuristic và tìm kiếm trên cây trạng thái.
    Input/Output: Input là `state` và `config` tùy chọn. Output là `Move`
    được chọn cho `state.side_to_move`, hoặc `None` nếu không có nước đi hợp lệ.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    search_config = config or SearchConfig()
    depth = max(1, search_config.depth)
    transposition_table: dict[StateKey, TranspositionEntry] = {}
    legal_moves = generate_legal_moves(state)
    if not legal_moves:
        return None

    alpha = -inf
    beta = inf
    best_score = -inf
    best_move: Move | None = None
    state_key = _state_key(state)
    tt_entry = transposition_table.get(state_key)
    preferred_move = tt_entry.best_move if tt_entry is not None else None

    for move in _ordered_moves(state, legal_moves, preferred_move):
        state.make_move(move)
        try:
            score = -_negamax(
                state=state,
                depth=depth - 1,
                alpha=-beta,
                beta=-alpha,
                use_alpha_beta=search_config.use_alpha_beta,
                transposition_table=transposition_table,
            )
        finally:
            state.undo_move()

        if score > best_score:
            best_score = score
            best_move = move
        if search_config.use_alpha_beta and score > alpha:
            alpha = score

    transposition_table[state_key] = TranspositionEntry(
        depth=depth,
        score=best_score,
        flag="exact",
        best_move=best_move,
    )
    return best_move


def _negamax(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    use_alpha_beta: bool,
    transposition_table: dict[StateKey, TranspositionEntry],
) -> float:
    """def: Đánh giá một trạng thái bằng thuật toán negamax đệ quy.

    Role in System: Duyệt cây trò chơi, áp dụng cắt tỉa alpha-beta và tái
    sử dụng các trạng thái đã gặp thông qua bảng băm chuyển vị.
    Input/Output: Input gồm `state` hiện tại, các ngưỡng tìm kiếm, `depth`
    còn lại và bảng chuyển vị. Output là một điểm số kiểu `float`.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    alpha_original = alpha
    beta_original = beta
    state_key = _state_key(state)
    tt_entry = transposition_table.get(state_key)
    preferred_move: Move | None = None
    if tt_entry is not None and tt_entry.depth >= depth:
        preferred_move = tt_entry.best_move
        if tt_entry.flag == "exact":
            return tt_entry.score
        if tt_entry.flag == "lower":
            alpha = max(alpha, tt_entry.score)
        else:
            beta = min(beta, tt_entry.score)
        if alpha >= beta:
            return tt_entry.score
    elif tt_entry is not None:
        preferred_move = tt_entry.best_move

    legal_moves = generate_legal_moves(state)
    if depth == 0 or not legal_moves:
        return _evaluate_leaf(state, legal_moves)

    best_score = -inf
    best_move: Move | None = None
    for move in _ordered_moves(state, legal_moves, preferred_move):
        state.make_move(move)
        try:
            score = -_negamax(
                state=state,
                depth=depth - 1,
                alpha=-beta,
                beta=-alpha,
                use_alpha_beta=use_alpha_beta,
                transposition_table=transposition_table,
            )
        finally:
            state.undo_move()

        if score > best_score:
            best_score = score
            best_move = move
        if use_alpha_beta:
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break

    flag: Literal["exact", "lower", "upper"] = "exact"
    if best_score <= alpha_original:
        flag = "upper"
    elif best_score >= beta_original:
        flag = "lower"
    transposition_table[state_key] = TranspositionEntry(
        depth=depth,
        score=best_score,
        flag=flag,
        best_move=best_move,
    )
    return best_score


def _evaluate_leaf(state: GameState, legal_moves: list[Move]) -> float:
    """def: Chấm điểm một nút kết thúc hoặc nút đã chạm giới hạn độ sâu.

    Role in System: Chuyển trạng thái ở biên cây tìm kiếm thành giá trị số
    để truyền ngược lên các mức phía trên.
    Input/Output: Input là `state` và danh sách `legal_moves` đã tính sẵn.
    Output là điểm `float` hoặc mức phạt thua chiếu bí.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    if not legal_moves:
        return -MATE_SCORE
    return float(evaluate_position(state))


def _ordered_moves(
    state: GameState,
    legal_moves: list[Move],
    preferred_move: Move | None = None,
) -> list[Move]:
    """def: Sắp xếp nước đi hợp lệ để tăng hiệu quả tìm kiếm.

    Role in System: Đưa các nước bắt quân triển vọng và nước tốt nhất đã
    được lưu trong cache lên trước để cắt tỉa hiệu quả hơn.
    Input/Output: Input là `state`, `legal_moves` và `preferred_move` tùy
    chọn. Output là danh sách `Move` đã được sắp xếp.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    def move_sort_key(move: Move) -> tuple[int, int, Position, Position]:
        preferred_bonus = 1 if preferred_move is not None and move == preferred_move else 0
        captured_piece = state.piece_at(move.end)
        capture_value = 0 if captured_piece is None else MATERIAL_VALUES[captured_piece.kind]
        moved_piece = state.piece_at(move.start)
        attacker_value = 0 if moved_piece is None else MATERIAL_VALUES[moved_piece.kind]
        return (-preferred_bonus, -capture_value, attacker_value, move.start, move.end)

    return sorted(legal_moves, key=move_sort_key)


def _state_key(state: GameState) -> StateKey:
    """def: Chuyển trạng thái hiện tại thành khóa cho bảng chuyển vị.

    Role in System: Cho phép nhận diện và tái sử dụng các trạng thái lặp lại
    trong quá trình heuristic search.
    Input/Output: Input là `state`. Output là một `StateKey` có thể băm,
    gồm bên sắp đi và nội dung bàn cờ.
    Author: 25521829 - Nguyen Van Thuong
    Date: 2026-04-29
    Ver: 0.2
    """
    board_key = tuple(tuple(row) for row in state.board)
    return (state.side_to_move, board_key)
