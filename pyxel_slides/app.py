"""Pyxel application: window, input, slide navigation, typewriter effect."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pyxel

from .assets.fonts import FontSet, ensure_fonts
from .ir import Slide
from .parser import parse_markdown
from .renderer import BUILTIN_GLYPH_H, BUILTIN_GLYPH_W, SlideRenderer
from .theme import GAMEBOY, Theme

# Characters revealed per frame for the typewriter effect.
_REVEAL_SPEED = 4


class SlidesApp:
    """Pyxel-based slide presenter.

    Default resolution is 384x216 (16:9). Pass ``--resolution WxH`` on the CLI
    or a larger ``width``/``height`` here for bigger windows (Pyxel 2.x supports
    up to at least 800px on the long axis).
    """

    def __init__(
        self,
        markdown_path: Path,
        theme: Theme = GAMEBOY,
        width: int = 384,
        height: int = 216,
        fps: int = 30,
        title: str = "pyxel-slides",
        pyxres_path: Optional[Path] = None,
        download_fonts: bool = True,
    ) -> None:
        self.markdown_path = Path(markdown_path)
        self.theme = theme
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.pyxres_path = pyxres_path
        self.download_fonts = download_fonts

        self.slides: List[Slide] = []
        self.index: int = 0
        self._mtime: float = 0.0
        self._reveal_chars: int = -1  # -1 = show all (typewriter disabled until first load)

    # --- lifecycle -------------------------------------------------------- #

    def run(self) -> None:
        self._load_markdown()

        # Attempt to download Spleen BDFs before starting Pyxel (network I/O
        # must happen before pyxel.init on some platforms).
        if self.download_fonts:
            ensure_fonts(quiet=False)

        pyxel.init(self.width, self.height, title=self.title, fps=self.fps)
        self._apply_palette()

        if self.pyxres_path and self.pyxres_path.exists():
            try:
                pyxel.load(str(self.pyxres_path))
            except Exception as exc:  # noqa: BLE001
                print(f"[pyxel-slides] Failed to load pyxres '{self.pyxres_path}': {exc}")

        # Load BDF fonts now that pyxel.init() has been called.
        fonts = FontSet.from_cache()
        self.renderer = SlideRenderer(
            self.theme, self.width, self.height, fonts,
            base_dir=self.markdown_path.parent,
        )

        # Start typewriter from slide 0.
        self._reveal_chars = 0

        pyxel.run(self.update, self.draw)

    # --- input ------------------------------------------------------------ #

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            return

        # --- Typewriter advance ---
        if self._reveal_chars >= 0 and self.slides:
            target = self.slides[self.index].body_char_count()
            if self._reveal_chars < target:
                self._reveal_chars = min(target, self._reveal_chars + _REVEAL_SPEED)

        # --- Navigation (Space / Right skip typewriter reveal first) ---
        advance_keys = (
            pyxel.btnp(pyxel.KEY_RIGHT)
            or pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_PAGEDOWN)
            or pyxel.btnp(pyxel.KEY_RETURN)
        )
        if advance_keys:
            if self.slides:
                target = self.slides[self.index].body_char_count()
                if self._reveal_chars >= 0 and self._reveal_chars < target:
                    # Skip reveal: show all text on this slide.
                    self._reveal_chars = target
                else:
                    self._goto(self.index + 1)

        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_PAGEUP) or pyxel.btnp(pyxel.KEY_BACKSPACE):
            self._goto(self.index - 1)
        elif pyxel.btnp(pyxel.KEY_HOME):
            self._goto(0)
        elif pyxel.btnp(pyxel.KEY_END):
            self._goto(len(self.slides) - 1)
        elif pyxel.btnp(pyxel.KEY_R):
            self._load_markdown()

    def draw(self) -> None:
        if not self.slides:
            pyxel.cls(self.theme.bg)
            pyxel.text(8, 8, "No slides found.", self.theme.fg)
            return

        slide = self.slides[self.index]
        self.renderer.draw(slide, reveal_budget=self._reveal_chars)
        self._draw_chrome()

    # --- helpers ---------------------------------------------------------- #

    def _goto(self, i: int) -> None:
        if not self.slides:
            return
        old = self.index
        self.index = max(0, min(len(self.slides) - 1, i))
        if self.index != old:
            self._reveal_chars = 0  # reset typewriter when changing slides

    def _load_markdown(self) -> None:
        text = self.markdown_path.read_text(encoding="utf-8")
        self.slides = parse_markdown(text)
        try:
            self._mtime = self.markdown_path.stat().st_mtime
        except OSError:
            self._mtime = 0.0
        if self.index >= len(self.slides):
            self.index = max(0, len(self.slides) - 1)
        self._reveal_chars = 0  # restart typewriter after reload
        print(f"[pyxel-slides] Loaded {len(self.slides)} slide(s) from {self.markdown_path}")

    def _apply_palette(self) -> None:
        for i, rgb in enumerate(self.theme.palette[:16]):
            pyxel.colors[i] = rgb

    def _draw_chrome(self) -> None:
        """Draw slide counter + progress bar using built-in font (always visible)."""
        label = f"{self.index + 1}/{len(self.slides)}"
        pyxel.text(
            self.width - len(label) * BUILTIN_GLYPH_W - 4,
            self.height - BUILTIN_GLYPH_H - 2,
            label,
            self.theme.accent,
        )
        if len(self.slides) > 1:
            bar_w = self.width - 8
            filled = int(bar_w * (self.index + 1) / len(self.slides))
            pyxel.rect(4, self.height - 2, bar_w, 1, self.theme.muted)
            pyxel.rect(4, self.height - 2, filled, 1, self.theme.accent)
