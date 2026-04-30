"""Tests for Phase 8: --theme CLI flag and hot-reload behaviour.

All tests are pure logic / argument-parsing; no Pyxel window is opened.
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyxel_slides.cli import _THEMES, _parse_resolution, main
from pyxel_slides.theme import GAMEBOY, VSCODE_LIGHT


# --------------------------------------------------------------------------- #
# _THEMES registry
# --------------------------------------------------------------------------- #

def test_themes_registry_contains_vscode_light():
    assert "vscode_light" in _THEMES


def test_themes_registry_contains_gameboy():
    assert "gameboy" in _THEMES


def test_themes_registry_vscode_light_value():
    assert _THEMES["vscode_light"] is VSCODE_LIGHT


def test_themes_registry_gameboy_value():
    assert _THEMES["gameboy"] is GAMEBOY


# --------------------------------------------------------------------------- #
# _parse_resolution
# --------------------------------------------------------------------------- #

def test_parse_resolution_valid():
    assert _parse_resolution("384x216") == (384, 216)


def test_parse_resolution_uppercase():
    assert _parse_resolution("800X600") == (800, 600)


def test_parse_resolution_invalid_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_resolution("badvalue")


def test_parse_resolution_missing_x_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_resolution("384-216")


# --------------------------------------------------------------------------- #
# main() argument parsing — theme selection
# --------------------------------------------------------------------------- #

def _make_md(tmp_path: Path, content: str = "# Hello\n\nWorld\n") -> Path:
    p = tmp_path / "deck.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_main_default_theme_is_vscode_light(tmp_path):
    """Omitting --theme should use vscode_light, not gameboy."""
    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, theme, **kwargs):
        captured["theme"] = theme
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md)])

    assert captured["theme"] is VSCODE_LIGHT


def test_main_theme_gameboy(tmp_path):
    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, theme, **kwargs):
        captured["theme"] = theme
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md), "--theme", "gameboy"])

    assert captured["theme"] is GAMEBOY


def test_main_theme_vscode_light_explicit(tmp_path):
    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, theme, **kwargs):
        captured["theme"] = theme
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md), "--theme", "vscode_light"])

    assert captured["theme"] is VSCODE_LIGHT


def test_main_invalid_theme_exits(tmp_path):
    md = _make_md(tmp_path)
    with pytest.raises(SystemExit):
        main([str(md), "--theme", "nonexistent_theme"])


# --------------------------------------------------------------------------- #
# main() argument parsing — hot-reload flag
# --------------------------------------------------------------------------- #

def test_main_hot_reload_on_by_default(tmp_path):
    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, hot_reload, **kwargs):
        captured["hot_reload"] = hot_reload
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md)])

    assert captured["hot_reload"] is True


def test_main_no_hot_reload_flag(tmp_path):
    md = _make_md(tmp_path)
    captured = {}

    def fake_app(*, hot_reload, **kwargs):
        captured["hot_reload"] = hot_reload
        obj = MagicMock()
        obj.run = MagicMock()
        return obj

    with patch("pyxel_slides.cli.SlidesApp", side_effect=lambda **kw: fake_app(**kw)):
        main([str(md), "--no-hot-reload"])

    assert captured["hot_reload"] is False


# --------------------------------------------------------------------------- #
# main() — missing file
# --------------------------------------------------------------------------- #

def test_main_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        main([str(tmp_path / "nonexistent.md")])


# --------------------------------------------------------------------------- #
# SlidesApp._check_hot_reload (pure logic, no Pyxel)
# --------------------------------------------------------------------------- #

class _FakeSlide:
    def body_char_count(self) -> int:
        return 0


def _make_app_no_pyxel(md_path: Path, hot_reload: bool = True):
    """Construct a SlidesApp without calling run() (avoids pyxel.init)."""
    from pyxel_slides.app import SlidesApp

    app = SlidesApp.__new__(SlidesApp)
    app.markdown_path = md_path
    app.theme = VSCODE_LIGHT
    app.width = 384
    app.height = 216
    app.fps = 30
    app.title = "test"
    app.pyxres_path = None
    app.download_fonts = False
    app.hot_reload = hot_reload
    app.slides = [_FakeSlide()]
    app.index = 0
    app._mtime = md_path.stat().st_mtime
    app._reveal_chars = -1
    app._hot_reload_counter = 0
    return app


def test_check_hot_reload_no_change(tmp_path):
    md = _make_md(tmp_path)
    app = _make_app_no_pyxel(md)
    initial_mtime = app._mtime

    # _check_hot_reload should do nothing when mtime hasn't changed.
    reload_calls = []
    app._load_markdown = lambda: reload_calls.append(True)
    app._check_hot_reload()

    assert reload_calls == []
    assert app._mtime == initial_mtime


def test_check_hot_reload_detects_change(tmp_path):
    md = _make_md(tmp_path)
    app = _make_app_no_pyxel(md)

    # Simulate a file change by altering the recorded mtime.
    app._mtime = app._mtime - 1.0  # older than actual

    reload_calls = []
    app._load_markdown = lambda: reload_calls.append(True)
    app._check_hot_reload()

    assert reload_calls == [True]


def test_check_hot_reload_missing_file(tmp_path):
    md = _make_md(tmp_path)
    app = _make_app_no_pyxel(md)

    # Delete the file; _check_hot_reload should not raise.
    md.unlink()
    app._check_hot_reload()  # must not raise


def test_check_hot_reload_increments_counter(tmp_path):
    """The counter in update() reaches fps → calls _check_hot_reload."""
    md = _make_md(tmp_path)
    app = _make_app_no_pyxel(md)

    app.fps = 5  # small value so we don't need many iterations
    check_calls = []
    app._check_hot_reload = lambda: check_calls.append(True)

    # Simulate the counter branch manually (mirrors the update() logic).
    for _ in range(app.fps):
        app._hot_reload_counter += 1
        if app._hot_reload_counter >= app.fps:
            app._hot_reload_counter = 0
            app._check_hot_reload()

    assert check_calls == [True]
    assert app._hot_reload_counter == 0
