from __future__ import annotations

import tkinter as tk
from tkinter import font, ttk


def configure_fonts(root: tk.Tk) -> None:
    """Use a UI font family that renders Vietnamese accents consistently."""
    available = set(font.families(root))
    preferred = ("Segoe UI", "Arial", "DejaVu Sans", "Noto Sans", "Liberation Sans")
    family = next((name for name in preferred if name in available), "TkDefaultFont")

    for font_name, size, weight in (
        ("TkDefaultFont", 10, "normal"),
        ("TkTextFont", 10, "normal"),
        ("TkMenuFont", 10, "normal"),
        ("TkHeadingFont", 10, "bold"),
        ("TkCaptionFont", 10, "normal"),
    ):
        try:
            default_font = font.nametofont(font_name)
            default_font.configure(family=family, size=size, weight=weight)
        except tk.TclError:
            continue

    style = ttk.Style(root)
    style.configure(".", font=(family, 10))
    style.configure("Title.TLabel", font=(family, 18, "bold"))
    style.configure("Subtitle.TLabel", font=(family, 16, "bold"))
    style.configure("Heading.TLabel", font=(family, 10, "bold"))
