import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chinese_chess_ai.audio.sound_manager import SoundManager


class _LiveThread:
    def is_alive(self) -> bool:
        return True


class AudioTests(unittest.TestCase):
    def test_music_playlist_prefers_numbered_tracks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            music_dir = root / "music"
            music_dir.mkdir()
            (music_dir / "old.mp3").touch()
            (music_dir / "2.mp3").touch()
            (music_dir / "1.mp3").touch()

            manager = SoundManager(enabled=False)
            manager._assets_dir = lambda subdir: root / subdir

            self.assertEqual(
                [path.name for path in manager._music_file_paths()],
                ["1.mp3", "2.mp3"],
            )

    def test_playlist_running_checks_same_playlist(self) -> None:
        manager = SoundManager(enabled=False)
        playlist = [Path("assets/music/1.mp3"), Path("assets/music/2.mp3")]
        manager._playlist = list(playlist)
        manager._playlist_thread = _LiveThread()
        manager._playlist_stop.clear()
        manager._music_playing = True

        self.assertTrue(manager._playlist_is_running(playlist))
        self.assertFalse(manager._playlist_is_running(list(reversed(playlist))))


if __name__ == "__main__":
    unittest.main()
