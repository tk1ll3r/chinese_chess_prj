from __future__ import annotations

import random

ROOM_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
ROOM_CODE_LENGTH = 6


def normalize_room_code(room_code: str) -> str:
    compact = "".join(character for character in room_code.upper() if character.isalnum())
    if len(compact) != ROOM_CODE_LENGTH:
        raise ValueError(f"Room code must be {ROOM_CODE_LENGTH} characters long.")
    if any(character not in ROOM_CODE_ALPHABET for character in compact):
        raise ValueError("Room code contains unsupported characters.")
    return compact


def generate_room_code(rng: random.Random | None = None) -> str:
    generator = rng or random.SystemRandom()
    return "".join(generator.choice(ROOM_CODE_ALPHABET) for _ in range(ROOM_CODE_LENGTH))
