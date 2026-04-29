from __future__ import annotations

from .constants import BOARD_COLS, BOARD_ROWS, PALACE_COLUMNS, PALACE_ROWS
from .moves import Move
from .state import GameState
from .types import Piece, PieceKind, Position, Side


def inside_board(position: Position) -> bool:
    """def: Kiểm tra một tọa độ có nằm trong bàn cờ Tướng hay không.

    Role in System: Là điều kiện biên cơ sở được dùng xuyên suốt trong sinh
    nước đi và kiểm tra tấn công.
    Input/Output: Input là `position` dưới dạng `(row, col)`. Output là
    `True` nếu tọa độ thuộc bàn cờ 10x9, ngược lại là `False`.
    """
    row, col = position
    return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS


def inside_palace(side: Side, position: Position) -> bool:
    """def: Kiểm tra một tọa độ có nằm trong cung của một bên hay không.

    Role in System: Áp đặt luật di chuyển trong cung cho quân tướng và sĩ.
    Input/Output: Input là `side` và `position`. Output là `True` nếu ô đó
    thuộc phạm vi cung của bên tương ứng, ngược lại là `False`.
    """
    row, col = position
    return row in PALACE_ROWS[side] and col in PALACE_COLUMNS


def iter_side_positions(state: GameState, side: Side):
    for row, col, _piece in state.iter_pieces(side):
        yield row, col


def _river_crossed(side: Side, row: int) -> bool:
    return row <= 4 if side is Side.RED else row >= 5


def _friendly_piece_at(state: GameState, side: Side, position: Position) -> bool:
    piece = state.piece_at(position)
    return piece is not None and piece.side is side


def _append_step_move(
    state: GameState,
    side: Side,
    start: Position,
    end: Position,
    moves: list[Move],
    note: str,
) -> None:
    if not inside_board(end):
        return
    if _friendly_piece_at(state, side, end):
        return
    moves.append(Move(start=start, end=end, note=note))


def _generate_general_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        end = (row + delta_row, col + delta_col)
        if inside_palace(piece.side, end):
            _append_step_move(state, piece.side, start, end, moves, "general")
    return moves


def _generate_advisor_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    for delta_row, delta_col in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        end = (row + delta_row, col + delta_col)
        if inside_palace(piece.side, end):
            _append_step_move(state, piece.side, start, end, moves, "advisor")
    return moves


def _generate_elephant_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    for delta_row, delta_col in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
        end = (row + delta_row, col + delta_col)
        if not inside_board(end):
            continue
        end_row, _end_col = end
        if piece.side is Side.RED and end_row < 5:
            continue
        if piece.side is Side.BLACK and end_row > 4:
            continue
        eye = (row + delta_row // 2, col + delta_col // 2)
        if state.piece_at(eye) is not None:
            continue
        _append_step_move(state, piece.side, start, end, moves, "elephant")
    return moves


def _generate_horse_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    candidates = (
        ((-2, -1), (-1, 0)),
        ((-2, 1), (-1, 0)),
        ((2, -1), (1, 0)),
        ((2, 1), (1, 0)),
        ((-1, -2), (0, -1)),
        ((1, -2), (0, -1)),
        ((-1, 2), (0, 1)),
        ((1, 2), (0, 1)),
    )
    for (delta_row, delta_col), (leg_row, leg_col) in candidates:
        leg = (row + leg_row, col + leg_col)
        end = (row + delta_row, col + delta_col)
        if not inside_board(end):
            continue
        if state.piece_at(leg) is not None:
            continue
        _append_step_move(state, piece.side, start, end, moves, "horse")
    return moves


def _generate_chariot_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        current_row = row + delta_row
        current_col = col + delta_col
        while inside_board((current_row, current_col)):
            end = (current_row, current_col)
            occupant = state.piece_at(end)
            if occupant is None:
                moves.append(Move(start=start, end=end, note="chariot"))
            else:
                if occupant.side is not piece.side:
                    moves.append(Move(start=start, end=end, note="chariot"))
                break
            current_row += delta_row
            current_col += delta_col
    return moves


def _generate_cannon_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        current_row = row + delta_row
        current_col = col + delta_col
        screen_found = False
        while inside_board((current_row, current_col)):
            end = (current_row, current_col)
            occupant = state.piece_at(end)
            if not screen_found:
                if occupant is None:
                    moves.append(Move(start=start, end=end, note="cannon"))
                else:
                    screen_found = True
            else:
                if occupant is not None:
                    if occupant.side is not piece.side:
                        moves.append(Move(start=start, end=end, note="cannon"))
                    break
            current_row += delta_row
            current_col += delta_col
    return moves


def _generate_soldier_moves(state: GameState, start: Position, piece: Piece) -> list[Move]:
    row, col = start
    moves: list[Move] = []
    forward = -1 if piece.side is Side.RED else 1
    _append_step_move(state, piece.side, start, (row + forward, col), moves, "soldier")

    if _river_crossed(piece.side, row):
        _append_step_move(state, piece.side, start, (row, col - 1), moves, "soldier")
        _append_step_move(state, piece.side, start, (row, col + 1), moves, "soldier")

    return moves


_MOVE_GENERATORS = {
    PieceKind.GENERAL: _generate_general_moves,
    PieceKind.ADVISOR: _generate_advisor_moves,
    PieceKind.ELEPHANT: _generate_elephant_moves,
    PieceKind.HORSE: _generate_horse_moves,
    PieceKind.CHARIOT: _generate_chariot_moves,
    PieceKind.CANNON: _generate_cannon_moves,
    PieceKind.SOLDIER: _generate_soldier_moves,
}


def generate_pseudo_legal_moves_for_side(state: GameState, side: Side) -> list[Move]:
    """def: Sinh toàn bộ nước đi theo luật quân cờ cho một bên trước khi kiểm tra an toàn tướng.

    Role in System: Tạo ra tập nước đi ở lớp đầu tiên, sau đó sẽ được lọc
    tiếp thành các nước đi hợp lệ hoàn toàn.
    Input/Output: Input là `state` và `side`. Output là danh sách `Move`
    chỉ thỏa luật di chuyển của quân cờ.
    """
    moves: list[Move] = []
    for row, col, piece in state.iter_pieces(side):
        generator = _MOVE_GENERATORS[piece.kind]
        moves.extend(generator(state, (row, col), piece))
    return moves


def generals_face_each_other(state: GameState) -> bool:
    """def: Kiểm tra trạng thái hai tướng đối mặt trực tiếp.

    Role in System: Ngăn các trạng thái phạm luật khi hai tướng cùng cột và
    không có quân cản ở giữa.
    Input/Output: Input là `state`. Output là `True` nếu khoảng giữa hai
    tướng trên cùng cột không có quân nào chắn.
    """
    red_row, red_col = state.red_general_position
    black_row, black_col = state.black_general_position
    if red_col != black_col:
        return False

    start_row = min(red_row, black_row) + 1
    end_row = max(red_row, black_row)
    for row in range(start_row, end_row):
        if state.piece_at((row, red_col)) is not None:
            return False
    return True


def _piece_matches(
    state: GameState,
    position: Position,
    side: Side,
    kind: PieceKind,
) -> bool:
    if not inside_board(position):
        return False
    piece = state.board[position[0]][position[1]]
    return piece is not None and piece.side is side and piece.kind is kind


def _sliding_attack_reaches(
    state: GameState,
    target: Position,
    deltas: tuple[tuple[int, int], ...],
    attacker_side: Side,
    allowed_kinds: tuple[PieceKind, ...],
) -> bool:
    target_row, target_col = target
    for delta_row, delta_col in deltas:
        row = target_row + delta_row
        col = target_col + delta_col
        while inside_board((row, col)):
            piece = state.board[row][col]
            if piece is None:
                row += delta_row
                col += delta_col
                continue
            return piece.side is attacker_side and piece.kind in allowed_kinds
    return False


def _cannon_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        row = target_row + delta_row
        col = target_col + delta_col
        screen_found = False
        while inside_board((row, col)):
            piece = state.board[row][col]
            if piece is None:
                row += delta_row
                col += delta_col
                continue
            if not screen_found:
                screen_found = True
            else:
                return piece.side is attacker_side and piece.kind is PieceKind.CANNON
            row += delta_row
            col += delta_col
    return False


def _horse_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    candidates = (
        ((-2, -1), (-1, 0)),
        ((-2, 1), (-1, 0)),
        ((2, -1), (1, 0)),
        ((2, 1), (1, 0)),
        ((-1, -2), (0, -1)),
        ((1, -2), (0, -1)),
        ((-1, 2), (0, 1)),
        ((1, 2), (0, 1)),
    )
    for (delta_row, delta_col), (leg_row, leg_col) in candidates:
        attacker_position = (target_row - delta_row, target_col - delta_col)
        leg_position = (attacker_position[0] + leg_row, attacker_position[1] + leg_col)
        if not inside_board(attacker_position) or not inside_board(leg_position):
            continue
        if state.board[leg_position[0]][leg_position[1]] is not None:
            continue
        if _piece_matches(state, attacker_position, attacker_side, PieceKind.HORSE):
            return True
    return False


def _advisor_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    for delta_row, delta_col in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        attacker_position = (target_row - delta_row, target_col - delta_col)
        if not inside_palace(attacker_side, attacker_position):
            continue
        if _piece_matches(state, attacker_position, attacker_side, PieceKind.ADVISOR):
            return True
    return False


def _elephant_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    for delta_row, delta_col in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
        attacker_position = (target_row - delta_row, target_col - delta_col)
        if not inside_board(attacker_position):
            continue
        attacker_row, _attacker_col = attacker_position
        if attacker_side is Side.RED and attacker_row < 5:
            continue
        if attacker_side is Side.BLACK and attacker_row > 4:
            continue
        eye = (attacker_position[0] + (delta_row // 2), attacker_position[1] + (delta_col // 2))
        if not inside_board(eye) or state.board[eye[0]][eye[1]] is not None:
            continue
        if _piece_matches(state, attacker_position, attacker_side, PieceKind.ELEPHANT):
            return True
    return False


def _soldier_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    if attacker_side is Side.RED:
        forward_source = (target_row + 1, target_col)
        if _piece_matches(state, forward_source, attacker_side, PieceKind.SOLDIER):
            return True
        for side_source in ((target_row, target_col - 1), (target_row, target_col + 1)):
            if not inside_board(side_source) or side_source[0] > 4:
                continue
            if _piece_matches(state, side_source, attacker_side, PieceKind.SOLDIER):
                return True
        return False

    forward_source = (target_row - 1, target_col)
    if _piece_matches(state, forward_source, attacker_side, PieceKind.SOLDIER):
        return True
    for side_source in ((target_row, target_col - 1), (target_row, target_col + 1)):
        if not inside_board(side_source) or side_source[0] < 5:
            continue
        if _piece_matches(state, side_source, attacker_side, PieceKind.SOLDIER):
            return True
    return False


def _general_attack_reaches(state: GameState, target: Position, attacker_side: Side) -> bool:
    target_row, target_col = target
    for delta_row, delta_col in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        attacker_position = (target_row - delta_row, target_col - delta_col)
        if not inside_palace(attacker_side, attacker_position):
            continue
        if _piece_matches(state, attacker_position, attacker_side, PieceKind.GENERAL):
            return True
    return False


def is_square_attacked(state: GameState, target: Position, attacker_side: Side) -> bool:
    """def: Xác định một ô đích có đang bị một bên tấn công hay không.

    Role in System: Là truy vấn chiến thuật lõi dùng cho kiểm tra chiếu
    tướng và lọc nước đi hợp lệ.
    Input/Output: Input là `state`, `target` và `attacker_side`. Output là
    `True` nếu có ít nhất một quân hoặc một hướng tấn công chạm tới ô đó.
    """
    if _general_attack_reaches(state, target, attacker_side):
        return True
    if _advisor_attack_reaches(state, target, attacker_side):
        return True
    if _elephant_attack_reaches(state, target, attacker_side):
        return True
    if _horse_attack_reaches(state, target, attacker_side):
        return True
    if _sliding_attack_reaches(
        state,
        target=target,
        deltas=((1, 0), (-1, 0), (0, 1), (0, -1)),
        attacker_side=attacker_side,
        allowed_kinds=(PieceKind.CHARIOT,),
    ):
        return True
    if _cannon_attack_reaches(state, target, attacker_side):
        return True
    return _soldier_attack_reaches(state, target, attacker_side)


def is_in_check(state: GameState, side: Side) -> bool:
    """def: Kiểm tra tướng của một bên có đang bị chiếu hay không.

    Role in System: Xác nhận tính hợp lệ của bàn cờ sau một nước đi và cung
    cấp tín hiệu nguy hiểm chiến thuật cho engine và giao diện.
    Input/Output: Input là `state` và `side`. Output là `True` nếu tướng
    của bên đó đang bị tấn công hoặc hai tướng đang đối mặt.
    """
    if generals_face_each_other(state):
        return True
    general_position = (
        state.red_general_position if side is Side.RED else state.black_general_position
    )
    return is_square_attacked(state, general_position, side.opponent())


def generate_pseudo_legal_moves(state: GameState) -> list[Move]:
    """def: Sinh các nước đi giả hợp lệ cho bên đang tới lượt.

    Role in System: Là hàm bao thuận tiện gắn quá trình sinh nước đi với
    lượt hiện tại được lưu trong `GameState`.
    Input/Output: Input là `state`. Output là danh sách `Move` giả hợp lệ
    dành cho `state.side_to_move`.
    """
    return generate_pseudo_legal_moves_for_side(state, state.side_to_move)


def generate_legal_moves(state: GameState) -> list[Move]:
    """def: Sinh danh sách nước đi hợp lệ hoàn toàn cho bên đang tới lượt.

    Role in System: Tạo ra danh sách nước đi chuẩn được dùng bởi CLI, GUI,
    test và AI search.
    Input/Output: Input là `state`. Output là danh sách `Move` còn hợp lệ
    sau khi đã lọc tự chiếu tướng và lỗi đối mặt tướng.
    """
    moving_side = state.side_to_move
    legal_moves: list[Move] = []
    for move in generate_pseudo_legal_moves(state):
        state.make_move(move)
        try:
            if not is_in_check(state, moving_side):
                legal_moves.append(move)
        finally:
            state.undo_move()
    return legal_moves
