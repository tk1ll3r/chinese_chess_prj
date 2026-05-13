from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

try:
    from PIL import Image, ImageOps, ImageTk
except Exception:  # pragma: no cover - Pillow is optional at runtime.
    Image = None
    ImageOps = None
    ImageTk = None


FIRST_IMAGE_NAME = "first.jpg"
BACKGROUND_IMAGE_NAME = "background.jpg"
ONSITE_BACKGROUND_IMAGE_NAME = "background_onsite.jpg"


def assets_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parents[2] / "assets"


def background_image_path(image_name: str = BACKGROUND_IMAGE_NAME) -> Path:
    return assets_dir() / image_name


def background_asset_ready(image_name: str = BACKGROUND_IMAGE_NAME) -> bool:
    return background_image_path(image_name).exists()


def create_cover_photo(image_name: str, size: tuple[int, int]) -> tk.PhotoImage | None:
    if Image is None or ImageOps is None or ImageTk is None:
        return None
    path = background_image_path(image_name)
    if not path.exists():
        return None
    width, height = size
    try:
        source = Image.open(path).convert("RGB")
        fitted = ImageOps.fit(
            source,
            (max(1, width), max(1, height)),
            method=Image.Resampling.LANCZOS,
        )
        return ImageTk.PhotoImage(fitted)
    except Exception:
        return None


class BackgroundImage:
    def __init__(
        self,
        parent: tk.Misc,
        fallback: str = "#1f1f1f",
        image_name: str = BACKGROUND_IMAGE_NAME,
    ) -> None:
        self.parent = parent
        self.fallback = fallback
        self.image_name = image_name
        self.label = tk.Label(parent, bd=0, highlightthickness=0, bg=fallback)
        self.label.place(x=0, y=0, relwidth=1, relheight=1)
        self.label.lower()
        self._source = self._load_source()
        self._photo: tk.PhotoImage | None = None
        self._last_size: tuple[int, int] = (0, 0)
        self.parent.bind("<Configure>", self._on_configure, add="+")
        self.parent.after_idle(self.refresh)

    def _load_source(self):
        if Image is None:
            return None
        path = background_image_path(self.image_name)
        if not path.exists():
            return None
        try:
            return Image.open(path).convert("RGB")
        except Exception:
            return None

    def _on_configure(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is self.parent:
            self.refresh()

    def refresh(self) -> None:
        width = max(1, self.parent.winfo_width())
        height = max(1, self.parent.winfo_height())
        size = (width, height)
        if size == self._last_size:
            return
        self._last_size = size

        if self._source is None or ImageOps is None or ImageTk is None:
            self.label.configure(image="", bg=self.fallback)
            return

        fitted = ImageOps.fit(self._source, size, method=Image.Resampling.LANCZOS)
        self._photo = ImageTk.PhotoImage(fitted)
        self.label.configure(image=self._photo)
        self.label.lower()


def install_background(
    parent: tk.Misc,
    fallback: str = "#1f1f1f",
    image_name: str = BACKGROUND_IMAGE_NAME,
) -> BackgroundImage:
    try:
        parent.configure(bg=fallback)
    except Exception:
        pass
    return BackgroundImage(parent, fallback=fallback, image_name=image_name)
