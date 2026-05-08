"""Pyxel application: window, input, slide navigation, typewriter effect.

Phase 6: clickable hyperlinks.
  - Mouse is enabled via pyxel.mouse(True).
  - Left-click on a rendered link opens it in the default browser.
  - Hovered link URL is shown in the bottom status bar.

Phase 8: hot-reload + theme CLI flag.
  - When hot_reload=True (default), the mtime of the .md file is checked
    once per second; on change the deck is re-parsed and re-rendered
    automatically without user interaction.

Phase 9: overview mode, presenter timer, export-to-PNG.
  - O key opens a slide-thumbnail grid; Escape or click to return / jump.
  - MM:SS presenter timer shown in the chrome; T resets it.
  - --export-dir PATH renders every slide to slide_NNN.png via Pillow.
"""

from __future__ import annotations

import time
import webbrowser
from pathlib import Path
from typing import Any, List, Optional

import pyxel

from .assets.fonts import FontSet, ensure_fonts
from .ir import Slide
from .parser import parse_markdown
from .renderer import BUILTIN_GLYPH_H, BUILTIN_GLYPH_W, SlideRenderer, _hit_test
from .theme import GAMEBOY, VSCODE_LIGHT, Theme

# Characters revealed per frame for the typewriter effect.
_REVEAL_SPEED = 4

# Overview grid layout constants.
_OV_COLS = 4
_OV_CARD_W = 88
_OV_CARD_H = 52
_OV_GAP = 4
_OV_MARGIN_X = 4
_OV_MARGIN_Y = 4
_OV_LABEL_H = 8  # pixels reserved for the overview header label


class SlidesApp:
    """Pyxel-based slide presenter.

    Default resolution is 384x216 (16:9). Pass ``--resolution WxH`` on the CLI
    or a larger ``width``/``height`` here for bigger windows (Pyxel 2.x supports
    up to at least 800px on the long axis).
    """

    def __init__(
        self,
        markdown_path: Path,
        theme: Theme = VSCODE_LIGHT,
        width: int = 384,
        height: int = 216,
        fps: int = 30,
        title: str = "pyxel-slides",
        pyxres_path: Optional[Path] = None,
        download_fonts: bool = True,
        hot_reload: bool = True,
        export_dir: Optional[Path] = None,
        typewriter: bool = False,
    ) -> None:
        self.markdown_path = Path(markdown_path).resolve()
        self.theme = theme
        self.width = width
        self.height = height
        self.fps = fps
        self.title = title
        self.pyxres_path = pyxres_path
        self.download_fonts = download_fonts
        self.hot_reload = hot_reload
        self.export_dir = Path(export_dir) if export_dir else None
        self.typewriter = typewriter

        self.slides: List[Slide] = []
        self.index: int = 0
        self._mtime: float = 0.0
        self._reveal_chars: int = -1  # -1 = show all (typewriter disabled until first load)
        # Step-by-step display state
        self._current_step: int = 1  # Current step for progressive display (1 = first step, 0 = show all)
        # Shimizukawa-style slide transition.
        self._old_img: Optional[Any] = None    # pyxel.Image snapshot of departing slide
        self._trans_rate: float = 0.0          # 1.0 → 0.0; zero = no transition active
        self._trans_direction: str = "right"   # "right"|"left"|"down"|"up"
        # Hot-reload: check mtime every _HOT_RELOAD_INTERVAL frames.
        self._hot_reload_counter: int = 0
        # Phase 9 state.
        self._overview: bool = False
        self._ov_scroll_row: int = 0
        self._timer_start: float = 0.0
        self._exporting: bool = False
        self._export_frame: int = 0

    # --- lifecycle -------------------------------------------------------- #

    def run(self) -> None:
        self._load_markdown()

        # Attempt to download Spleen BDFs before starting Pyxel (network I/O
        # must happen before pyxel.init on some platforms).
        if self.download_fonts:
            ensure_fonts(quiet=False)

        pyxel.init(self.width, self.height, title=self.title, fps=self.fps)
        pyxel.mouse(True)  # enable mouse for clickable links
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

        # Start typewriter from slide 0 (or show all immediately if disabled).
        self._reveal_chars = 0 if self.typewriter else -1

        # Phase 9: presenter timer starts now.
        self._timer_start = time.time()

        # Phase 9: export mode — render each slide to PNG then quit.
        if self.export_dir:
            self._exporting = True
            self._export_frame = 0
            self.export_dir.mkdir(parents=True, exist_ok=True)
            print(f"[pyxel-slides] Export mode → {self.export_dir}")

        pyxel.run(self.update, self.draw)

    # --- input ------------------------------------------------------------ #

    def update(self) -> None:
        # Q always quits.
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return

        # --- Export mode: just wait until all frames are saved, then quit ---
        if self._exporting:
            if self._export_frame >= len(self.slides):
                pyxel.quit()
            return

        # --- Slide transition in progress: count down and block input ---
        if self._trans_rate > 0:
            delta = 3.0 / self.fps
            self._trans_rate = max(0.0, self._trans_rate - delta)
            return

        # Escape: close overview if open, otherwise quit.
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            if self._overview:
                self._overview = False
            else:
                pyxel.quit()
            return

        # --- Overview mode input ---
        if self._overview:
            if pyxel.btnp(pyxel.KEY_UP):
                self._ov_scroll_row = max(0, self._ov_scroll_row - 1)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                max_row = max(0, (len(self.slides) - 1) // _OV_COLS)
                self._ov_scroll_row = min(max_row, self._ov_scroll_row + 1)
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                idx = self._overview_card_at(pyxel.mouse_x, pyxel.mouse_y)
                if idx >= 0:
                    self.index = idx   # direct jump — no transition
                    self._reveal_chars = 0 if self.typewriter else -1
                    self._overview = False
            return

        # O: open overview, auto-scroll to show the current slide's row.
        if pyxel.btnp(pyxel.KEY_O):
            self._ov_scroll_row = self.index // _OV_COLS
            self._overview = True
            return

        # T: reset presenter timer.
        if pyxel.btnp(pyxel.KEY_T):
            self._timer_start = time.time()

        # --- Typewriter advance (only when enabled) ---
        if self.typewriter and self._reveal_chars >= 0 and self.slides:
            target = self.slides[self.index].body_char_count()
            if self._reveal_chars < target:
                self._reveal_chars = min(target, self._reveal_chars + _REVEAL_SPEED)

        # --- Navigation (Space / Right skip typewriter reveal first, then advance steps/slide) ---
        advance_keys = (
            pyxel.btnp(pyxel.KEY_RIGHT)
            or pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_PAGEDOWN)
            or pyxel.btnp(pyxel.KEY_RETURN)
        )
        if advance_keys:
            if self.slides:
                current_slide = self.slides[self.index]
                max_step = max((getattr(b, 'step', 1) for b in current_slide.blocks), default=1)
                target = current_slide.body_char_count()
                if self.typewriter and self._reveal_chars >= 0 and self._reveal_chars < target:
                    # Skip typewriter reveal: show all text on this slide.
                    self._reveal_chars = target
                elif self._current_step < max_step:
                    # Reveal next step before advancing to next slide.
                    self._current_step += 1
                else:
                    self._goto(self.index + 1)

        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_PAGEUP) or pyxel.btnp(pyxel.KEY_BACKSPACE):
            if self.slides and self._current_step > 1:
                self._current_step -= 1
            else:
                self._goto(self.index - 1)
        elif pyxel.btnp(pyxel.KEY_HOME):
            self._goto(0)
        elif pyxel.btnp(pyxel.KEY_END):
            self._goto(len(self.slides) - 1)
        elif pyxel.btnp(pyxel.KEY_R):
            self._load_markdown()

        # --- Step-by-step navigation (Down arrow advances step, Up arrow goes back) ---
        if pyxel.btnp(pyxel.KEY_DOWN):
            if self.slides:
                current_slide = self.slides[self.index]
                # Find the maximum step number for this slide
                max_step = 1
                for block in current_slide.blocks:
                    block_step = getattr(block, 'step', 1)
                    max_step = max(max_step, block_step)
                # Advance step if possible
                if self._current_step < max_step:
                    self._current_step += 1
                else:
                    # If at max step, go to next slide
                    self._goto(self.index + 1)
        elif pyxel.btnp(pyxel.KEY_UP):
            if self.slides:
                if self._current_step > 1:
                    self._current_step -= 1
                else:
                    # If at step 1, go to previous slide
                    self._goto(self.index - 1)

        # --- Hot-reload: check mtime periodically ---
        if self.hot_reload:
            self._hot_reload_counter += 1
            if self._hot_reload_counter >= self.fps:  # once per second
                self._hot_reload_counter = 0
                self._check_hot_reload()

        # --- Mouse: open links on left click ---
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and hasattr(self, "renderer"):
            url = _hit_test(self.renderer.links, pyxel.mouse_x, pyxel.mouse_y)
            if url:
                webbrowser.open(url)

    def draw(self) -> None:
        # --- Export mode: render slide, save PNG, advance ---
        if self._exporting:
            if self._export_frame < len(self.slides):
                slide = self.slides[self._export_frame]
                self.renderer.draw(slide, reveal_budget=-1)
                self._try_save_frame()
                self._export_frame += 1
                if self._export_frame >= len(self.slides):
                    n = len(self.slides)
                    print(f"[pyxel-slides] Export complete: {n} slide(s) → {self.export_dir}")
            else:
                pyxel.cls(self.theme.bg)
            return

        if not self.slides:
            pyxel.cls(self.theme.bg)
            pyxel.text(8, 8, "No slides found.", self.theme.fg)
            return

        # --- Overview mode ---
        if self._overview:
            self._draw_overview()
            return

        slide = self.slides[self.index]
        slide.step = self._current_step  # Set current step before rendering
        self.renderer.draw(slide, reveal_budget=self._reveal_chars)

        # Shimizukawa-style transition overlay (drawn on top of the new slide).
        if self._trans_rate > 0 and self._old_img is not None:
            self._draw_trans_overlay()
            return  # suppress chrome during transition

        self._draw_chrome()

    # --- helpers ---------------------------------------------------------- #

    def _goto(self, i: int) -> None:
        if not self.slides:
            return
        new = max(0, min(len(self.slides) - 1, i))
        if new == self.index:
            return
        # Capture the current screen (previous frame's draw) as the departing slide.
        if self._old_img is None:
            self._old_img = pyxel.Image(self.width, self.height)
        self._old_img.blt(0, 0, pyxel.screen, 0, 0, self.width, self.height)
        # Choose direction based on navigation context.
        going_forward = new > self.index
        if going_forward:
            self._trans_direction = "right" if self.slides[new].is_section_title else "down"
        else:
            self._trans_direction = "left" if self.slides[self.index].is_section_title else "up"
        self.index = new
        self._reveal_chars = 0 if self.typewriter else -1
        self._current_step = 1  # Reset step when changing slides
        self._trans_rate = 1.0

    def _draw_trans_overlay(self) -> None:
        """Shimizukawa-style directional slide with dither cross-fade."""
        rate = self._trans_rate
        w, h = self.width, self.height
        d = self._trans_direction
        # Old slide slides away quadratically; new slide (already drawn) is underneath.
        if d == "right":    # old exits left
            ox, oy = -int(w * (1 - rate) ** 2), 0
        elif d == "left":   # old exits right
            ox, oy = +int(w * (1 - rate) ** 2), 0
        elif d == "down":   # old exits up
            ox, oy = 0, -int(h * (1 - rate) ** 2)
        else:               # "up": old exits down
            ox, oy = 0, +int(h * (1 - rate) ** 2)
        pyxel.dither(rate)
        pyxel.blt(ox, oy, self._old_img, 0, 0, w, h)
        pyxel.dither(1.0)

    def _load_markdown(self) -> None:
        text = self.markdown_path.read_text(encoding="utf-8")
        self.slides = parse_markdown(text)
        try:
            self._mtime = self.markdown_path.stat().st_mtime
        except OSError:
            self._mtime = 0.0
        if self.index >= len(self.slides):
            self.index = max(0, len(self.slides) - 1)
        self._reveal_chars = 0 if self.typewriter else -1  # restart typewriter after reload
        print(f"[pyxel-slides] Loaded {len(self.slides)} slide(s) from {self.markdown_path}")

    def _check_hot_reload(self) -> None:
        """Reload the deck if the source file has been modified on disk."""
        try:
            new_mtime = self.markdown_path.stat().st_mtime
        except OSError:
            return
        if new_mtime != self._mtime:
            print("[pyxel-slides] Source changed — hot-reloading…")
            self._load_markdown()

    def _apply_palette(self) -> None:
        for i, rgb in enumerate(self.theme.palette[:16]):
            pyxel.colors[i] = rgb

    def _draw_chrome(self) -> None:
        """Draw slide counter, progress bar, presenter timer, and hovered-link URL indicator."""
        # --- Presenter timer (bottom-left) ---
        elapsed = time.time() - self._timer_start
        timer_str = self._format_time(elapsed)
        pyxel.text(
            4,
            self.height - BUILTIN_GLYPH_H - 2,
            timer_str,
            self.theme.muted,
        )

        # --- Hovered link URL (bottom-left, one row above counter) ---
        if hasattr(self, "renderer") and self.renderer.links:
            url = _hit_test(self.renderer.links, pyxel.mouse_x, pyxel.mouse_y)
            if url:
                max_chars = (self.width - 8) // BUILTIN_GLYPH_W
                display = url if len(url) <= max_chars else url[:max_chars - 3] + "..."
                url_y = self.height - BUILTIN_GLYPH_H * 2 - 4
                pyxel.text(4, url_y, display, self.theme.eff_link)
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

    # --- Phase 9 helpers -------------------------------------------------- #

    @staticmethod
    def _format_time(elapsed: float) -> str:
        """Format *elapsed* seconds as ``MM:SS``."""
        total = max(0, int(elapsed))
        return f"{total // 60:02d}:{total % 60:02d}"

    def _overview_card_at(self, mx: int, my: int) -> int:
        """Return the slide index of the overview card under (mx, my), or -1.

        Accounts for the current scroll position (_ov_scroll_row) and the gap
        pixels between cards so that clicks on gaps return -1.
        """
        ov_top = _OV_MARGIN_Y + _OV_LABEL_H
        col = (mx - _OV_MARGIN_X) // (_OV_CARD_W + _OV_GAP)
        row_rel = (my - ov_top) // (_OV_CARD_H + _OV_GAP)
        if col < 0 or col >= _OV_COLS or row_rel < 0:
            return -1
        # Verify the click is inside the card body, not in the inter-card gap.
        card_x = _OV_MARGIN_X + col * (_OV_CARD_W + _OV_GAP)
        card_y = ov_top + row_rel * (_OV_CARD_H + _OV_GAP)
        if mx < card_x or mx >= card_x + _OV_CARD_W:
            return -1
        if my < card_y or my >= card_y + _OV_CARD_H:
            return -1
        idx = (row_rel + self._ov_scroll_row) * _OV_COLS + col
        if idx < 0 or idx >= len(self.slides):
            return -1
        return idx

    def _draw_overview(self) -> None:
        """Render the slide-thumbnail overview grid."""
        pyxel.cls(self.theme.eff_panel_bg)
        hint = "[O/Esc] close  [↑↓] scroll  click slide to jump"
        pyxel.text(_OV_MARGIN_X, _OV_MARGIN_Y, hint, self.theme.muted)

        ov_top = _OV_MARGIN_Y + _OV_LABEL_H
        first_idx = self._ov_scroll_row * _OV_COLS
        for slot, slide_idx in enumerate(range(first_idx, len(self.slides))):
            col = slot % _OV_COLS
            row = slot // _OV_COLS
            cx = _OV_MARGIN_X + col * (_OV_CARD_W + _OV_GAP)
            cy = ov_top + row * (_OV_CARD_H + _OV_GAP)
            if cy + _OV_CARD_H > self.height:
                break  # no more vertical space

            is_cur = slide_idx == self.index
            border_col = self.theme.accent if is_cur else self.theme.muted
            pyxel.rect(cx, cy, _OV_CARD_W, _OV_CARD_H, self.theme.bg)
            pyxel.rectb(cx, cy, _OV_CARD_W, _OV_CARD_H, border_col)

            num_col = self.theme.accent if is_cur else self.theme.muted
            pyxel.text(cx + 2, cy + 2, str(slide_idx + 1), num_col)

            title = self.slides[slide_idx].title
            if title:
                max_chars = (_OV_CARD_W - 4) // BUILTIN_GLYPH_W
                display = title if len(title) <= max_chars else title[:max_chars - 1] + "~"
                pyxel.text(cx + 2, cy + BUILTIN_GLYPH_H + 4, display, self.theme.fg)

    def _try_save_frame(self) -> None:
        """Save the current Pyxel screen as a PNG for the export sequence.

        Reads palette-indexed pixel data via ``pyxel.screen.pget()``, converts
        to RGB using the active theme palette, then writes a PNG with Pillow.
        Silently skips (with a warning) when Pillow is not installed.
        """
        if not self.export_dir:
            return
        from .dither import pillow_available
        if not pillow_available():
            print("[pyxel-slides] Pillow not available — cannot export PNGs.")
            return
        from PIL import Image as PilImage
        out = self.export_dir / f"slide_{self._export_frame:03d}.png"
        try:
            pal = self.theme.palette_as_rgb
            w, h = self.width, self.height
            pixels = [
                pal[pyxel.screen.pget(x, y)]
                for y in range(h)
                for x in range(w)
            ]
            img = PilImage.new("RGB", (w, h))
            img.putdata(pixels)
            img.save(str(out))
            print(f"[pyxel-slides] Exported {out}")
        except Exception as exc:  # noqa: BLE001
            print(f"[pyxel-slides] Failed to export {out}: {exc}")
