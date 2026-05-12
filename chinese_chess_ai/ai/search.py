from __future__ import annotations

import random
from dataclasses import dataclass
from math import inf
from typing import Literal

from ..engine.constants import MATERIAL_VALUES
from ..engine.moves import Move
from ..engine.rules import generate_legal_moves, is_in_check
from ..engine.state import GameState
from ..engine.types import Position
from .evaluate import evaluate_position

MATE_SCORE = 1_000_000
QUIESCENCE_MAX_DEPTH = 4
NOISE_SCALE = 0.001
StateKey = tuple[object, tuple[tuple[object | None, ...], ...]]


@dataclass(slots=True)
class SearchConfig:
    """def: Lưu các tham số cấu hình có thể thay đổi của thuật toán tìm kiếm.

    Role in System: Cho phép nơi gọi điều khiển độ sâu tìm kiếm và việc bật
    tắt cắt tỉa mà không cần sửa mã cài đặt thuật toán.
    Input/Output: Lưu các giá trị cấu hình `depth` và `use_alpha_beta`.
    """
    depth: int = 2
    use_alpha_beta: bool = True
    use_quiescence: bool = True
    use_iterative_deepening: bool = False


@dataclass(slots=True)
class TranspositionEntry:
    depth: int
    score: float
    flag: Literal["exact", "lower", "upper"]
    best_move: Move | None = None


# Killer moves: store moves that caused beta cutoffs
killer_moves: dict[int, list[Move]] = {}


def choose_move(state: GameState, config: SearchConfig | None = None) -> Move | None:
    """def: Chọn nước đi hợp lệ tốt nhất cho trạng thái hiện tại.

    Role in System: Là điểm vào chính của AI, kết nối phần sinh nước đi,
    đánh giá heuristic và tìm kiếm trên cây trạng thái.
    Input/Output: Input là `state` và `config` tùy chọn. Output là `Move`
    được chọn cho `state.side_to_move`, hoặc `None` nếu không có nước đi hợp lệ.
    """
    search_config = config or SearchConfig()
    legal_moves = generate_legal_moves(state)
    if not legal_moves:
        return None

    # Clear killer moves for new search
    global killer_moves
    killer_moves = {}

    transposition_table: dict[StateKey, TranspositionEntry] = {}

    if search_config.use_iterative_deepening:
        # Iterative deepening: search depth 1, 2, 3, ... up to target depth
        best_move: Move | None = None
        for current_depth in range(1, search_config.depth + 1):
            best_move = _search_at_depth(
                state, current_depth, transposition_table, search_config
            )
        return best_move
    else:
        return _search_at_depth(
            state, search_config.depth, transposition_table, search_config
        )


def _search_at_depth(
    state: GameState,
    depth: int,
    transposition_table: dict[StateKey, TranspositionEntry],
    config: SearchConfig,
) -> Move | None:
    """Search at a specific depth."""
    depth = max(1, depth)
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

    for move in _ordered_moves(state, legal_moves, preferred_move, depth):
        state.make_move(move)
        try:
            score = -_negamax(
                state=state,
                depth=depth - 1,
                alpha=-beta,
                beta=-alpha,
                config=config,
                transposition_table=transposition_table,
                ply=1,
            )
        finally:
            state.undo_move()

        if score > best_score:
            best_score = score
            best_move = move
        if config.use_alpha_beta and score > alpha:
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
    config: SearchConfig,
    transposition_table: dict[StateKey, TranspositionEntry],
    ply: int,
) -> float:
    """def: Đánh giá một trạng thái bằng thuật toán negamax đệ quy.

    Role in System: Duyệt cây trò chơi, áp dụng cắt tỉa alpha-beta và tái
    sử dụng các trạng thái đã gặp thông qua bảng băm chuyển vị.
    Input/Output: Input gồm `state` hiện tại, các ngưỡng tìm kiếm, `depth`
    còn lại và bảng chuyển vị. Output là một điểm số kiểu `float`.
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
    if depth == 0:
        # Use quiescence search at leaf nodes
        if config.use_quiescence:
            return _quiescence_search(state, alpha, beta, 0, config, transposition_table)
        else:
            return _evaluate_leaf(state, legal_moves)

    if not legal_moves:
        return _evaluate_leaf(state, legal_moves)

    best_score = -inf
    best_move: Move | None = None
    for move in _ordered_moves(state, legal_moves, preferred_move, ply):
        state.make_move(move)
        try:
            score = -_negamax(
                state=state,
                depth=depth - 1,
                alpha=-beta,
                beta=-alpha,
                config=config,
                transposition_table=transposition_table,
                ply=ply + 1,
            )
        finally:
            state.undo_move()

        if score > best_score:
            best_score = score
            best_move = move
        if config.use_alpha_beta:
            if score > alpha:
                alpha = score
            if alpha >= beta:
                # Store killer move
                if move.end not in [m.end for m in killer_moves.get(ply, [])]:
                    if ply not in killer_moves:
                        killer_moves[ply] = []
                    killer_moves[ply].insert(0, move)
                    if len(killer_moves[ply]) > 2:
                        killer_moves[ply] = killer_moves[ply][:2]
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


def _quiescence_search(
    state: GameState,
    alpha: float,
    beta: float,
    depth: int,
    config: SearchConfig,
    transposition_table: dict[StateKey, TranspositionEntry],
) -> float:
    """Quiescence search: extend search for tactical positions (captures, checks)."""
    if depth >= QUIESCENCE_MAX_DEPTH:
        return float(evaluate_position(state))

    # Stand pat: can we already beat beta without searching?
    stand_pat = float(evaluate_position(state))
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Only search captures and checks
    legal_moves = generate_legal_moves(state)
    tactical_moves = [
        move for move in legal_moves
        if state.piece_at(move.end) is not None  # Capture
        or _is_check_move(state, move)  # Check
    ]

    if not tactical_moves:
        return stand_pat

    for move in _ordered_moves(state, tactical_moves, None, 0):
        state.make_move(move)
        try:
            score = -_quiescence_search(
                state, -beta, -alpha, depth + 1, config, transposition_table
            )
        finally:
            state.undo_move()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def _is_check_move(state: GameState, move: Move) -> bool:
    """Check if a move gives check to opponent."""
    state.make_move(move)
    in_check = is_in_check(state, state.side_to_move)
    state.undo_move()
    return in_check


def _evaluate_leaf(state: GameState, legal_moves: list[Move]) -> float:
    """def: Chấm điểm một nút kết thúc hoặc nút đã chạm giới hạn độ sâu.

    Role in System: Chuyển trạng thái ở biên cây tìm kiếm thành giá trị số
    để truyền ngược lên các mức phía trên.
    Input/Output: Input là `state` và danh sách `legal_moves` đã tính sẵn.
    Output là điểm `float` hoặc mức phạt thua chiếu bí.
    """
    if not legal_moves:
        return -MATE_SCORE
    return float(evaluate_position(state)) + random.random() * NOISE_SCALE


def _ordered_moves(
    state: GameState,
    legal_moves: list[Move],
    preferred_move: Move | None = None,
    ply: int = 0,
) -> list[Move]:
    """def: Sắp xếp nước đi hợp lệ để tăng hiệu quả tìm kiếm.

    Role in System: Đưa các nước bắt quân triển vọng và nước tốt nhất đã
    được lưu trong cache lên trước để cắt tỉa hiệu quả hơn.
    Input/Output: Input là `state`, `legal_moves` và `preferred_move` tùy
    chọn. Output là danh sách `Move` đã được sắp xếp.
    """
    def move_sort_key(move: Move) -> tuple[int, int, int, int, Position, Position]:
        # 1. Preferred move from transposition table (highest priority)
        preferred_bonus = 1 if preferred_move is not None and move == preferred_move else 0

        # 2. Killer moves (non-capture moves that caused beta cutoff)
        killer_bonus = 0
        if ply in killer_moves:
            for i, killer in enumerate(killer_moves[ply]):
                if move == killer:
                    killer_bonus = 2 - i
                    break

        # 3. Captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
        captured_piece = state.piece_at(move.end)
        capture_value = 0 if captured_piece is None else MATERIAL_VALUES[captured_piece.kind]

        # 4. Attacker value (prefer lower value attackers for captures)
        moved_piece = state.piece_at(move.start)
        attacker_value = 0 if moved_piece is None else MATERIAL_VALUES[moved_piece.kind]

        return (
            -preferred_bonus,
            -killer_bonus,
            -capture_value,
            attacker_value,
            move.start,
            move.end,
        )

    return sorted(legal_moves, key=move_sort_key)


def _state_key(state: GameState) -> StateKey:
    """def: Chuyển trạng thái hiện tại thành khóa cho bảng chuyển vị.

    Role in System: Cho phép nhận diện và tái sử dụng các trạng thái lặp lại
    trong quá trình heuristic search.
    Input/Output: Input là `state`. Output là một `StateKey` có thể băm,
    gồm bên sắp đi và nội dung bàn cờ.
    """
    board_key = tuple(tuple(row) for row in state.board)
    return (state.side_to_move, board_key)
