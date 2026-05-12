from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

SoundType = Literal["move", "capture", "check", "checkmate", "select", "illegal", "button"]


class SoundManager:
    """Manages game sound effects with graceful fallback if pygame unavailable."""

    def __init__(self, assets_dir: str | Path | None = None, enabled: bool = True):
        self.enabled = enabled
        self.volume = 0.7
        self._pygame_available = False
        self._sounds: dict[SoundType, object] = {}

        if assets_dir is None:
            if getattr(sys, "frozen", False):
                assets_dir = Path(sys._MEIPASS) / "assets" / "sounds"
            else:
                assets_dir = Path(__file__).parent.parent.parent / "assets" / "sounds"
        self.assets_dir = Path(assets_dir)

        if self.enabled:
            self._init_pygame()

    def _init_pygame(self) -> None:
        """Initialize pygame mixer if available."""
        try:
            import pygame
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._pygame_available = True
        except (ImportError, Exception):
            self._pygame_available = False

    def _load_sound(self, sound_type: SoundType) -> object | None:
        """Lazy load sound file."""
        if not self._pygame_available or not self.enabled:
            return None

        if sound_type in self._sounds:
            return self._sounds[sound_type]

        sound_path = self.assets_dir / f"{sound_type}.wav"
        if not sound_path.exists():
            return None

        try:
            import pygame
            sound = pygame.mixer.Sound(str(sound_path))
            sound.set_volume(self.volume)
            self._sounds[sound_type] = sound
            return sound
        except Exception:
            return None

    def play(self, sound_type: SoundType) -> None:
        """Play a sound effect."""
        if not self.enabled or not self._pygame_available:
            return

        sound = self._load_sound(sound_type)
        if sound is not None:
            try:
                sound.play()
            except Exception:
                pass

    def play_move(self) -> None:
        """Play move sound."""
        self.play("move")

    def play_capture(self) -> None:
        """Play capture sound."""
        self.play("capture")

    def play_check(self) -> None:
        """Play check sound."""
        self.play("check")

    def play_checkmate(self) -> None:
        """Play checkmate sound."""
        self.play("checkmate")

    def play_select(self) -> None:
        """Play select sound."""
        self.play("select")

    def play_illegal(self) -> None:
        """Play illegal move sound."""
        self.play("illegal")

    def play_button(self) -> None:
        """Play button click sound."""
        self.play("button")

    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            if sound is not None:
                try:
                    sound.set_volume(self.volume)
                except Exception:
                    pass

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable sound."""
        self.enabled = enabled
        if enabled and not self._pygame_available:
            self._init_pygame()
