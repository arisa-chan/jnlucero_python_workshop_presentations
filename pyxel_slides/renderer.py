"""Slide renderer (Phase 3).

New in Phase 3:
  - Pygments syntax highlighting inside code panels.  Each token span is
    drawn with a role-mapped GameBoy palette colour (keywords/numbers →
    muted, strings/comments → accent, identifiers → bg).
  - Graceful fallback to plain text when Pygments is absent.

Phase 2 features retained:
  - FontSet: Spleen BDF fonts (body/heading_sm/heading_md/heading_lg/mono).
  - Styled TextRun rendering: bold, italic, inline-code pill, links.
  - Word-wrap respects inline run boundaries.
  - Typewriter reveal: `reveal_budget` (Paragraphs/ListBlocks only).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyxel

from .assets.fonts import FontSet
from .dither import dither_to_palette, fit_dimensions, pillow_available
from .highlight import role_to_color, tokenize_lines
from .ir import CodeBlock, Heading, ImageBlock, ListBlock, MathBlock, Paragraph, Slide, TextRun, plain
from .mathtext import matplotlib_available, render_math
from .theme import Theme


# --------------------------------------------------------------------------- #
# Built-in font constants (Pyxel 4x6 bitmap font)
# --------------------------------------------------------------------------- #

BUILTIN_GLYPH_W = 4
BUILTIN_GLYPH_H = 6

# Legacy aliases so any existing code that imported these still works.
GLYPH_W = BUILTIN_GLYPH_W
GLYPH_H = BUILTIN_GLYPH_H


# --------------------------------------------------------------------------- #
# Low-level helpers
# --------------------------------------------------------------------------- #

def _draw_text(x: int, y: int, s: str, col: int, font: Optional[Any] = None) -> None:
    """Draw text, using a custom pyxel.Font when provided."""
    if font is not None:
        pyxel.text(x, y, s, col, font)
    else:
        pyxel.text(x, y, s, col)


def _text_width(s: str, font: Optional[Any], glyph_w: int) -> int:
    """Pixel width of string s for the given font / fallback metrics."""
    if font is not None:
        return font.text_width(s)
    return len(s) * glyph_w


# --------------------------------------------------------------------------- #
# Styled-run word-wrap
# --------------------------------------------------------------------------- #

def _flatten(runs: List[TextRun]) -> List[Tuple[str, TextRun]]:
    """Expand TextRun list into (char, style_run) pairs."""
    flat: list[Tuple[str, TextRun]] = []
    for r in runs:
        for ch in r.text:
            flat.append((ch, r))
    return flat


def _compress(flat: List[Tuple[str, TextRun]]) -> List[TextRun]:
    """Re-group (char, style) pairs back into minimal TextRun segments."""
    if not flat:
        return [TextRun("")]
    result: list[TextRun] = []
    chars = [flat[0][0]]
    ref = flat[0][1]

    def _same(a: TextRun, b: TextRun) -> bool:
        return (a.bold == b.bold and a.italic == b.italic
                and a.highlight == b.highlight and a.code == b.code
                and a.url == b.url)

    for ch, run in flat[1:]:
        if _same(run, ref):
            chars.append(ch)
        else:
            result.append(TextRun("".join(chars), bold=ref.bold, italic=ref.italic,
                                  highlight=ref.highlight, code=ref.code, url=ref.url))
            chars = [ch]
            ref = run
    result.append(TextRun("".join(chars), bold=ref.bold, italic=ref.italic,
                           highlight=ref.highlight, code=ref.code, url=ref.url))
    return result


def wrap_runs(
    runs: List[TextRun],
    max_width_px: int,
    font: Optional[Any],
    glyph_w: int,
) -> List[List[TextRun]]:
    """Word-wrap a list of TextRuns into display lines.

    Returns a list of lines, each line being a List[TextRun].
    For monospace fonts (Spleen, built-in), glyph_w is the per-char pixel width.
    """
    if max_width_px <= 0:
        return [runs]

    # Operate at character-count level (valid for monospaced fonts).
    max_chars = max(1, max_width_px // glyph_w)
    flat = _flatten(runs)
    n = len(flat)

    lines: list[list[Tuple[str, TextRun]]] = []
    cur_line: list[Tuple[str, TextRun]] = []
    cur_len = 0
    i = 0

    while i < n:
        ch, style = flat[i]

        # Hard newline.
        if ch == "\n":
            lines.append(cur_line)
            cur_line = []
            cur_len = 0
            i += 1
            continue

        # Find the end of the current word (until space or newline).
        j = i
        while j < n and flat[j][0] not in (" ", "\n"):
            j += 1
        word_len = j - i

        if word_len == 0:
            # This character is a space.
            if cur_line and cur_len < max_chars:
                cur_line.append((ch, style))
                cur_len += 1
            elif not cur_line:
                pass  # skip leading space on a wrapped line
            i += 1
            continue

        # Wrap before word if it doesn't fit (and line is non-empty).
        if cur_len > 0 and cur_len + word_len > max_chars:
            lines.append(cur_line)
            cur_line = []
            cur_len = 0

        # If word itself exceeds max_chars, hard-split it.
        while word_len > max_chars - cur_len and word_len > 0:
            take = max_chars - cur_len
            cur_line.extend(flat[i: i + take])
            cur_len += take
            i += take
            word_len -= take
            lines.append(cur_line)
            cur_line = []
            cur_len = 0

        # Append remaining word chars.
        cur_line.extend(flat[i: j])
        cur_len += j - i
        i = j

    lines.append(cur_line)
    return [_compress(line) for line in lines]


# --------------------------------------------------------------------------- #
# Single-line styled run drawing  (respects typewriter budget)
# --------------------------------------------------------------------------- #

def draw_run_line(
    line_runs: List[TextRun],
    x: int,
    y: int,
    theme: Theme,
    font: Optional[Any],
    glyph_w: int,
    glyph_h: int,
    budget: int,   # chars remaining; -1 = unlimited
) -> Tuple[int, int]:
    """Draw one line of styled runs left-to-right.

    Returns (next_x_after_last_run, remaining_budget).
    Bold: text drawn at x and x+1 (fake-bold pixel doubling).
    Italic: accent colour.
    Highlight: accent rect behind, bg-coloured text.
    Code: fg rect behind (dark pill), bg-coloured text.
    Link: accent colour + 1-px underline below glyph.
    """
    cx = x
    for run in line_runs:
        text = run.text
        if budget >= 0:
            text = text[:max(0, budget)]
            budget -= len(text)

        if not text:
            if budget == 0:
                break
            continue

        w = _text_width(text, font, glyph_w)

        # --- Choose colour and optional background rect ---
        if run.math:
            # Inline math: show LaTeX source in muted colour.
            # Full inline-image rendering is deferred to a later phase.
            col = theme.muted
        elif run.highlight:
            pyxel.rect(cx, y - 1, w, glyph_h + 2, theme.accent)
            col = theme.bg
        elif run.code:
            pyxel.rect(cx - 1, y - 1, w + 2, glyph_h + 2, theme.fg)
            col = theme.bg
        elif run.url:
            col = theme.accent
        elif run.italic:
            col = theme.accent   # lighter shade signals italics
        else:
            col = theme.fg

        # --- Draw text ---
        _draw_text(cx, y, text, col, font)

        if run.bold:
            # Fake-bold: draw again shifted one pixel right.
            _draw_text(cx + 1, y, text, col, font)

        if run.url:
            pyxel.rect(cx, y + glyph_h, w, 1, theme.accent)

        cx += w
        if budget == 0:
            break

    return cx, budget


# --------------------------------------------------------------------------- #
# Renderer
# --------------------------------------------------------------------------- #

class SlideRenderer:
    def __init__(
        self,
        theme: Theme,
        width: int,
        height: int,
        fonts: Optional[FontSet] = None,
        base_dir: Optional[Path] = None,
    ) -> None:
        self.theme = theme
        self.width = width
        self.height = height
        self.fonts = fonts or FontSet.fallback()
        self.base_dir = base_dir  # used to resolve relative image paths
        self._image_cache: Dict[str, Optional[List[List[int]]]] = {}

    # --- public ----------------------------------------------------------- #

    def draw(self, slide: Slide, reveal_budget: int = -1) -> None:
        """Draw the slide. reveal_budget = -1 means show everything."""
        pyxel.cls(self.theme.bg)
        if slide.is_section_title:
            self._draw_section_title(slide)
        else:
            self._draw_content(slide, reveal_budget)

    # --- section-title slide ---------------------------------------------- #

    def _draw_section_title(self, slide: Slide) -> None:
        title = ""
        subtitle_runs: List[TextRun] = []

        for b in slide.blocks:
            if isinstance(b, Heading) and b.level == 1 and not title:
                title = b.text
            elif isinstance(b, Paragraph) and not subtitle_runs:
                subtitle_runs = b.runs

        f = self.fonts
        lg_font, lgw, lgh = f.heading_lg, f.heading_lg_w, f.heading_lg_h

        title_w = _text_width(title, lg_font, lgw)

        if lg_font is None:
            # Use pixel-doubling trick for the built-in font.
            scale = 4
            while scale > 1 and len(title) * BUILTIN_GLYPH_W * scale > self.width - 2 * self.theme.padding:
                scale -= 1
            title_w = len(title) * BUILTIN_GLYPH_W * scale
            lgh = BUILTIN_GLYPH_H * scale
            x = (self.width - title_w) // 2
            y = (self.height - lgh) // 2
            _draw_text_scaled_builtin(x, y, title, self.theme.fg, scale)
        else:
            if title_w > self.width - 2 * self.theme.padding:
                # Truncate with ellipsis.
                while title_w > self.width - 2 * self.theme.padding and title:
                    title = title[:-1]
                    title_w = _text_width(title + "...", lg_font, lgw)
                title += "..."
                title_w = _text_width(title, lg_font, lgw)
            x = (self.width - title_w) // 2
            y = (self.height - lgh) // 2
            _draw_text(x, y, title, self.theme.fg, lg_font)

        if subtitle_runs:
            md_font, mdw, mdh = f.heading_md, f.heading_md_w, f.heading_md_h
            sub_text = "".join(r.text for r in subtitle_runs)
            sub_w = _text_width(sub_text, md_font, mdw)
            sx = (self.width - sub_w) // 2
            sy = y + lgh + 8
            _draw_text(sx, sy, sub_text, self.theme.accent, md_font)

    # --- content slide ---------------------------------------------------- #

    def _draw_content(self, slide: Slide, reveal_budget: int = -1) -> None:
        pad = self.theme.padding
        x, y = pad, pad
        max_w = self.width - 2 * pad
        budget = reveal_budget  # mutable local

        for block in slide.blocks:
            if isinstance(block, Heading):
                y = self._draw_heading(block, x, y, max_w)
            elif isinstance(block, Paragraph):
                y, budget = self._draw_paragraph(block, x, y, max_w, budget)
            elif isinstance(block, ListBlock):
                y, budget = self._draw_list(block, x, y, max_w, budget)
            elif isinstance(block, CodeBlock):
                y = self._draw_codeblock(block, x, y, max_w)
            elif isinstance(block, ImageBlock):
                y = self._draw_imageblock(block, x, y, max_w)
            elif isinstance(block, MathBlock):
                y = self._draw_mathblock(block, x, y, max_w)

            if y >= self.height - pad:
                break  # Overflow clipping (scroll / auto-split in a later phase).

    # --- block drawers ---------------------------------------------------- #

    def _draw_heading(self, h: Heading, x: int, y: int, max_w: int) -> int:
        f = self.fonts
        if h.level == 1:
            font, fw, fh = f.heading_lg, f.heading_lg_w, f.heading_lg_h
            col = self.theme.fg
            # Center H1 when it appears inside a content slide.
            tw = _text_width(h.text, font, fw)
            if font is None:
                scale = 3
                tw = len(h.text) * BUILTIN_GLYPH_W * scale
                fh = BUILTIN_GLYPH_H * scale
                x_head = (self.width - tw) // 2
                _draw_text_scaled_builtin(x_head, y, h.text, col, scale)
            else:
                x_head = max(x, (self.width - tw) // 2)
                _draw_text(x_head, y, h.text, col, font)
            y += fh + self.theme.line_spacing + 4
            return y

        elif h.level == 2:
            font, fw, fh = f.heading_md, f.heading_md_w, f.heading_md_h
            col = self.theme.fg
        elif h.level == 3:
            font, fw, fh = f.heading_sm, f.heading_sm_w, f.heading_sm_h
            col = self.theme.accent
        else:
            font, fw, fh = None, BUILTIN_GLYPH_W, BUILTIN_GLYPH_H
            col = self.theme.accent

        lines = wrap_runs(plain(h.text), max_w, font, fw)
        for line_runs in lines:
            if font is None:
                scale = 2 if h.level <= 3 else 1
                _draw_text_scaled_builtin(x, y, h.text, col, scale)
            else:
                cx = x
                for run in line_runs:
                    _draw_text(cx, y, run.text, col, font)
                    cx += _text_width(run.text, font, fw)
            y += fh + self.theme.line_spacing

        if h.level in (2, 3):
            pyxel.rect(x, y, max_w, 1, self.theme.accent)
            y += 5
        else:
            y += 4
        return y

    def _draw_paragraph(
        self,
        p: Paragraph,
        x: int,
        y: int,
        max_w: int,
        budget: int,
    ) -> Tuple[int, int]:
        f = self.fonts
        font, fw, fh = f.body, f.body_w, f.body_h
        lines = wrap_runs(p.runs, max_w, font, fw)

        for line_runs in lines:
            if budget == 0:
                break
            _, budget = draw_run_line(
                line_runs, x, y,
                self.theme, font, fw, fh,
                budget,
            )
            y += fh + self.theme.line_spacing

        return y + 4, budget

    def _draw_list(
        self,
        lst: ListBlock,
        x: int,
        y: int,
        max_w: int,
        budget: int,
    ) -> Tuple[int, int]:
        f = self.fonts
        font, fw, fh = f.body, f.body_w, f.body_h

        for idx, item_runs in enumerate(lst.items, start=1):
            bullet = f"{idx}." if lst.ordered else "*"
            indent = x + fw * (len(bullet) + 1)
            item_max_w = max_w - (indent - x)

            lines = wrap_runs(item_runs, item_max_w, font, fw)

            for li, line_runs in enumerate(lines):
                if budget == 0:
                    break
                if li == 0:
                    _draw_text(x, y, bullet, self.theme.accent, font)
                _, budget = draw_run_line(
                    line_runs, indent, y,
                    self.theme, font, fw, fh,
                    budget,
                )
                y += fh + self.theme.line_spacing

            if budget == 0:
                break

        return y + 4, budget

    def _draw_imageblock(self, ib: ImageBlock, x: int, y: int, max_w: int) -> int:
        """Draw a dithered image block, centered horizontally.

        On first call the image is loaded + dithered and cached by path.
        Subsequent frames use the cached pixel array.
        Falls back to a placeholder rectangle + alt text when Pillow is absent
        or the file cannot be opened.
        """
        pad = self.theme.padding
        max_img_h = self.height // 2  # don't let one image eat the whole slide

        cache_key = ib.path
        if cache_key not in self._image_cache:
            # Resolve the path relative to the deck directory.
            if self.base_dir:
                full_path = (self.base_dir / ib.path).resolve()
            else:
                full_path = Path(ib.path).resolve()

            if pillow_available() and full_path.exists():
                # Find natural image size for aspect-ratio calculation.
                try:
                    from PIL import Image as _Img  # noqa: PLC0415
                    with _Img.open(full_path) as probe:
                        nat_w, nat_h = probe.size
                except Exception:  # noqa: BLE001
                    nat_w, nat_h = max_w, max_img_h

                tw, th = fit_dimensions(nat_w, nat_h, max_w, max_img_h)
                self._image_cache[cache_key] = dither_to_palette(full_path, tw, th)
            else:
                self._image_cache[cache_key] = None  # placeholder

        pixels = self._image_cache[cache_key]

        if pixels is None:
            # Placeholder: dark rect with alt text.
            ph_h = self.fonts.body_h * 2 + 4
            pyxel.rect(x, y, max_w, ph_h, self.theme.fg)
            alt_label = (f"[{ib.alt}]" if ib.alt else "[image]")[:max_w // self.fonts.body_w]
            _draw_text(x + 4, y + 4, alt_label, self.theme.bg, self.fonts.body)
            return y + ph_h + 4

        img_h = len(pixels)
        img_w = len(pixels[0]) if img_h else 0
        if img_w == 0:
            return y

        # Center horizontally.
        img_x = x + (max_w - img_w) // 2

        for row_idx, row in enumerate(pixels):
            iy = y + row_idx
            if iy >= self.height:
                break
            for col_idx, col in enumerate(row):
                pyxel.pset(img_x + col_idx, iy, col)

        return y + img_h + 4

    def _draw_mathblock(self, mb: MathBlock, x: int, y: int, max_w: int) -> int:
        """Draw a display-math block, centered horizontally.

        On first call the expression is rasterised and cached.  Subsequent
        frames use the cached pixel array.  Falls back to a dark code-style
        panel showing the raw LaTeX source when matplotlib is absent or the
        expression fails to render.
        """
        cache_key = f"math:{mb.expr}"
        max_math_h = self.height // 3  # math should not eat the whole slide

        if cache_key not in self._image_cache:
            if matplotlib_available():
                self._image_cache[cache_key] = render_math(
                    mb.expr, max_w, max_math_h
                )
            else:
                self._image_cache[cache_key] = None

        pixels = self._image_cache[cache_key]

        if pixels is None:
            # Fallback: display raw LaTeX inside a dark code-style panel.
            f = self.fonts
            font, fw, fh = f.mono, f.mono_w, f.mono_h
            display = f"$$ {mb.expr} $$"
            lines = wrap_runs(plain(display), max_w - 8, font, fw)
            ph_h = fh * len(lines) + 8
            pyxel.rect(x, y, max_w, ph_h, self.theme.fg)
            for li, line_runs in enumerate(lines):
                cx = x + 4
                for run in line_runs:
                    _draw_text(cx, y + 4 + li * (fh + 1), run.text, self.theme.muted, font)
                    cx += _text_width(run.text, font, fw)
            return y + ph_h + 4

        img_h = len(pixels)
        img_w = len(pixels[0]) if img_h else 0
        if img_w == 0:
            return y

        # Center horizontally.
        img_x = x + (max_w - img_w) // 2
        for row_idx, row in enumerate(pixels):
            iy = y + row_idx
            if iy >= self.height:
                break
            for col_idx, col in enumerate(row):
                pyxel.pset(img_x + col_idx, iy, col)

        return y + img_h + 4

    def _draw_codeblock(self, cb: CodeBlock, x: int, y: int, max_w: int) -> int:
        """Draw a syntax-highlighted code panel."""
        f = self.fonts
        font, fw, fh = f.mono, f.mono_w, f.mono_h
        line_h = fh + 1
        pad = 3  # inner horizontal + vertical padding
        max_chars = max(1, (max_w - pad * 2) // fw)

        # Tokenize into per-line spans (Pygments or plain fallback).
        token_lines = tokenize_lines(cb.code, cb.language)

        # Truncate token lines that overflow horizontally.
        def _truncate(spans: list) -> list:
            """Clip spans to max_chars, appending '>' marker."""
            total = 0
            out: list = []
            for text, role in spans:
                remaining = max_chars - total
                if remaining <= 0:
                    break
                if len(text) <= remaining:
                    out.append((text, role))
                    total += len(text)
                else:
                    out.append((text[: remaining - 1] + ">", role))
                    total = max_chars
                    break
            return out

        display_lines = [_truncate(spans) for spans in token_lines]

        block_h = line_h * len(display_lines) + pad * 2
        pyxel.rect(x, y, max_w, block_h, self.theme.fg)

        for i, spans in enumerate(display_lines):
            cx = x + pad
            ty = y + pad + i * line_h
            for text, role in spans:
                col = role_to_color(role, self.theme)
                _draw_text(cx, ty, text, col, font)
                cx += _text_width(text, font, fw)

        return y + block_h + 4


# --------------------------------------------------------------------------- #
# Fallback: pixel-doubling for Pyxel's built-in 4x6 font
# --------------------------------------------------------------------------- #

def _draw_text_scaled_builtin(x: int, y: int, s: str, col: int, scale: int) -> None:
    """Render with built-in font and integer pixel-scale blit (no external font)."""
    if scale <= 1:
        pyxel.text(x, y, s, col)
        return
    w = max(1, len(s) * BUILTIN_GLYPH_W)
    h = BUILTIN_GLYPH_H
    img = pyxel.Image(w, h)
    sentinel = 0
    img.cls(sentinel)
    img.text(0, 0, s, col)
    for py_ in range(h):
        for px_ in range(w):
            c = img.pget(px_, py_)
            if c == sentinel and col != sentinel:
                continue
            pyxel.rect(x + px_ * scale, y + py_ * scale, scale, scale, c)


# --------------------------------------------------------------------------- #
# Plain text wrap helper (kept for CLI / tests that still import it)
# --------------------------------------------------------------------------- #

def wrap_text(text: str, max_width_px: int, scale: int = 1) -> List[str]:
    """Greedy word-wrap (plain text). Returns list of line strings."""
    font_w = BUILTIN_GLYPH_W * scale
    lines = wrap_runs(plain(text), max_width_px, None, font_w)
    return ["".join(r.text for r in line) for line in lines]


# Legacy alias.
draw_text_scaled = _draw_text_scaled_builtin
