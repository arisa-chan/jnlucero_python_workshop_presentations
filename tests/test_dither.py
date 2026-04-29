"""Unit tests for pyxel_slides.dither and the ImageBlock parser path."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pytest

from pyxel_slides.dither import (
    GAMEBOY_PALETTE,
    _floyd_steinberg,
    _nearest_index,
    dither_to_palette,
    fit_dimensions,
    pillow_available,
)
from pyxel_slides.ir import ImageBlock, Paragraph
from pyxel_slides.parser import parse_markdown


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _make_png_bytes(width: int, height: int, color=(128, 128, 128)) -> bytes:
    """Create a minimal solid-colour PNG in memory using Pillow."""
    if not pillow_available():
        pytest.skip("Pillow not installed")
    from PIL import Image  # noqa: PLC0415
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# _nearest_index
# --------------------------------------------------------------------------- #

def test_nearest_index_exact_match():
    pal = GAMEBOY_PALETTE
    for i, (r, g, b) in enumerate(pal):
        assert _nearest_index(r, g, b, pal) == i


def test_nearest_index_midpoint():
    pal = [(0, 0, 0), (255, 255, 255)]
    # Pure black → index 0
    assert _nearest_index(0, 0, 0, pal) == 0
    # Pure white → index 1
    assert _nearest_index(255, 255, 255, pal) == 1
    # Mid-grey → either (no strict requirement, just check range)
    result = _nearest_index(128, 128, 128, pal)
    assert result in (0, 1)


# --------------------------------------------------------------------------- #
# _floyd_steinberg
# --------------------------------------------------------------------------- #

def test_floyd_steinberg_pure_black():
    """Image of all black pixels → index of darkest palette entry."""
    pal = [(0, 0, 0), (255, 255, 255)]
    pixels = [(0, 0, 0)] * 4
    result = _floyd_steinberg(pixels, 2, 2, pal)
    assert all(v == 0 for v in result)


def test_floyd_steinberg_pure_white():
    pal = [(0, 0, 0), (255, 255, 255)]
    pixels = [(255, 255, 255)] * 4
    result = _floyd_steinberg(pixels, 2, 2, pal)
    assert all(v == 1 for v in result)


def test_floyd_steinberg_output_length():
    pal = GAMEBOY_PALETTE
    w, h = 8, 6
    pixels = [(128, 100, 10)] * (w * h)
    result = _floyd_steinberg(pixels, w, h, pal)
    assert len(result) == w * h


def test_floyd_steinberg_indices_in_range():
    pal = GAMEBOY_PALETTE
    w, h = 16, 16
    import random
    rng = random.Random(42)
    pixels = [(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255)) for _ in range(w * h)]
    result = _floyd_steinberg(pixels, w, h, pal)
    assert all(0 <= v < len(pal) for v in result), "Out-of-range palette index"


# --------------------------------------------------------------------------- #
# fit_dimensions
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("iw,ih,mw,mh,ew,eh", [
    (100, 100, 50, 50, 50, 50),    # square, scale down
    (200, 100, 50, 50, 50, 25),    # wide, limited by width
    (100, 200, 50, 50, 25, 50),    # tall, limited by height
    (10,  10,  50, 50, 10, 10),    # small image: no upscale
    (0,   0,   50, 50, 50, 50),    # degenerate input
])
def test_fit_dimensions(iw, ih, mw, mh, ew, eh):
    tw, th = fit_dimensions(iw, ih, mw, mh)
    assert tw == ew and th == eh, f"got ({tw},{th}), expected ({ew},{eh})"


# --------------------------------------------------------------------------- #
# dither_to_palette
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not pillow_available(), reason="Pillow not installed")
def test_dither_to_palette_shape():
    png = _make_png_bytes(16, 12)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png)
        path = Path(f.name)

    result = dither_to_palette(path, 16, 12)
    assert result is not None
    assert len(result) == 12
    assert all(len(row) == 16 for row in result)


@pytest.mark.skipif(not pillow_available(), reason="Pillow not installed")
def test_dither_to_palette_indices_valid():
    png = _make_png_bytes(8, 8, color=(100, 150, 30))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png)
        path = Path(f.name)

    result = dither_to_palette(path, 8, 8)
    assert result is not None
    for row in result:
        for idx in row:
            assert 0 <= idx < len(GAMEBOY_PALETTE), f"index {idx} out of range"


@pytest.mark.skipif(not pillow_available(), reason="Pillow not installed")
def test_dither_to_palette_missing_file():
    result = dither_to_palette(Path("/nonexistent/does_not_exist.png"), 8, 8)
    assert result is None


def test_dither_to_palette_no_pillow_returns_none(monkeypatch):
    import pyxel_slides.dither as _d
    monkeypatch.setattr(_d, "_PILLOW", False)
    result = _d.dither_to_palette(Path("any.png"), 4, 4)
    assert result is None


# --------------------------------------------------------------------------- #
# Parser: ImageBlock detection
# --------------------------------------------------------------------------- #

def test_image_only_paragraph_becomes_imageblock():
    md = "## Slide\n\n![a cat](images/cat.png)\n"
    slides = parse_markdown(md)
    blocks = slides[0].blocks
    # Second block should be an ImageBlock, not a Paragraph.
    img_blocks = [b for b in blocks if isinstance(b, ImageBlock)]
    assert len(img_blocks) == 1
    assert img_blocks[0].path == "images/cat.png"
    assert img_blocks[0].alt == "a cat"


def test_image_path_and_alt_preserved():
    md = "![logo](./assets/logo.png)\n"
    slides = parse_markdown(md)
    ib = slides[0].blocks[0]
    assert isinstance(ib, ImageBlock)
    assert ib.path == "./assets/logo.png"
    assert ib.alt == "logo"


def test_image_in_mixed_paragraph_becomes_paragraph():
    """![img](x.png) inline with text → Paragraph with alt as TextRun."""
    md = "Look at this: ![cool](cool.png) image.\n"
    slides = parse_markdown(md)
    block = slides[0].blocks[0]
    assert isinstance(block, Paragraph)
    full_text = block.text
    assert "cool" in full_text


def test_multiple_images_on_separate_lines():
    md = "![first](a.png)\n\n![second](b.png)\n"
    slides = parse_markdown(md)
    img_blocks = [b for b in slides[0].blocks if isinstance(b, ImageBlock)]
    assert len(img_blocks) == 2
    assert img_blocks[0].path == "a.png"
    assert img_blocks[1].path == "b.png"


def test_image_alt_empty():
    md = "![](no_alt.png)\n"
    slides = parse_markdown(md)
    ib = slides[0].blocks[0]
    assert isinstance(ib, ImageBlock)
    assert ib.alt == ""
    assert ib.path == "no_alt.png"
