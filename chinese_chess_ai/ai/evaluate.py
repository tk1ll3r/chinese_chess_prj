from __future__ import annotations

from ..engine.constants import MATERIAL_VALUES
from ..engine.state import GameState
from ..engine.types import PieceKind, Side

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


def positional_score(state: GameState, perspective: Side) -> int:
    """def: Cộng thêm điểm thưởng vị trí đơn giản vào hàm đánh giá.

    Role in System: Mở rộng cách chấm điểm quân lực thuần túy bằng một mức
    nhận biết vị trí nhẹ, đặc biệt cho quân tốt sau khi qua sông.
    Input/Output: Input là `state` và `perspective`. Output là số nguyên
    biểu diễn phần điều chỉnh điểm theo vị trí cho bên đó.
    """
    score = 0
    for row, _col, piece in state.iter_pieces():
        bonus = 0
        if piece.kind is PieceKind.SOLDIER:
            if piece.side is Side.RED and row <= 4:
                bonus = SOLDIER_CROSSED_RIVER_BONUS + (4 - row)
            elif piece.side is Side.BLACK and row >= 5:
                bonus = SOLDIER_CROSSED_RIVER_BONUS + (row - 5)

        if piece.side is perspective:
            score += bonus
        else:
            score -= bonus
    return score


def evaluate_position(state: GameState, perspective: Side | None = None) -> int:
    """def: Tính điểm heuristic tổng hợp cho một trạng thái bàn cờ.

    Role in System: Cung cấp hàm đánh giá tĩnh chính được dùng ở các lá của
    cây tìm kiếm và khi so sánh nhanh các nước đi ứng viên.
    Input/Output: Input là `state` và `perspective` tùy chọn. Output là số
    nguyên biểu diễn điểm đánh giá cho bên được chọn.
    """
    side = perspective or state.side_to_move
    return material_score(state, side) + positional_score(state, side)
