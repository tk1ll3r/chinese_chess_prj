from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Literal

SoundType = Literal["move", "capture", "check", "checkmate", "select", "illegal", "button"]


class SoundManager:
    """Manages game sound effects and background music."""

    def __init__(self, assets_dir: str | Path | None = None, enabled: bool = True):
        self.enabled = enabled
        self.volume = 0.7
        self._pygame_available = False
        self._sounds: dict[SoundType, object] = {}
        self._music_enabled = True
        self._music_playing = False
        self._current_music: str | None = None

        if assets_dir is None:
            if getattr(sys, "frozen", False):
                assets_dir = Path(sys._MEIPASS) / "assets" / "sounds"
            else:
                assets_dir = Path(__file__).parent.parent.parent / "assets" / "sounds"
        self.assets_dir = Path(assets_dir)

        if self.enabled:
            self._init_pygame()

    def _init_pygame(self) -> None:
        try:
            import pygame
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._pygame_available = True
        except (ImportError, Exception):
            self._pygame_available = False

    def _load_sound(self, sound_type: SoundType) -> object | None:
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
        if not self.enabled or not self._pygame_available:
            return

        sound = self._load_sound(sound_type)
        if sound is not None:
            try:
                sound.play()
            except Exception:
                pass

    def play_move(self) -> None:
        self.play("move")

    def play_capture(self) -> None:
        self.play("capture")

    def play_check(self) -> None:
        self.play("check")

    def play_checkmate(self) -> None:
        self.play("checkmate")

    def play_select(self) -> None:
        self.play("select")

    def play_illegal(self) -> None:
        self.play("illegal")

    def play_button(self) -> None:
        self.play("button")

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            if sound is not None:
                try:
                    sound.set_volume(self.volume)
                except Exception:
                    pass
        if self._pygame_available:
            try:
                import pygame
                pygame.mixer.music.set_volume(self.volume)
            except Exception:
                pass

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled and not self._pygame_available:
            self._init_pygame()
        if not enabled:
            self.stop_music()

    def music_dir(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / "assets" / "music"
        return Path(__file__).parent.parent.parent / "assets" / "music"

    def play_music(self, file_name: str = "", loop: int = -1) -> None:
        if not self._pygame_available or not self._music_enabled:
            return
        try:
            import pygame
            music_path = self.music_dir() / file_name if file_name else None
            if music_path is not None and not music_path.exists():
                return
            if self._music_playing:
                pygame.mixer.music.stop()
                self._music_playing = False
            if music_path is not None:
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loop)
                self._music_playing = True
                self._current_music = file_name
        except Exception:
            pass

    def play_music_list(self, file_names: list[str], loop: int = -1) -> None:
        if not self._pygame_available or not self._music_enabled or not file_names:
            return
        self.play_music(file_names[0], loop)

    def stop_music(self) -> None:
        if not self._pygame_available:
            return
        try:
            import pygame
            if self._music_playing:
                pygame.mixer.music.stop()
                self._music_playing = False
                self._current_music = None
        except Exception:
            pass

    def set_music_enabled(self, enabled: bool) -> None:
        self._music_enabled = enabled
        if not enabled:
            self.stop_music()

    def is_music_playing(self) -> bool:
        return self._music_playing

    def music_file_paths(self) -> list[Path]:
        music_dir = self.music_dir()
        if not music_dir.exists():
            return []
        return sorted(
            p for p in music_dir.iterdir()
            if p.suffix.lower() in {".mp3", ".wav", ".ogg", ".flac"}
        )
