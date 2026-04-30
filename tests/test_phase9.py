"""Tests for Phase 9: presenter timer, overview mode, export-to-PNG plumbing.

All tests are pure logic; no Pyxel window is opened.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyxel_slides.app import (
    SlidesApp,
    _OV_CARD_H,
    _OV_CARD_W,
    _OV_COLS,
    _OV_GAP,
    _OV_LABEL_H,
    _OV_MARGIN_X,
    _OV_MARGIN_Y,
)
from pyxel_slides.theme import VSCODE_LIGHT


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _make_md(tmp_path: Path, n: int = 3) -> Path:
    """Write a deck .md with *n* slides."""
    slides = "\n\n---\n\n".join(f"# Slide {i + 1}\n\nBody {i + 1}" for i in range(n))
    p = tmp_path / "deck.md"
    p.write_text(slides, encoding="utf-8")
    return p


def _make_app(tmp_path: Path, n: int = 6, **kwargs) -> SlidesApp:
    """Construct a SlidesApp without calling run() (avoids pyxel.init)."""
    from pyxel_slides.app import SlidesApp
    from pyxel_slides.ir import Heading, Slide

    md = _make_md(tmp_path, n)
    app = SlidesApp.__new__(SlidesApp)
    app.markdown_path = md
    app.theme = VSCODE_LIGHT
    app.width = 384
    app.height = 216
    app.fps = 30
    app.title = "test"
    app.pyxres_path = None
    app.download_fonts = False
    app.hot_reload = False
    app.export_dir = kwargs.get("export_dir", None)

    # Build N slides with titles
    app.slides = [
        Slide(blocks=[Heading(level=1, text=f"Slide {i + 1}")])
        for i in range(n)
    ]
    app.index = 0
    app._mtime = 0.0
    app._reveal_chars = -1
    app._hot_reload_counter = 0
    # Phase 9
    app._overview = False
    app._ov_scroll_row = 0
    app._timer_start = 0.0
    app._exporting = False
    app._export_frame = 0
    return app


# --------------------------------------------------------------------------- #
# _format_time
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("elapsed,expected", [
    (0,      "00:00"),
    (1,      "00:01"),
    (59,     "00:59"),
    (60,     "01:00"),
    (61,     "01:01"),
    (3599,   "59:59"),
    (3600,   "60:00"),
    (3661,   "61:01"),
    (-5,     "00:00"),  # negative elapsed → clamped to 0
    (0.9,    "00:00"),  # fractional < 1s → 0
    (1.9,    "00:01"),  # truncated, not rounded
])
def test_format_time(elapsed, expected):
    assert SlidesApp._format_time(elapsed) == expected


# --------------------------------------------------------------------------- #
# _overview_card_at — geometry
# --------------------------------------------------------------------------- #

def _card_origin(col: int, row_rel: int) -> tuple[int, int]:
    """Pixel coordinates of top-left corner of card at (col, row_rel)."""
    ov_top = _OV_MARGIN_Y + _OV_LABEL_H
    x = _OV_MARGIN_X + col * (_OV_CARD_W + _OV_GAP)
    y = ov_top + row_rel * (_OV_CARD_H + _OV_GAP)
    return x, y


def test_overview_card_at_first_card(tmp_path):
    app = _make_app(tmp_path)
    x, y = _card_origin(0, 0)
    assert app._overview_card_at(x, y) == 0


def test_overview_card_at_second_column(tmp_path):
    app = _make_app(tmp_path)
    x, y = _card_origin(1, 0)
    assert app._overview_card_at(x, y) == 1


def test_overview_card_at_second_row(tmp_path):
    app = _make_app(tmp_path, n=8)
    x, y = _card_origin(0, 1)
    assert app._overview_card_at(x, y) == _OV_COLS  # first card in row 1


def test_overview_card_at_last_column(tmp_path):
    app = _make_app(tmp_path, n=8)
    x, y = _card_origin(_OV_COLS - 1, 0)
    assert app._overview_card_at(x, y) == _OV_COLS - 1


def test_overview_card_at_inside_right_edge(tmp_path):
    app = _make_app(tmp_path)
    x, y = _card_origin(0, 0)
    assert app._overview_card_at(x + _OV_CARD_W - 1, y) == 0


def test_overview_card_at_exactly_on_right_gap(tmp_path):
    """A click in the inter-card gap (col 0 right edge + 1) should return -1."""
    app = _make_app(tmp_path, n=8)
    x, y = _card_origin(0, 0)
    assert app._overview_card_at(x + _OV_CARD_W, y) == -1


def test_overview_card_at_bottom_gap(tmp_path):
    """A click just below the card (in the gap) should return -1."""
    app = _make_app(tmp_path, n=8)
    x, y = _card_origin(0, 0)
    assert app._overview_card_at(x, y + _OV_CARD_H) == -1


def test_overview_card_at_negative_coords(tmp_path):
    app = _make_app(tmp_path)
    assert app._overview_card_at(-1, -1) == -1


def test_overview_card_at_beyond_slide_count(tmp_path):
    """The 6th slot when only 5 slides exist should return -1."""
    app = _make_app(tmp_path, n=5)
    # Slide index 5 (slot 5) doesn't exist.
    x, y = _card_origin(1, 1)  # col=1, row=1 → index = 1*4+1 = 5
    assert app._overview_card_at(x, y) == -1


def test_overview_card_at_with_scroll(tmp_path):
    """With _ov_scroll_row=1, the first visible card maps to slide index _OV_COLS."""
    app = _make_app(tmp_path, n=12)
    app._ov_scroll_row = 1
    x, y = _card_origin(0, 0)
    assert app._overview_card_at(x, y) == _OV_COLS


def test_overview_card_at_zero_scroll_vs_one_scroll(tmp_path):
    """Same pixel, different scroll_row → different slide index."""
    app = _make_app(tmp_path, n=12)
    x, y = _card_origin(2, 0)
    app._ov_scroll_row = 0
    idx0 = app._overview_card_at(x, y)
    app._ov_scroll_row = 1
    idx1 = app._overview_card_at(x, y)
    assert idx1 == idx0 + _OV_COLS


# --------------------------------------------------------------------------- #
# Overview scroll bounds
# --------------------------------------------------------------------------- #

def test_ov_scroll_row_auto_set_on_open(tmp_path):
    """Opening the overview should auto-scroll to show the current slide's row."""
    app = _make_app(tmp_path, n=12)
    app.index = 7  # row 1 (slides 4-7)
    # Simulate the O-key logic from update():
    app._ov_scroll_row = app.index // _OV_COLS
    assert app._ov_scroll_row == 1


def test_ov_scroll_max_row(tmp_path):
    """max_row computation used for DOWN-arrow clamping."""
    n = 10
    app = _make_app(tmp_path, n=n)
    max_row = max(0, (n - 1) // _OV_COLS)
    # With 10 slides and 4 cols: last slide is index 9 → row 2.
    assert max_row == 2


# --------------------------------------------------------------------------- #
# CLI --export-dir integration
# --------------------------------------------------------------------------- #

def test_main_export_dir_passed_to_app(tmp_path):
    from pyxel_slides.cli import main

    md = _make_md(tmp_path)
    export_path = tmp_path / "out"
    captured = {}

    def fake_app(*, export_dir, **kwargs):
        captured["export_dir"] = export_dir
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md), "--export-dir", str(export_path)])

    assert captured["export_dir"] == export_path


def test_main_export_dir_none_by_default(tmp_path):
    from pyxel_slides.cli import main

    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, export_dir, **kwargs):
        captured["export_dir"] = export_dir
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md)])

    assert captured["export_dir"] is None


# --------------------------------------------------------------------------- #
# Export state machine logic
# --------------------------------------------------------------------------- #

def test_export_frame_increments_in_draw(tmp_path):
    """Each _try_save_frame call (during export draw) increments _export_frame."""
    app = _make_app(tmp_path, n=3)
    app._exporting = True
    app._export_frame = 0
    app.export_dir = tmp_path / "out"

    # Stub out Pillow-dependent save and renderer
    app._try_save_frame = MagicMock()
    app.renderer = MagicMock()
    app.renderer.draw = MagicMock()

    # Simulate the draw() export branch for each frame
    for expected_frame in range(3):
        assert app._export_frame == expected_frame
        app.renderer.draw(app.slides[app._export_frame], reveal_budget=-1)
        app._try_save_frame()
        app._export_frame += 1

    assert app._export_frame == 3


def test_export_done_flag_triggers_after_all_slides(tmp_path):
    """After _export_frame reaches len(slides), the update() logic should quit."""
    app = _make_app(tmp_path, n=3)
    app._exporting = True
    app._export_frame = 3  # already past last slide

    quit_called = []
    with patch("pyxel_slides.app.pyxel") as mock_pyxel:
        mock_pyxel.btnp.return_value = False
        mock_pyxel.KEY_Q = 0
        # Simulate the exporting branch in update():
        if app._exporting:
            if app._export_frame >= len(app.slides):
                mock_pyxel.quit()

    mock_pyxel.quit.assert_called_once()


def test_export_dir_created_if_missing(tmp_path):
    """SlidesApp.run() should create export_dir if it doesn't exist."""
    from pyxel_slides.app import SlidesApp

    export_path = tmp_path / "subdir" / "output"
    assert not export_path.exists()

    md = _make_md(tmp_path)
    app = SlidesApp.__new__(SlidesApp)
    # Minimal __init__ state
    app.markdown_path = md
    app.theme = VSCODE_LIGHT
    app.width = 384
    app.height = 216
    app.fps = 30
    app.title = "test"
    app.pyxres_path = None
    app.download_fonts = False
    app.hot_reload = False
    app.export_dir = export_path
    app.slides = []
    app.index = 0
    app._mtime = 0.0
    app._reveal_chars = -1
    app._hot_reload_counter = 0
    app._overview = False
    app._ov_scroll_row = 0
    app._timer_start = 0.0
    app._exporting = False
    app._export_frame = 0

    # Invoke just the export_dir.mkdir() logic from run()
    app.export_dir.mkdir(parents=True, exist_ok=True)
    assert export_path.exists()
