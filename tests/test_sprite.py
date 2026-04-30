"""Unit tests for Phase 7 sprite block support.

Covers:
  * SpriteBlock IR defaults and field types.
  * _parse_sprite_block — pure key=value parsing logic.
  * parse_markdown — pyxel-sprite fence becomes SpriteBlock, not CodeBlock.
  * Animation-frame index arithmetic (period / frame_idx).
"""

from __future__ import annotations

import pytest

from pyxel_slides.ir import CodeBlock, SpriteBlock
from pyxel_slides.parser import _parse_sprite_block, parse_markdown


# --------------------------------------------------------------------------- #
# SpriteBlock IR defaults
# --------------------------------------------------------------------------- #

def test_sprite_block_defaults():
    sb = SpriteBlock()
    assert sb.img == 0
    assert sb.u == 0
    assert sb.v == 0
    assert sb.w == 16
    assert sb.h == 16
    assert sb.scale == 1.0
    assert sb.colkey == -1   # -1 = no transparency
    assert sb.frames == 1
    assert sb.frame_w == -1  # -1 = same as w
    assert sb.anim_fps == 8


def test_sprite_block_custom_fields():
    sb = SpriteBlock(img=1, u=32, v=16, w=24, h=24, scale=2.0, colkey=0,
                     frames=4, frame_w=24, anim_fps=12)
    assert sb.img == 1
    assert sb.u == 32
    assert sb.v == 16
    assert sb.w == 24
    assert sb.h == 24
    assert sb.scale == 2.0
    assert sb.colkey == 0
    assert sb.frames == 4
    assert sb.frame_w == 24
    assert sb.anim_fps == 12


# --------------------------------------------------------------------------- #
# _parse_sprite_block — key=value parsing
# --------------------------------------------------------------------------- #

def test_parse_sprite_block_empty_gives_defaults():
    sb = _parse_sprite_block("")
    assert sb == SpriteBlock()


def test_parse_sprite_block_basic_fields():
    content = "img=1\nu=8\nv=16\nw=32\nh=32"
    sb = _parse_sprite_block(content)
    assert sb.img == 1
    assert sb.u == 8
    assert sb.v == 16
    assert sb.w == 32
    assert sb.h == 32


def test_parse_sprite_block_scale_as_float():
    sb = _parse_sprite_block("scale=2.5")
    assert sb.scale == 2.5


def test_parse_sprite_block_scale_integer_string():
    sb = _parse_sprite_block("scale=3")
    assert sb.scale == 3.0


def test_parse_sprite_block_colkey():
    sb = _parse_sprite_block("colkey=0")
    assert sb.colkey == 0


def test_parse_sprite_block_animation_fields():
    sb = _parse_sprite_block("frames=4\nframe_w=16\nanim_fps=12")
    assert sb.frames == 4
    assert sb.frame_w == 16
    assert sb.anim_fps == 12


def test_parse_sprite_block_ignores_unknown_keys():
    # Should not raise; unknown keys silently dropped.
    sb = _parse_sprite_block("foo=bar\nalpha=99\nw=8")
    assert sb.w == 8


def test_parse_sprite_block_ignores_bad_int_values():
    # "hello" can't be int; falls back to default w=16.
    sb = _parse_sprite_block("w=hello")
    assert sb.w == 16


def test_parse_sprite_block_ignores_comment_lines():
    content = "# this is a comment\nw=8\n# another comment"
    sb = _parse_sprite_block(content)
    assert sb.w == 8


def test_parse_sprite_block_ignores_lines_without_equals():
    sb = _parse_sprite_block("just a sentence\nw=8")
    assert sb.w == 8


def test_parse_sprite_block_strips_whitespace():
    sb = _parse_sprite_block("  img = 2  \n  w = 24  ")
    assert sb.img == 2
    assert sb.w == 24


def test_parse_sprite_block_all_int_fields():
    content = (
        "img=2\nu=16\nv=32\nw=24\nh=24\n"
        "colkey=3\nframes=8\nframe_w=24\nanim_fps=6"
    )
    sb = _parse_sprite_block(content)
    assert sb == SpriteBlock(
        img=2, u=16, v=32, w=24, h=24,
        colkey=3, frames=8, frame_w=24, anim_fps=6,
    )


# --------------------------------------------------------------------------- #
# parse_markdown — integration: pyxel-sprite fence → SpriteBlock
# --------------------------------------------------------------------------- #

_SPRITE_SLIDE = """\
# Sprite Demo

```pyxel-sprite
img=0
u=0
v=0
w=16
h=16
scale=2
```
"""

def test_parse_markdown_sprite_fence_produces_sprite_block():
    slides = parse_markdown(_SPRITE_SLIDE)
    assert len(slides) == 1
    blocks = slides[0].blocks
    sprite_blocks = [b for b in blocks if isinstance(b, SpriteBlock)]
    assert len(sprite_blocks) == 1


def test_parse_markdown_sprite_block_fields():
    slides = parse_markdown(_SPRITE_SLIDE)
    sb = next(b for b in slides[0].blocks if isinstance(b, SpriteBlock))
    assert sb.img == 0
    assert sb.w == 16
    assert sb.h == 16
    assert sb.scale == 2.0


def test_parse_markdown_sprite_fence_not_code_block():
    slides = parse_markdown(_SPRITE_SLIDE)
    code_blocks = [b for b in slides[0].blocks if isinstance(b, CodeBlock)]
    assert code_blocks == []


def test_parse_markdown_regular_fence_still_code_block():
    src = "# Code\n\n```python\nprint('hi')\n```\n"
    slides = parse_markdown(src)
    code_blocks = [b for b in slides[0].blocks if isinstance(b, CodeBlock)]
    assert len(code_blocks) == 1
    assert code_blocks[0].language == "python"


def test_parse_markdown_sprite_alongside_other_blocks():
    src = """\
# Mixed Slide

Some introductory text.

```pyxel-sprite
w=32
h=32
```

A paragraph after the sprite.
"""
    slides = parse_markdown(src)
    assert len(slides) == 1
    types = [type(b).__name__ for b in slides[0].blocks]
    assert "SpriteBlock" in types
    assert "Paragraph" in types


# --------------------------------------------------------------------------- #
# Animation frame arithmetic (no Pyxel dependency)
# --------------------------------------------------------------------------- #

def _frame_idx(frame_count: int, anim_fps: int, frames: int) -> int:
    """Mirror of the arithmetic used in SlideRenderer._draw_spriteblock."""
    period = max(1, 30 // max(1, anim_fps))
    return (frame_count // period) % max(1, frames)


def test_animation_single_frame_always_zero():
    for fc in range(120):
        assert _frame_idx(fc, anim_fps=8, frames=1) == 0


def test_animation_cycles_through_all_frames():
    frames = 4
    anim_fps = 10
    period = max(1, 30 // anim_fps)  # = 3
    seen = set()
    for fc in range(period * frames * 2):
        seen.add(_frame_idx(fc, anim_fps, frames))
    assert seen == {0, 1, 2, 3}


def test_animation_period_is_at_least_one():
    # anim_fps=60 would give 30//60=0; clamped to 1.
    assert _frame_idx(0, anim_fps=60, frames=2) == 0
    assert _frame_idx(1, anim_fps=60, frames=2) == 1


def test_animation_frame_idx_in_range():
    frames = 6
    for fc in range(300):
        idx = _frame_idx(fc, anim_fps=8, frames=frames)
        assert 0 <= idx < frames
