from __future__ import annotations

from ..engine.constants import MATERIAL_VALUES
from ..engine.rules import generate_legal_moves
from ..engine.state import GameState
from ..engine.types import PieceKind, Side
from .piece_square_tables import get_piece_square_value

SOLDIER_CROSSED_RIVER_BONUS = 3


def material_score(state: GameState, perspective: Side) -> int:
    """def: Chấm điểm một thế cờ chỉ dựa trên tương quan quân lực.

    Role in System: Cung cấp heuristic cơ sở để so sánh các trạng thái ở
    giai đoạn đầu của AI search.
    Input/Output: Input là `state` và `perspective`. Output là số nguyên,
    trong đó giá trị dương có lợi cho `perspective`.
    """
    score = 0
    for _row, _col, piece in state.iter_pieces():
        value = MATERIAL_VALUES[piece.kind]
        if piece.side is perspective:
            score += value
        else:
            score -= value
    return score


def positional_score(state: GameState, perspective: Side) -> float:
    """def: Cộng thêm điểm thưởng vị trí vào hàm đánh giá.

    Role in System: Mở rộng cách chấm điểm quân lực thuần túy bằng piece-square tables
    và các yếu tố vị trí khác.
    Input/Output: Input là `state` và `perspective`. Output là số thực
    biểu diễn phần điều chỉnh điểm theo vị trí cho bên đó.
    """
    score = 0.0
    for row, col, piece in state.iter_pieces():
        # Piece-square table value
        pst_value = get_piece_square_value(piece.kind, row, col, piece.side)

        # Additional soldier bonus for crossing river
        bonus = 0.0
        if piece.kind is PieceKind.SOLDIER:
            if piece.side is Side.RED and row <= 4:
                bonus = SOLDIER_CROSSED_RIVER_BONUS + (4 - row)
            elif piece.side is Side.BLACK and row >= 5:
                bonus = SOLDIER_CROSSED_RIVER_BONUS + (row - 5)

        total_value = pst_value + bonus
        if piece.side is perspective:
            score += total_value
        else:
            score -= total_value
    return score


def mobility_score(state: GameState, perspective: Side) -> float:
    """Evaluate piece mobility (number of legal moves)."""
    score = 0.0

    # Count legal moves for current side
    current_moves = len(generate_legal_moves(state))

    # Simulate opponent's mobility
    state.side_to_move = state.side_to_move.opponent()
    opponent_moves = len(generate_legal_moves(state))
    state.side_to_move = state.side_to_move.opponent()  # Restore

    if state.side_to_move == perspective:
        score = (current_moves - opponent_moves) * 0.1
    else:
        score = (opponent_moves - current_moves) * 0.1

    return score


def king_safety_score(state: GameState, perspective: Side) -> float:
    """Evaluate king safety based on defenders."""
    score = 0.0

    # Check if king has advisors and elephants nearby
    red_gen_row, red_gen_col = state.red_general_position
    black_gen_row, black_gen_col = state.black_general_position

    def count_defenders(gen_row: int, gen_col: int, side: Side) -> int:
        defenders = 0
        # Check for advisors in palace
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            r, c = gen_row + dr, gen_col + dc
            if 0 <= r < 10 and 0 <= c < 9:
                piece = state.board[r][c]
                if piece and piece.side == side and piece.kind == PieceKind.ADVISOR:
                    defenders += 1
        # Check for elephants
        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            r, c = gen_row + dr, gen_col + dc
            if 0 <= r < 10 and 0 <= c < 9:
                piece = state.board[r][c]
                if piece and piece.side == side and piece.kind == PieceKind.ELEPHANT:
                    defenders += 1
        return defenders

    red_defenders = count_defenders(red_gen_row, red_gen_col, Side.RED)
    black_defenders = count_defenders(black_gen_row, black_gen_col, Side.BLACK)

    if perspective == Side.RED:
        score = (red_defenders - black_defenders) * 2.0
    else:
        score = (black_defenders - red_defenders) * 2.0

    return score


def evaluate_position(state: GameState, perspective: Side | None = None) -> float:
    """def: Tính điểm heuristic tổng hợp cho một trạng thái bàn cờ.

    Role in System: Cung cấp hàm đánh giá tĩnh chính được dùng ở các lá của
    cây tìm kiếm và khi so sánh nhanh các nước đi ứng viên.
    Input/Output: Input là `state` và `perspective` tùy chọn. Output là số thực
    biểu diễn điểm đánh giá cho bên được chọn.
    """
    side = perspective or state.side_to_move

    # Combine all evaluation components
    material = material_score(state, side)
    positional = positional_score(state, side)
    mobility = mobility_score(state, side)
    king_safety = king_safety_score(state, side)

    return material + positional + mobility + king_safety

