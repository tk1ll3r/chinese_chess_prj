import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chinese_chess_ai.engine.moves import Move
from chinese_chess_ai.engine.state import GameState
from chinese_chess_ai.network.protocol import (
    decode_message,
    deserialize_state,
    encode_message,
    move_from_payload,
    move_to_payload,
    serialize_state,
)
from chinese_chess_ai.network.discovery import (
    RoomAnnouncement,
    RoomDiscoveryError,
    select_room_candidate,
)
from chinese_chess_ai.network.room_code import generate_room_code, normalize_room_code


class NetworkingSerializationTests(unittest.TestCase):
    def test_move_round_trip(self) -> None:
        move = Move(start=(6, 0), end=(5, 0))

        restored = move_from_payload(move_to_payload(move))

        self.assertEqual(restored, move)

    def test_state_round_trip_preserves_board_and_turn(self) -> None:
        state = GameState.initial()
        state.make_move(Move(start=(6, 0), end=(5, 0)))

        payload = serialize_state(
            state,
            move_history=["1. red: (6,0) -> (5,0)"],
            captured_by_red=["BP"],
            captured_by_black=[],
            status="Board synchronized",
        )
        restored = deserialize_state(payload)

        self.assertEqual(restored.state.render_ascii(), state.render_ascii())
        self.assertEqual(restored.state.side_to_move, state.side_to_move)
        self.assertEqual(restored.state.red_general_position, state.red_general_position)
        self.assertEqual(restored.move_history, ("1. red: (6,0) -> (5,0)",))
        self.assertEqual(restored.captured_by_red, ("BP",))
        self.assertEqual(restored.status, "Board synchronized")

    def test_message_round_trip(self) -> None:
        raw = encode_message("error", {"message": "bad move"})

        decoded = decode_message(raw)

        self.assertEqual(decoded["type"], "error")
        self.assertEqual(decoded["payload"]["message"], "bad move")

    def test_generated_room_code_has_expected_shape(self) -> None:
        room_code = generate_room_code()

        self.assertEqual(len(room_code), 6)
        self.assertEqual(room_code, room_code.upper())

    def test_normalize_room_code_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            normalize_room_code("not-a-valid-room-code")

    def test_select_room_candidate_returns_matching_room(self) -> None:
        announcement = RoomAnnouncement(
            room_code="XQ7K2P",
            game_name="ChineseChess",
            tcp_port=5000,
            room_id="room-1",
            host_name="host-a",
            source_ip="192.168.1.10",
            observed_at=10.0,
        )

        selected = select_room_candidate("XQ7K2P", [announcement], now=12.0)

        self.assertEqual(selected.source_ip, "192.168.1.10")
        self.assertEqual(selected.tcp_port, 5000)

    def test_select_room_candidate_rejects_collisions(self) -> None:
        announcements = [
            RoomAnnouncement(
                room_code="XQ7K2P",
                game_name="ChineseChess",
                tcp_port=5000,
                room_id="room-1",
                host_name="host-a",
                source_ip="192.168.1.10",
                observed_at=10.0,
            ),
            RoomAnnouncement(
                room_code="XQ7K2P",
                game_name="ChineseChess",
                tcp_port=5001,
                room_id="room-2",
                host_name="host-b",
                source_ip="192.168.1.11",
                observed_at=10.5,
            ),
        ]

        with self.assertRaises(RoomDiscoveryError):
            select_room_candidate("XQ7K2P", announcements, now=12.0)


if __name__ == "__main__":
    unittest.main()
