from __future__ import annotations

import sys
import threading
from pathlib import Path
from typing import Literal

SoundType = Literal["move", "capture", "check", "checkmate", "select", "illegal", "button"]
SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac"}
BACKGROUND_MUSIC_FILES = ("1.mp3", "2.mp3")
MUSIC_VOLUME_SCALE = 0.6


class SoundManager:
    """Manages game sound effects via pygame.mixer with winsound fallback on Windows."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.volume = 0.5
        self._pygame_available = False
        self._winsound_available = False
        self._sounds: dict[SoundType, object] = {}
        self._music_enabled = True
        self._music_playing = False
        self._playlist: list[Path] = []
        self._playlist_thread: threading.Thread | None = None
        self._playlist_stop = threading.Event()

        if sys.platform == "win32":
            try:
                import winsound
                self._winsound_available = True
            except Exception:
                pass

        if self.enabled:
            self._init_pygame()

    def _assets_dir(self, subdir: str) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / "assets" / subdir
        return Path(__file__).parent.parent.parent / "assets" / subdir

    def _init_pygame(self) -> None:
        try:
            import pygame
            for freq, chan, buf in [(44100, 2, 1024), (22050, 1, 512)]:
                try:
                    pygame.mixer.init(frequency=freq, size=-16, channels=chan, buffer=buf)
                    self._pygame_available = True
                    return
                except Exception:
                    continue
        except ImportError:
            pass

    # --- Sound effects ---

    def _play_winsound(self, sound_type: SoundType) -> bool:
        if not self._winsound_available:
            return False
        sounds_dir = self._assets_dir("sounds")
        for ext in SUPPORTED_EXTENSIONS:
            path = sounds_dir / f"{sound_type}{ext}"
            if path.exists():
                break
        else:
            return False
        try:
            import winsound
            flags = winsound.SND_ASYNC | winsound.SND_NODEFAULT
            winsound.PlaySound(str(path), flags)
            return True
        except Exception:
            return False

    def _load_sound(self, sound_type: SoundType) -> object | None:
        if not self._pygame_available or not self.enabled:
            return None
        if sound_type in self._sounds:
            return self._sounds[sound_type]

        sounds_dir = self._assets_dir("sounds")
        for ext in SUPPORTED_EXTENSIONS:
            path = sounds_dir / f"{sound_type}{ext}"
            if path.exists():
                break
        else:
            return None

        try:
            import pygame
            snd = pygame.mixer.Sound(str(path))
            snd.set_volume(self.volume)
            self._sounds[sound_type] = snd
            return snd
        except Exception:
            return None

    def play(self, sound_type: SoundType) -> None:
        if not self.enabled:
            return

        if self._pygame_available:
            snd = self._load_sound(sound_type)
            if snd is not None:
                try:
                    snd.play()
                    return
                except Exception:
                    pass

        self._play_winsound(sound_type)

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
        for snd in self._sounds.values():
            if snd is not None:
                try:
                    snd.set_volume(self.volume)
                except Exception:
                    pass
        if self._pygame_available:
            try:
                import pygame
                pygame.mixer.music.set_volume(self.volume * MUSIC_VOLUME_SCALE)
            except Exception:
                pass

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled and not self._pygame_available:
            self._init_pygame()

    # --- Background music (pygame only) ---

    def start_playlist(self) -> None:
        if not self._pygame_available or not self._music_enabled:
            return
        playlist = self._music_file_paths()
        if not playlist:
            return
        if self._playlist_is_running(playlist):
            return
        self._stop_playlist_thread()
        self._playlist = playlist
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
        except Exception:
            pass

    def set_music_enabled(self, enabled: bool) -> None:
        self._music_enabled = enabled
        if not enabled:
            self.stop_music()
        elif enabled and self._pygame_available:
            self.start_playlist()

    def close(self) -> None:
        self.stop_music()

    def _stop_playlist_thread(self) -> None:
        self._music_playing = False
        self._playlist_stop.set()
        if self._playlist_thread is not None:
            self._playlist_thread.join(timeout=1)
            self._playlist_thread = None

    def _music_file_paths(self) -> list[Path]:
        music_dir = self._assets_dir("music")
        if not music_dir.exists():
            return []
        preferred = [
            music_dir / file_name
            for file_name in BACKGROUND_MUSIC_FILES
            if (music_dir / file_name).exists()
        ]
        if preferred:
            return preferred
        return sorted(
            p for p in music_dir.iterdir()
            if p.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _playlist_is_running(self, playlist: list[Path]) -> bool:
        return (
            self._music_playing
            and self._playlist_thread is not None
            and self._playlist_thread.is_alive()
            and not self._playlist_stop.is_set()
            and self._playlist == playlist
        )

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
                    pygame.mixer.music.set_volume(self.volume * MUSIC_VOLUME_SCALE)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        if self._playlist_stop.wait(0.5):
                            return
                except Exception:
                    continue

    # --- Diagnostic ---

    def diagnostic(self) -> dict:
        """Return audio status info for debugging."""
        return {
            "enabled": self.enabled,
            "volume": self.volume,
            "pygame_available": self._pygame_available,
            "winsound_available": self._winsound_available,
            "music_enabled": self._music_enabled,
            "music_playing": self._music_playing,
            "sounds_loaded": list(self._sounds.keys()),
            "music_dir_exists": self._assets_dir("music").exists(),
            "music_files": [p.name for p in self._music_file_paths()],
            "sounds_dir_exists": self._assets_dir("sounds").exists(),
            "sound_files": [p.name for p in self._assets_dir("sounds").iterdir()] if self._assets_dir("sounds").exists() else [],
        }
