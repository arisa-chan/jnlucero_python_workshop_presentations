"""Slide renderer.

Phase 6: clickable hyperlinks.
  - draw_run_line records hit-areas (x, y, w, h, url) in a link_areas list.
  - SlideRenderer.links is rebuilt on every draw() call.
  - _hit_test(links, mx, my) returns the URL under the mouse, or None.

Phase 3 (retained): Pygments syntax highlighting.
Phase 2 (retained): BDF fonts, styled TextRun rendering, typewriter reveal.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# (x, y, width, height, url) — pixel bounding box of a rendered hyperlink.
LinkArea = Tuple[int, int, int, int, str]

import pyxel

from .assets.fonts import FontSet
from .dither import dither_to_palette, fit_dimensions, pillow_available
from .highlight import role_to_color, tokenize_lines
from .ir import CanvasBlock, CodeBlock, ColumnBreak, Heading, ImageBlock, ListBlock, MathBlock, Paragraph, Slide, SpriteBlock, TableBlock, TextRun, plain
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

def _draw_italic(x: int, y: int, text: str, col: int, font: Optional[Any],
                 glyph_w: int, glyph_h: int, bg_col: int) -> None:
    """Draw text with a per-row horizontal shear that simulates italic.

    The top row is shifted right by ``slant`` pixels; the bottom row is at
    the normal position.  Each intermediate row is shifted proportionally.
    This works for any font size because we read back rendered pixels with
    ``pyxel.screen.pget()`` and redraw them with the shear applied.
    """
    slant = max(1, glyph_h // 4)  # 2px for 8px tall, 4px for 16px tall
    # First, draw the text normally so the pixels are on screen.
    _draw_text(x, y, text, col, font)
    tw = _text_width(text, font, glyph_w)
    # Now shear the rendered pixels row by row (top → max shift, bottom → 0).
    for row in range(glyph_h):
        shift = int(round(slant * (glyph_h - 1 - row) / max(1, glyph_h - 1)))
        if shift == 0:
            continue
        # Read the rendered row.
        pixels = [pyxel.screen.pget(x + ci, y + row) for ci in range(tw)]
        # Erase the original row (and the area the shift may reveal).
        for ci in range(tw + shift):
            pyxel.pset(x + ci, y + row, bg_col)
        # Write back with the horizontal shift.
        for ci, p in enumerate(pixels):
            pyxel.pset(x + ci + shift, y + row, p)


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
        if r.newline:
            # Insert a newline character for explicit line breaks
            flat.append(("\n", r))
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
                and a.url == b.url and a.math == b.math)

    for ch, run in flat[1:]:
        if _same(run, ref):
            chars.append(ch)
        else:
            result.append(TextRun("".join(chars), bold=ref.bold, italic=ref.italic,
                                  highlight=ref.highlight, code=ref.code, url=ref.url,
                                  math=ref.math))
            chars = [ch]
            ref = run
    result.append(TextRun("".join(chars), bold=ref.bold, italic=ref.italic,
                           highlight=ref.highlight, code=ref.code, url=ref.url,
                           math=ref.math))
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
    Math runs are treated as unbreakable atoms so that LaTeX expressions are
    never split across lines (which would produce invalid partial expressions).
    """
    if max_width_px <= 0:
        return [runs]

    # Operate at character-count level (valid for monospaced fonts).
    max_chars = max(1, max_width_px // glyph_w)

    # Replace spaces within math runs with a private-use sentinel so the
    # word-wrap logic never breaks a math expression at an internal space.
    _SPC = "\u00A0"
    safe_runs = []
    for r in runs:
        if r.math and " " in r.text:
            safe_runs.append(TextRun(
                r.text.replace(" ", _SPC),
                bold=r.bold, italic=r.italic, highlight=r.highlight,
                code=r.code, url=r.url, math=True,
            ))
        else:
            safe_runs.append(r)

    flat = _flatten(safe_runs)
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
    compressed = [_compress(line) for line in lines]

    # Restore sentinel back to real spaces within math runs.
    result: list[list[TextRun]] = []
    for line in compressed:
        fixed: list[TextRun] = []
        for run in line:
            if run.math and _SPC in run.text:
                fixed.append(TextRun(
                    run.text.replace(_SPC, " "),
                    bold=run.bold, italic=run.italic, highlight=run.highlight,
                    code=run.code, url=run.url, math=True,
                ))
            else:
                fixed.append(run)
        result.append(fixed)
    return result


# --------------------------------------------------------------------------- #
# Single-line styled run drawing  (respects typewriter budget)
# --------------------------------------------------------------------------- #

def _hit_test(
    links: List[LinkArea],
    mx: int,
    my: int,
) -> Optional[str]:
    """Return the URL of the first link whose rect contains (mx, my), or None."""
    for x, y, w, h, url in links:
        if x <= mx < x + w and y <= my < y + h:
            return url
    return None


def draw_run_line(
    line_runs: List[TextRun],
    x: int,
    y: int,
    theme: Theme,
    font: Optional[Any],
    glyph_w: int,
    glyph_h: int,
    budget: int,   # chars remaining; -1 = unlimited
    link_areas: Optional[List[LinkArea]] = None,
    math_cache: Optional[Dict[str, Optional[List[List[int]]]]] = None,
    palette_rgb: Optional[List[Tuple[int, int, int]]] = None,
    bold_font: Optional[Any] = None,
    italic_font: Optional[Any] = None,
) -> Tuple[int, int]:
    """Draw one line of styled runs left-to-right.

    Returns (next_x_after_last_run, remaining_budget).
    Bold: text drawn at x and x+1 (fake-bold pixel doubling).
    Italic: muted colour.
    Highlight: eff_highlight_bg rect + eff_highlight_fg text.
    Code: eff_code_pill rect + eff_code_pill_fg text.
    Link: eff_link colour + 1-px underline below glyph.
         Appends (x, y, w, h, url) to link_areas when provided.
    Math (inline $...$): rendered as a small image when math_cache and
         palette_rgb are provided; falls back to muted raw LaTeX text.
    """
    cx = x
    for run in line_runs:
        text = run.text
        # Math runs: don't consume typewriter budget (rendered as images, not chars).
        if budget >= 0 and not run.math:
            text = text[:max(0, budget)]
            budget -= len(text)

        if not text:
            if budget == 0:
                break
            continue

        # --- Inline math: render as a dithered image when possible ---
        if run.math and math_cache is not None and palette_rgb is not None and matplotlib_available():
            cache_key = f"imath:{glyph_h}:{run.text}"
            if cache_key not in math_cache:
                # 3× supersampling: render at 3× the natural font-size then
                # LANCZOS-downscale to glyph_h so math matches normal text size.
                # At 100 DPI, font_size pt ≈ font_size × (100/72) px cap-height;
                # glyph_h × 2.16 = glyph_h × 3 × 0.72 gives a 3× supersample.
                math_cache[cache_key] = render_math(
                    run.text,
                    max_w=800,
                    max_h=glyph_h * 12,  # generous ceiling for the 3× render
                    font_size=max(9.0, glyph_h * 2.16),
                    palette_rgb=palette_rgb,
                    target_h=glyph_h,
                    pad_px=2,
                )
            pixels = math_cache.get(cache_key)
            if pixels is not None:
                img_h = len(pixels)
                img_w = len(pixels[0]) if img_h else 0
                if img_w > 0:
                    # Bottom-align with the text line so the math baseline
                    # sits near the text baseline rather than floating above.
                    vy = y + max(0, glyph_h - img_h)
                    for row_idx, row_pix in enumerate(pixels):
                        iy = vy + row_idx
                        for col_idx, pval in enumerate(row_pix):
                            pyxel.pset(cx + col_idx, iy, pval)
                    cx += img_w + 2
                if budget == 0:
                    break
                continue  # skip normal text drawing below

        w = _text_width(text, font, glyph_w)

        # --- Choose colour and optional background rect ---
        if run.math:
            # Fallback: show LaTeX source in muted colour (no matplotlib).
            col = theme.muted
        elif run.highlight:
            pyxel.rect(cx, y - 1, w, glyph_h + 2, theme.eff_highlight_bg)
            col = theme.eff_highlight_fg
        elif run.code:
            pyxel.rect(cx - 1, y - 1, w + 2, glyph_h + 2, theme.eff_code_pill)
            col = theme.eff_code_pill_fg
        elif run.url:
            col = theme.eff_link
        elif run.italic:
            col = theme.fg  # full colour; shearing provides the visual lean
        else:
            col = theme.fg

        # --- Choose the effective font for this run ---
        eff_font = font
        if run.bold and not run.code and not run.math and bold_font is not None:
            eff_font = bold_font
        elif run.italic and not run.code and not run.math and italic_font is not None:
            eff_font = italic_font

        # --- Draw text ---
        if run.italic and not run.code and not run.math and italic_font is None:
            # Fallback italic: pixel-shear effect.
            _draw_italic(cx, y, text, col, font, glyph_w, glyph_h, theme.bg)
        else:
            _draw_text(cx, y, text, col, eff_font)

        if run.bold and (bold_font is None) and not run.code and not run.math:
            # Fallback bold: fake-bold pixel doubling.
            _draw_text(cx + 1, y, text, col, font)

        if run.url:
            pyxel.rect(cx, y + glyph_h, w, 1, theme.eff_link)
            if link_areas is not None:
                link_areas.append((cx, y, w, glyph_h, run.url))

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
        self.links: List[LinkArea] = []  # populated during each draw()

    # --- public ----------------------------------------------------------- #

    def draw(self, slide: Slide, reveal_budget: int = -1) -> None:
        """Draw the slide. reveal_budget = -1 means show everything."""
        self.links = []  # reset hit-areas for this frame
        pyxel.cls(self.theme.bg)
        if slide.is_section_title:
            self._draw_section_title(slide)
        else:
            self._draw_content(slide, reveal_budget)

    # --- section-title slide ---------------------------------------------- #

    def _draw_section_title(self, slide: Slide) -> None:
        title = ""
        subtitle_runs: List[TextRun] = []
        logo_block: Optional[ImageBlock] = None

        for b in slide.blocks:
            if isinstance(b, Heading) and b.level == 1 and not title:
                title = b.text
            elif isinstance(b, Paragraph) and not subtitle_runs:
                subtitle_runs = b.runs
            elif isinstance(b, ImageBlock) and not logo_block and not title:
                # Image before H1 is treated as a logo
                logo_block = b

        f = self.fonts
        lg_font, lgw, lgh = f.heading_lg, f.heading_lg_w, f.heading_lg_h

        # Render logo at the top if present
        pad = self.theme.padding
        logo_height = 0
        if logo_block:
            max_logo_w = self.width - 2 * pad
            max_logo_h = self.height // 3  # logo can take up to 1/3 of slide height
            logo_height = self._draw_imageblock(logo_block, pad, pad, max_logo_w) - pad

        title_lines = title.split("\n") if title else [""]
        title_max_w = self.width - 2 * pad
        title_gap = self.theme.line_spacing

        if lg_font is None:
            # Use pixel-doubling trick for the built-in font.
            scale = 4
            while scale > 1:
                title_w = max(
                    (len(line) * BUILTIN_GLYPH_W * scale for line in title_lines),
                    default=0,
                )
                if title_w <= title_max_w:
                    break
                scale -= 1
            lgh = BUILTIN_GLYPH_H * scale
            title_block_h = len(title_lines) * lgh + max(0, len(title_lines) - 1) * title_gap
            # Position title: center vertically, accounting for logo
            available_height = self.height - logo_height
            y = logo_height + (available_height - title_block_h) // 2
            for line in title_lines:
                title_w = len(line) * BUILTIN_GLYPH_W * scale
                x = (self.width - title_w) // 2
                _draw_text_scaled_builtin(x, y, line, self.theme.eff_heading, scale)
                y += lgh + title_gap
        else:
            fitted_lines: list[str] = []
            for line in title_lines:
                fitted = line
                title_w = _text_width(fitted, lg_font, lgw)
                if title_w > title_max_w:
                    # Truncate each explicit title line with ellipsis.
                    while fitted and _text_width(fitted + "...", lg_font, lgw) > title_max_w:
                        fitted = fitted[:-1]
                    if fitted:
                        fitted += "..."
                    elif _text_width("...", lg_font, lgw) <= title_max_w:
                        fitted = "..."
                fitted_lines.append(fitted)
            title_lines = fitted_lines
            title_block_h = len(title_lines) * lgh + max(0, len(title_lines) - 1) * title_gap
            # Position title: center vertically, accounting for logo
            available_height = self.height - logo_height
            y = logo_height + (available_height - title_block_h) // 2
            for line in title_lines:
                title_w = _text_width(line, lg_font, lgw)
                x = (self.width - title_w) // 2
                _draw_text(x, y, line, self.theme.eff_heading, lg_font)
                y += lgh + title_gap

        if subtitle_runs:
            md_font, mdw, mdh = f.heading_md, f.heading_md_w, f.heading_md_h
            sub_max_w = self.width - 2 * pad
            sub_lines = wrap_runs(subtitle_runs, sub_max_w, md_font, mdw)
            sy = y - title_gap + 8
            for sub_line_runs in sub_lines:
                line_text = "".join(r.text for r in sub_line_runs)
                lw = _text_width(line_text, md_font, mdw)
                sx = max(pad, (self.width - lw) // 2)
                _draw_text(sx, sy, line_text, self.theme.accent, md_font)
                sy += mdh + 4

    # --- content slide ---------------------------------------------------- #

    def _draw_blocks(
        self,
        blocks: List,
        x: int,
        y: int,
        max_w: int,
        budget: int,
    ) -> Tuple[int, int]:
        """Draw a sequence of blocks at (x, y) within max_w.

        Returns (final_y, remaining_budget).  ColumnBreak nodes are skipped.
        """
        pad = self.theme.padding
        for block in blocks:
            if y >= self.height - pad:
                break
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
            elif isinstance(block, CanvasBlock):
                y = self._draw_canvasblock(block, x, y, max_w)
            elif isinstance(block, SpriteBlock):
                y = self._draw_spriteblock(block, x, y, max_w)
            elif isinstance(block, TableBlock):
                y = self._draw_tableblock(block, x, y, max_w)
        return y, budget

    def _draw_content(self, slide: Slide, reveal_budget: int = -1) -> None:
        pad = self.theme.padding
        budget = reveal_budget

        # Filter blocks based on current step for progressive display
        if slide.step > 0:
            # Show only blocks with step <= current step
            blocks_to_draw = [b for b in slide.blocks if getattr(b, 'step', 1) <= slide.step]
        else:
            # step = 0 means show all blocks
            blocks_to_draw = slide.blocks

        # Locate a ColumnBreak, if any.
        col_break_idx = next(
            (i for i, b in enumerate(blocks_to_draw) if isinstance(b, ColumnBreak)), -1
        )

        if col_break_idx < 0:
            # Single-column layout.
            self._draw_blocks(blocks_to_draw, pad, pad, self.width - 2 * pad, budget)
            return

        # Two-column layout.
        gap = pad
        col_w = (self.width - 2 * pad - gap) // 2
        full_w = self.width - 2 * pad

        pre_blocks = blocks_to_draw[:col_break_idx]
        post_blocks = blocks_to_draw[col_break_idx + 1:]

        # Leading Heading blocks span the full width above both columns.
        n_headings = next(
            (i for i, b in enumerate(pre_blocks) if not isinstance(b, Heading)),
            len(pre_blocks),
        )
        y = pad
        for b in pre_blocks[:n_headings]:
            y = self._draw_heading(b, pad, y, full_w)

        left_blocks = pre_blocks[n_headings:]

        # Thin vertical divider between the columns.
        divider_x = pad + col_w + gap // 2
        pyxel.line(divider_x, y, divider_x, self.height - pad, self.theme.muted)

        _, budget = self._draw_blocks(left_blocks, pad, y, col_w, budget)
        self._draw_blocks(post_blocks, pad + col_w + gap, y, col_w, budget)

    # --- block drawers ---------------------------------------------------- #

    def _draw_heading(self, h: Heading, x: int, y: int, max_w: int) -> int:
        f = self.fonts
        if h.level == 1:
            font, fw, fh = f.heading_lg, f.heading_lg_w, f.heading_lg_h
            col = self.theme.eff_heading
            if font is None:
                # Built-in font: pixel-double and wrap at max_w.
                scale = 3
                lines_runs = wrap_runs(plain(h.text), max_w, font, BUILTIN_GLYPH_W * scale)
                lh = BUILTIN_GLYPH_H * scale
                for line_runs in lines_runs:
                    line = "".join(r.text for r in line_runs)
                    lw = len(line) * BUILTIN_GLYPH_W * scale
                    x_head = (self.width - lw) // 2
                    _draw_text_scaled_builtin(x_head, y, line, col, scale)
                    y += lh + self.theme.line_spacing
            else:
                # BDF font: use wrap_runs to centre each wrapped line.
                lines_runs = wrap_runs(plain(h.text), max_w, font, fw)
                for line_runs in lines_runs:
                    line_text = "".join(r.text for r in line_runs)
                    lw = _text_width(line_text, font, fw)
                    x_head = max(x, (self.width - lw) // 2)
                    _draw_text(x_head, y, line_text, col, font)
                    y += fh + self.theme.line_spacing
            y += 4
            return y

        elif h.level == 2:
            font, fw, fh = f.heading_md, f.heading_md_w, f.heading_md_h
            col = self.theme.accent
        elif h.level == 3:
            font, fw, fh = f.heading_sm, f.heading_sm_w, f.heading_sm_h
            col = self.theme.accent
        else:
            font, fw, fh = None, BUILTIN_GLYPH_W, BUILTIN_GLYPH_H
            col = self.theme.accent

        scale = 2 if h.level <= 3 else 1
        line_h = fh
        wrap_glyph_w = fw
        if font is None:
            line_h = BUILTIN_GLYPH_H * scale
            wrap_glyph_w = BUILTIN_GLYPH_W * scale

        lines = wrap_runs(plain(h.text), max_w, font, wrap_glyph_w)
        for line_runs in lines:
            line_text = "".join(r.text for r in line_runs)
            if font is None:
                _draw_text_scaled_builtin(x, y, line_text, col, scale)
            else:
                cx = x
                for run in line_runs:
                    _draw_text(cx, y, run.text, col, font)
                    cx += _text_width(run.text, font, fw)
            y += line_h + self.theme.line_spacing

        if h.level == 2:
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
                link_areas=self.links,
                math_cache=self._image_cache,
                palette_rgb=self.theme.palette_as_rgb,
                bold_font=self.fonts.bold,
                italic_font=self.fonts.italic,
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

        ordered_counter = lst.start  # tracks the current number for depth-0 ordered items

        for list_idx, item_runs in enumerate(lst.items):
            depth = lst.depths[list_idx] if list_idx < len(lst.depths) else 0
            depth_indent = depth * fw * 4  # 4 character-widths of indentation per level

            if lst.ordered and depth == 0:
                bullet = f"{ordered_counter}."
                ordered_counter += 1
            else:
                bullet = "*"

            item_x = x + depth_indent
            indent = item_x + fw * (len(bullet) + 1)
            item_max_w = max_w - (indent - x)

            lines = wrap_runs(item_runs, max(fw * 4, item_max_w), font, fw)

            for li, line_runs in enumerate(lines):
                if budget == 0:
                    break
                if li == 0:
                    _draw_text(item_x, y, bullet, self.theme.accent, font)
                _, budget = draw_run_line(
                    line_runs, indent, y,
                    self.theme, font, fw, fh,
                    budget,
                    link_areas=self.links,
                    math_cache=self._image_cache,
                    palette_rgb=self.theme.palette_as_rgb,
                    bold_font=self.fonts.bold,
                    italic_font=self.fonts.italic,
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

        # Include scale in cache key so different scales are cached separately
        cache_key = f"{ib.path}:{ib.scale}"
        if cache_key not in self._image_cache:
            is_url = ib.path.startswith(("http://", "https://"))

            if is_url:
                img_src: Any = ib.path  # URL string — fetched below
            elif self.base_dir:
                img_src = (self.base_dir / ib.path).resolve()
            else:
                img_src = Path(ib.path).resolve()

            src_available = is_url or (isinstance(img_src, Path) and img_src.exists())

            if pillow_available() and src_available:
                import io as _io  # noqa: PLC0415
                import urllib.request as _urlreq  # noqa: PLC0415

                from PIL import Image as _Img  # noqa: PLC0415

                img_open_arg: Any = None
                nat_w, nat_h = max_w, max_img_h
                try:
                    if is_url:
                        req = _urlreq.Request(  # noqa: S310
                            img_src,
                            headers={"User-Agent": "pyxel-slides/1.0 (https://github.com/pyxel-slides/pyxel-slides)"},
                        )
                        with _urlreq.urlopen(req, timeout=10) as resp:  # noqa: S310
                            buf = _io.BytesIO(resp.read())
                        with _Img.open(buf) as probe:
                            nat_w, nat_h = probe.size
                        buf.seek(0)
                        img_open_arg = buf
                    else:
                        with _Img.open(img_src) as probe:
                            nat_w, nat_h = probe.size
                        img_open_arg = img_src
                except Exception:  # noqa: BLE001
                    img_open_arg = None

                if img_open_arg is not None:
                    # Apply scale factor to the target dimensions
                    scaled_max_w = int(max_w * ib.scale)
                    scaled_max_h = int(max_img_h * ib.scale)
                    tw, th = fit_dimensions(nat_w, nat_h, scaled_max_w, scaled_max_h)
                    self._image_cache[cache_key] = dither_to_palette(
                        img_open_arg, tw, th,
                        palette_rgb=self.theme.palette_as_rgb,
                    )
                else:
                    self._image_cache[cache_key] = None
            else:
                self._image_cache[cache_key] = None  # placeholder

        pixels = self._image_cache[cache_key]

        if pixels is None:
            # Placeholder: dark rect with alt text.
            ph_h = self.fonts.body_h * 2 + 4
            pyxel.rect(x, y, max_w, ph_h, self.theme.eff_panel_bg)
            alt_label = (f"[{ib.alt}]" if ib.alt else "[image]")[:max_w // self.fonts.body_w]
            _draw_text(x + 4, y + 4, alt_label, self.theme.eff_code_fg, self.fonts.body)
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

    def _draw_tableblock(self, tb: TableBlock, x: int, y: int, max_w: int) -> int:
        """Draw a GFM pipe table with a header row and data rows."""
        ncols = len(tb.headers)
        if ncols == 0:
            return y

        f = self.fonts
        font, fw, fh = f.body, f.body_w, f.body_h
        pad = 4
        row_h = fh + pad * 2

        # Calculate column widths
        if tb.col_widths:
            # Use specified widths, but ensure they don't exceed max_w
            total_specified = sum(w for w in tb.col_widths if w > 0)
            auto_cols = sum(1 for w in tb.col_widths if w == 0)
            
            col_widths = []
            remaining_w = max_w
            for i, w in enumerate(tb.col_widths):
                if w > 0:
                    # Scale specified width proportionally if total exceeds max_w
                    if total_specified > max_w:
                        scaled_w = int(w * max_w / total_specified)
                        col_widths.append(max(fw * 4, scaled_w))
                    else:
                        col_widths.append(w)
                    remaining_w -= col_widths[-1]
                else:
                    # Auto-width: distribute remaining space
                    if auto_cols > 0:
                        auto_w = max(fw * 4, remaining_w // auto_cols)
                        col_widths.append(auto_w)
                    else:
                        col_widths.append(max(fw * 4, max_w // ncols))
        else:
            # Default: equal width columns
            col_w = max(fw * 4, max_w // ncols)
            col_widths = [col_w] * ncols

        total_w = sum(col_widths)

        # Header row (accent background).
        pyxel.rect(x, y, total_w, row_h, self.theme.accent)
        col_x = x
        for ci, hdr in enumerate(tb.headers):
            col_w = col_widths[ci]
            max_chars = max(1, (col_w - 2 * pad) // fw)
            _draw_text(col_x + pad, y + pad, hdr[:max_chars], self.theme.bg, font)
            col_x += col_w
        y += row_h

        # Separator line.
        pyxel.rect(x, y, total_w, 1, self.theme.accent)
        y += 1

        # Data rows (alternating background).
        for ri, row in enumerate(tb.rows):
            bg = self.theme.eff_panel_bg if ri % 2 == 0 else self.theme.bg
            pyxel.rect(x, y, total_w, row_h, bg)
            col_x = x
            for ci, cell in enumerate(row[:ncols]):
                col_w = col_widths[ci]
                max_chars = max(1, (col_w - 2 * pad) // fw)
                _draw_text(col_x + pad, y + pad, cell[:max_chars], self.theme.fg, font)
                col_x += col_w
            y += row_h

        # Bottom border.
        pyxel.rect(x, y, total_w, 1, self.theme.accent)
        y += 1

        return y + 4

    def _draw_mathblock(self, mb: MathBlock, x: int, y: int, max_w: int) -> int:
        """Draw a display-math block, centered horizontally.

        On first call the expression is rasterised and cached.  Subsequent
        frames use the cached pixel array.  Falls back to a dark code-style
        panel showing the raw LaTeX source when matplotlib is absent or the
        expression fails to render.
        """
        cache_key = f"math:{mb.expr}"
        max_math_h = self.height // 2  # allow up to half the slide height for equations

        if cache_key not in self._image_cache:
            if matplotlib_available():
                self._image_cache[cache_key] = render_math(
                    mb.expr, max_w, max_math_h,
                    palette_rgb=self.theme.palette_as_rgb,
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
            pyxel.rect(x, y, max_w, ph_h, self.theme.eff_panel_bg)
            for li, line_runs in enumerate(lines):
                cx = x + 4
                for run in line_runs:
                    _draw_text(cx, y + 4 + li * (fh + 1), run.text, self.theme.eff_code_fg, font)
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

    def _draw_canvasblock(self, cb: CanvasBlock, x: int, y: int, max_w: int) -> int:
        """Draw a CanvasBlock as a clipped offscreen Pyxel image."""
        canvas = cb.canvas
        pixels = canvas.rasterize()
        img_h = len(pixels)
        img_w = len(pixels[0]) if img_h else 0
        if img_w <= 0 or img_h <= 0:
            return y

        img = pyxel.Image(img_w, img_h)
        for row_idx, row in enumerate(pixels):
            for col_idx, col in enumerate(row):
                img.pset(col_idx, row_idx, col)

        for cmd in canvas.text_commands:
            if not cmd.points:
                continue
            tx, ty = cmd.points[0]
            img.text(tx, ty, cmd.text, cmd.color)

        scale = max(0.1, float(cb.scale))
        available_h = max(1, self.height - y - self.theme.padding)
        if img_w * scale > max_w:
            scale = max_w / img_w
        if img_h * scale > available_h:
            scale = min(scale, available_h / img_h)
        scale = max(0.1, scale)

        drawn_w = max(1, int(round(img_w * scale)))
        drawn_h = max(1, int(round(img_h * scale)))

        if cb.align == "left":
            canvas_x = x
        elif cb.align == "right":
            canvas_x = x + max(0, max_w - drawn_w)
        else:
            canvas_x = x + max(0, (max_w - drawn_w) // 2)

        pyxel.blt(canvas_x, y, img, 0, 0, img_w, img_h, scale=scale)
        return y + drawn_h + 4

    def _draw_codeblock(self, cb: CodeBlock, x: int, y: int, max_w: int) -> int:
        """Draw a syntax-highlighted code panel with a line-number gutter."""
        f = self.fonts
        font, fw, fh = f.mono, f.mono_w, f.mono_h
        line_h = fh + 1
        pad = 3  # inner horizontal + vertical padding

        # Tokenize into per-line spans (Pygments or plain fallback).
        token_lines = tokenize_lines(cb.code, cb.language)
        n_lines = len(token_lines)

        # Line-number gutter geometry.
        #   [pad][right-aligned digits][pad][1px sep][pad][code…][pad]
        n_digits = len(str(max(1, n_lines)))
        gutter_w = pad + fw * n_digits + pad + 1  # includes separator pixel

        max_chars = max(1, (max_w - gutter_w - pad - pad) // fw)

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
        pyxel.rect(x, y, max_w, block_h, self.theme.eff_panel_bg)

        # Vertical separator between gutter and code.
        sep_x = x + pad + fw * n_digits + pad
        pyxel.line(sep_x, y, sep_x, y + block_h - 1, self.theme.muted)

        code_x = sep_x + 1 + pad  # first pixel after separator + a small gap

        for i, spans in enumerate(display_lines):
            ty = y + pad + i * line_h
            # Line number: right-aligned within the digit columns, muted colour.
            lineno = str(i + 1).rjust(n_digits)
            _draw_text(x + pad, ty, lineno, self.theme.muted, font)
            # Code.
            cx = code_x
            for text, role in spans:
                col = role_to_color(role, self.theme)
                _draw_text(cx, ty, text, col, font)
                cx += _text_width(text, font, fw)

        return y + block_h + 4

    def _draw_spriteblock(self, sb: SpriteBlock, x: int, y: int, max_w: int) -> int:
        """Draw a Pyxel image-bank sprite using ``pyxel.blt()``.

        Supports integer/float scaling and automatic frame animation.
        The sprite is centred horizontally within the slide column.
        If ``blt`` raises (e.g. invalid bank index), a placeholder is shown.

        Animation: a horizontal strip of ``frames`` frames, each ``frame_w``
        pixels wide, is cycled at ``anim_fps`` frames-per-second (relative to
        the Pyxel default of 30 fps).
        """
        fw = sb.frame_w if sb.frame_w >= 0 else sb.w

        # Compute current animation frame (assumes ~30 fps app loop).
        period = max(1, 30 // max(1, sb.anim_fps))
        frame_idx = (pyxel.frame_count // period) % max(1, sb.frames)
        src_u = sb.u + frame_idx * fw

        # Pixel size of the drawn sprite.
        scale = float(sb.scale)
        drawn_w = int(fw * scale)
        drawn_h = int(sb.h * scale)

        # Centre horizontally.
        sprite_x = x + max(0, (max_w - drawn_w) // 2)
        sprite_y = y

        colkey = sb.colkey if sb.colkey >= 0 else None

        try:
            pyxel.blt(sprite_x, sprite_y, sb.img, src_u, sb.v, fw, sb.h,
                      colkey, scale=scale)
        except Exception:  # noqa: BLE001
            # Fallback: placeholder panel with descriptor text.
            label = f"[sprite img={sb.img} {fw}\u00d7{sb.h}]"
            ph_h = self.fonts.body_h * 2 + 4
            pyxel.rect(x, y, max_w, ph_h, self.theme.eff_panel_bg)
            _draw_text(x + 4, y + 4, label[:max_w // self.fonts.body_w],
                       self.theme.eff_code_fg, self.fonts.body)
            return y + ph_h + 4

        return y + drawn_h + 4


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
