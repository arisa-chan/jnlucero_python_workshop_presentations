"""Unit tests for pyxel_slides.mathtext and the math parser path (Phase 5)."""

from __future__ import annotations

import pytest

from pyxel_slides.ir import MathBlock, Paragraph, TextRun
from pyxel_slides.mathtext import matplotlib_available, render_math
from pyxel_slides.parser import parse_markdown


# --------------------------------------------------------------------------- #
# matplotlib_available
# --------------------------------------------------------------------------- #

def test_matplotlib_available_returns_bool():
    result = matplotlib_available()
    assert isinstance(result, bool)


def test_render_math_no_matplotlib_returns_none(monkeypatch):
    import pyxel_slides.mathtext as _m
    monkeypatch.setattr(_m, "_MATPLOTLIB", False)
    result = _m.render_math("x^2", 100, 50)
    assert result is None


# --------------------------------------------------------------------------- #
# render_math (requires matplotlib)
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not matplotlib_available(), reason="matplotlib not installed")
def test_render_math_returns_2d_list():
    result = render_math(r"\frac{a}{b}", 200, 80)
    assert result is not None, "Expected a pixel array"
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], list)


@pytest.mark.skipif(not matplotlib_available(), reason="matplotlib not installed")
def test_render_math_indices_in_range():
    from pyxel_slides.mathtext import _GAMEBOY_PALETTE
    result = render_math(r"E = mc^2", 200, 80)
    assert result is not None
    n_pal = len(_GAMEBOY_PALETTE)
    for row in result:
        for idx in row:
            assert 0 <= idx < n_pal, f"Palette index {idx} out of range"


@pytest.mark.skipif(not matplotlib_available(), reason="matplotlib not installed")
def test_render_math_respects_max_dimensions():
    max_w, max_h = 100, 60
    result = render_math(r"x^2 + y^2 = z^2", max_w, max_h)
    assert result is not None
    assert len(result) <= max_h, "Height exceeds max_h"
    assert all(len(row) <= max_w for row in result), "Width exceeds max_w"


@pytest.mark.skipif(not matplotlib_available(), reason="matplotlib not installed")
def test_render_math_invalid_expr_does_not_crash():
    # An invalid expression should return None or a valid array, never raise.
    try:
        result = render_math(r"\invalid{{{", 100, 50)
        # Either None or a valid 2D array is acceptable.
        if result is not None:
            assert isinstance(result, list)
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"render_math raised unexpectedly: {exc}")


@pytest.mark.skipif(not matplotlib_available(), reason="matplotlib not installed")
def test_render_math_rows_same_width():
    result = render_math(r"\sum_{i=0}^{n} i", 200, 80)
    assert result is not None
    widths = {len(row) for row in result}
    assert len(widths) == 1, f"Rows have inconsistent widths: {widths}"


# --------------------------------------------------------------------------- #
# Parser: MathBlock detection
# --------------------------------------------------------------------------- #

def test_math_block_basic():
    """$$...$$ on its own paragraph → MathBlock."""
    md = "## Slide\n\n$$E = mc^2$$\n"
    slides = parse_markdown(md)
    math_blocks = [b for b in slides[0].blocks if isinstance(b, MathBlock)]
    assert len(math_blocks) == 1


def test_math_block_expr_content():
    md = "$$\\frac{a}{b}$$\n"
    slides = parse_markdown(md)
    mb = slides[0].blocks[0]
    assert isinstance(mb, MathBlock)
    assert "frac" in mb.expr


def test_math_block_multiline():
    """Multi-line display math."""
    md = "$$\n\\int_0^1 x\\,dx = \\frac{1}{2}\n$$\n"
    slides = parse_markdown(md)
    mb = next((b for b in slides[0].blocks if isinstance(b, MathBlock)), None)
    assert mb is not None
    assert "int" in mb.expr


def test_math_block_does_not_emit_paragraph():
    md = "$$x + y = z$$\n"
    slides = parse_markdown(md)
    paragraphs = [b for b in slides[0].blocks if isinstance(b, Paragraph)]
    assert len(paragraphs) == 0


# --------------------------------------------------------------------------- #
# Parser: inline math → TextRun(math=True)
# --------------------------------------------------------------------------- #

def test_inline_math_in_paragraph():
    """$...$ inline in text → at least one TextRun with math=True."""
    md = "The area is $\\pi r^2$ for a circle.\n"
    slides = parse_markdown(md)
    block = slides[0].blocks[0]
    assert isinstance(block, Paragraph)
    math_runs = [r for r in block.runs if r.math]
    assert len(math_runs) >= 1


def test_inline_math_expr_stored_in_text():
    md = "Consider $\\alpha + \\beta = \\gamma$ here.\n"
    slides = parse_markdown(md)
    block = slides[0].blocks[0]
    assert isinstance(block, Paragraph)
    math_run = next((r for r in block.runs if r.math), None)
    assert math_run is not None
    assert "alpha" in math_run.text or "\\alpha" in math_run.text


def test_inline_math_mixed_with_plain_text():
    """Surrounding text is split into plain TextRuns; the math run is separate."""
    md = "Start $x$ end.\n"
    slides = parse_markdown(md)
    block = slides[0].blocks[0]
    assert isinstance(block, Paragraph)
    plain_runs = [r for r in block.runs if not r.math and r.text.strip()]
    math_runs = [r for r in block.runs if r.math]
    assert len(plain_runs) >= 1
    assert len(math_runs) == 1


def test_inline_math_is_not_plain():
    """TextRun with math=True has is_plain == False."""
    run = TextRun(text=r"\pi", math=True)
    assert not run.is_plain


def test_plain_textrun_is_still_plain():
    run = TextRun(text="hello")
    assert run.is_plain


# --------------------------------------------------------------------------- #
# TextRun.math interaction with existing flags
# --------------------------------------------------------------------------- #

def test_textrun_math_field_default_false():
    run = TextRun(text="x")
    assert run.math is False


def test_textrun_math_and_bold_both_set():
    """math and bold can coexist on the same run (unusual but not forbidden)."""
    run = TextRun(text=r"x^2", math=True, bold=True)
    assert run.math
    assert run.bold
    assert not run.is_plain
