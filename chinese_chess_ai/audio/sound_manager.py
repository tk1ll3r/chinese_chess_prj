from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Literal

SoundType = Literal["move", "capture", "check", "checkmate", "select", "illegal", "button"]

MUSIC_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}


class SoundManager:
    """Manages game sound effects and background music with playlist support."""

    def __init__(self, assets_dir: str | Path | None = None, enabled: bool = True):
        self.enabled = enabled
        self.volume = 0.7
        self._pygame_available = False
        self._sounds: dict[SoundType, object] = {}
        self._music_enabled = True
        self._music_playing = False
        self._current_music: str | None = None
        self._playlist: list[Path] = []
        self._playlist_thread: threading.Thread | None = None
        self._playlist_stop = threading.Event()

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

    def music_file_paths(self) -> list[Path]:
        music_dir = self.music_dir()
        if not music_dir.exists():
            return []
        return sorted(
            p for p in music_dir.iterdir()
            if p.suffix.lower() in MUSIC_EXTENSIONS
        )

    def start_playlist(self) -> None:
        """Start cycling through all music files in the assets/music directory."""
        if not self._pygame_available or not self._music_enabled:
            return
        self._playlist = self.music_file_paths()
        if not self._playlist:
            return
        self._stop_playlist_thread()
        self._music_playing = True
        self._playlist_stop.clear()
        self._playlist_thread = threading.Thread(
            target=self._playlist_worker, daemon=True
        )
        self._playlist_thread.start()

    def stop_music(self) -> None:
        self._stop_playlist_thread()
        if not self._pygame_available:
            return
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                self._music_playing = False
                self._current_music = None
        except Exception:
            pass

    def set_music_enabled(self, enabled: bool) -> None:
        self._music_enabled = enabled
        if not enabled:
            self.stop_music()
        elif enabled and self._pygame_available:
            self.start_playlist()

    def is_music_playing(self) -> bool:
        return self._music_playing

    def _stop_playlist_thread(self) -> None:
        self._music_playing = False
        self._playlist_stop.set()
        if self._playlist_thread is not None:
            self._playlist_thread.join(timeout=2)
            self._playlist_thread = None

    def _playlist_worker(self) -> None:
        import pygame
        while not self._playlist_stop.is_set():
            for music_path in self._playlist:
                if self._playlist_stop.is_set():
                    return
                try:
                    if not pygame.mixer.get_init():
                        return
                    pygame.mixer.music.load(str(music_path))
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play()
                    self._current_music = music_path.name
                    while pygame.mixer.music.get_busy():
                        if self._playlist_stop.wait(0.5):
                            return
                except Exception:
                    continue
