"""Unit tests for Phase 6 clickable hyperlink support.

Covers:
  * _hit_test — pure logic, no Pyxel required.
  * draw_run_line collecting link_areas — Pyxel draw calls are patched out.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from pyxel_slides.ir import TextRun
from pyxel_slides.renderer import _hit_test, draw_run_line


# --------------------------------------------------------------------------- #
# Minimal fake theme expected by draw_run_line
# --------------------------------------------------------------------------- #

class _FakeTheme:
    muted         = 3
    fg            = 1
    bg            = 0
    eff_link      = 2
    eff_highlight_bg  = 12
    eff_highlight_fg  = 1
    eff_code_pill     = 13
    eff_code_pill_fg  = 1


_THEME = _FakeTheme()


# --------------------------------------------------------------------------- #
# _hit_test — pure logic tests
# --------------------------------------------------------------------------- #

def test_hit_test_returns_none_for_empty_list():
    assert _hit_test([], 10, 10) is None


def test_hit_test_returns_url_when_inside():
    links = [(5, 10, 40, 8, "https://example.com")]
    assert _hit_test(links, 6, 11) == "https://example.com"


def test_hit_test_returns_none_when_outside():
    links = [(5, 10, 40, 8, "https://example.com")]
    assert _hit_test(links, 100, 100) is None


def test_hit_test_left_edge_inclusive():
    links = [(5, 10, 40, 8, "https://example.com")]
    assert _hit_test(links, 5, 10) == "https://example.com"


def test_hit_test_right_edge_exclusive():
    # x + w = 45 is outside the rect (exclusive)
    links = [(5, 10, 40, 8, "https://example.com")]
    assert _hit_test(links, 45, 10) is None


def test_hit_test_bottom_edge_exclusive():
    # y + h = 18 is outside the rect
    links = [(5, 10, 40, 8, "https://example.com")]
    assert _hit_test(links, 10, 18) is None


def test_hit_test_first_match_wins():
    links = [
        (0, 0, 50, 10, "https://first.com"),
        (0, 0, 50, 10, "https://second.com"),
    ]
    assert _hit_test(links, 5, 5) == "https://first.com"


def test_hit_test_multiple_non_overlapping_rects():
    links = [
        (0,  0, 40, 8, "https://alpha.com"),
        (0, 20, 40, 8, "https://beta.com"),
    ]
    assert _hit_test(links, 5, 1)  == "https://alpha.com"
    assert _hit_test(links, 5, 21) == "https://beta.com"
    assert _hit_test(links, 5, 10) is None   # gap between rects


# --------------------------------------------------------------------------- #
# draw_run_line — link_areas collection (Pyxel patched)
# --------------------------------------------------------------------------- #

_MOCK_PYXEL_ATTRS = {
    "text": MagicMock(),
    "rect": MagicMock(),
}


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_collects_url_area(mock_pyxel):
    """A URL run should append its bounding box to link_areas."""
    run = TextRun("click here", url="https://example.com")
    areas: list = []
    draw_run_line(
        [run], x=10, y=20,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=-1, link_areas=areas,
    )
    assert len(areas) == 1
    x, y, w, h, url = areas[0]
    assert url == "https://example.com"
    assert x == 10
    assert y == 20
    assert w == len("click here") * 4   # glyph_w=4, no custom font
    assert h == 6                        # glyph_h


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_no_url_does_not_add_area(mock_pyxel):
    """Plain, bold, italic runs must NOT add entries to link_areas."""
    runs = [
        TextRun("plain"),
        TextRun("bold text", bold=True),
        TextRun("italic text", italic=True),
    ]
    areas: list = []
    draw_run_line(
        runs, x=0, y=0,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=-1, link_areas=areas,
    )
    assert areas == []


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_multiple_url_runs(mock_pyxel):
    """Each URL run on the same line is tracked separately."""
    runs = [
        TextRun("first", url="https://a.com"),
        TextRun(" "),
        TextRun("second", url="https://b.com"),
    ]
    areas: list = []
    draw_run_line(
        runs, x=0, y=0,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=-1, link_areas=areas,
    )
    assert len(areas) == 2
    assert areas[0][4] == "https://a.com"
    assert areas[1][4] == "https://b.com"


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_no_link_areas_arg_still_works(mock_pyxel):
    """Passing no link_areas (default None) must not raise."""
    run = TextRun("a link", url="https://example.com")
    # Should not raise
    draw_run_line(
        [run], x=0, y=0,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=-1,
    )


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_url_area_x_position_advances(mock_pyxel):
    """Second URL run's x should be after the first non-URL run."""
    runs = [
        TextRun("ABC"),                          # 3 chars × 4px = 12px
        TextRun("link", url="https://z.com"),
    ]
    areas: list = []
    draw_run_line(
        runs, x=0, y=0,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=-1, link_areas=areas,
    )
    assert len(areas) == 1
    x, _, _, _, _ = areas[0]
    assert x == 12   # 3 chars × 4px


@patch("pyxel_slides.renderer.pyxel", **_MOCK_PYXEL_ATTRS)
def test_draw_run_line_typewriter_budget_limits_url_tracking(mock_pyxel):
    """When budget is exhausted before a URL run, no hit area is recorded."""
    runs = [
        TextRun("hello"),            # 5 chars
        TextRun("X", url="https://x.com"),  # comes after budget exhausted
    ]
    areas: list = []
    draw_run_line(
        runs, x=0, y=0,
        theme=_THEME, font=None, glyph_w=4, glyph_h=6,
        budget=5, link_areas=areas,  # only enough for "hello"
    )
    assert areas == []
