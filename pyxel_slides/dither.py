"""Image loading and Floyd-Steinberg dithering to a fixed palette.

Phase 4 feature: Markdown ``![alt](path)`` blocks are loaded with Pillow,
resized to fit the slide content area, and dithered to the GameBoy 4-shade
palette using Floyd-Steinberg error-diffusion.

Falls back gracefully when Pillow is not installed — callers receive ``None``
and should draw a placeholder rectangle instead.

Public API::

    pillow_available() -> bool
    dither_to_palette(path, target_w, target_h, palette_rgb) -> Optional[List[List[int]]]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# GameBoy DMG reference palette in (R, G, B) order.
# The position of each tuple matches the Pyxel palette index used in theme.py:
#   index 0 = COL_BG  (0x9BBC0F lightest)
#   index 1 = COL_FG  (0x0F380F darkest)
#   index 2 = COL_ACCENT (0x306230 dark green)
#   index 3 = COL_MUTED  (0x8BAC0F light green)
# --------------------------------------------------------------------------- #

GAMEBOY_PALETTE: List[Tuple[int, int, int]] = [
    (0x9B, 0xBC, 0x0F),  # 0 — bg / lightest
    (0x0F, 0x38, 0x0F),  # 1 — fg / darkest
    (0x30, 0x62, 0x30),  # 2 — accent / dark green
    (0x8B, 0xAC, 0x0F),  # 3 — muted / light green
]

# --------------------------------------------------------------------------- #
# Pillow availability
# --------------------------------------------------------------------------- #

try:
    from PIL import Image as _PilImage
    _PILLOW = True
except ImportError:
    _PILLOW = False


def pillow_available() -> bool:
    """Return True if Pillow is installed and importable."""
    return _PILLOW


# --------------------------------------------------------------------------- #
# Floyd-Steinberg dithering (pure Python, no numpy required)
# --------------------------------------------------------------------------- #

def _nearest_index(
    r: float, g: float, b: float,
    palette: List[Tuple[int, int, int]],
) -> int:
    """Return the index of the nearest palette colour by squared Euclidean distance."""
    best_idx = 0
    best_dist = float("inf")
    for i, (pr, pg, pb) in enumerate(palette):
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best_dist:
            best_dist = d
            best_idx = i
    return best_idx


def _floyd_steinberg(
    pixels: List[Tuple[int, int, int]],
    width: int,
    height: int,
    palette: List[Tuple[int, int, int]],
) -> List[int]:
    """Apply Floyd-Steinberg dithering and return a flat list of palette indices.

    *pixels* is a flat list of ``(r, g, b)`` tuples in row-major order.
    """
    # Use float channels for accurate error accumulation.
    buf_r = [float(p[0]) for p in pixels]
    buf_g = [float(p[1]) for p in pixels]
    buf_b = [float(p[2]) for p in pixels]
    result: List[int] = [0] * (width * height)

    for y in range(height):
        for x in range(width):
            pos = y * width + x
            old_r = buf_r[pos]
            old_g = buf_g[pos]
            old_b = buf_b[pos]

            idx = _nearest_index(old_r, old_g, old_b, palette)
            result[pos] = idx

            nr, ng, nb = palette[idx]
            err_r = old_r - nr
            err_g = old_g - ng
            err_b = old_b - nb

            # Distribute error to 4 neighbouring pixels.
            def _add(nx: int, ny: int, factor: float) -> None:
                if 0 <= nx < width and 0 <= ny < height:
                    npos = ny * width + nx
                    buf_r[npos] += err_r * factor
                    buf_g[npos] += err_g * factor
                    buf_b[npos] += err_b * factor

            _add(x + 1, y,     7 / 16)
            _add(x - 1, y + 1, 3 / 16)
            _add(x,     y + 1, 5 / 16)
            _add(x + 1, y + 1, 1 / 16)

    return result


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def dither_to_palette(
    path: Any,
    target_w: int,
    target_h: int,
    palette_rgb: Optional[List[Tuple[int, int, int]]] = None,
) -> Optional[List[List[int]]]:
    """Load *path*, resize to (*target_w* × *target_h*), dither to *palette_rgb*.

    *path* may be a :class:`pathlib.Path`, a ``str`` file path, or any
    file-like object accepted by :func:`PIL.Image.open` (e.g. ``io.BytesIO``).

    Returns a 2-D list ``pixels[row][col]`` of palette indices, or ``None`` if
    Pillow is unavailable or the image cannot be opened.

    *palette_rgb* defaults to :data:`GAMEBOY_PALETTE`.  The returned indices
    correspond directly to Pyxel palette slot numbers when the default palette
    is used with the GameBoy theme.
    """
    if not _PILLOW:
        return None

    if palette_rgb is None:
        palette_rgb = GAMEBOY_PALETTE

    try:
        img = _PilImage.open(path).convert("RGB")
    except Exception:  # noqa: BLE001
        return None

    if target_w <= 0 or target_h <= 0:
        return None

    img = img.resize((target_w, target_h), _PilImage.LANCZOS)
    flat_rgb: List[Tuple[int, int, int]] = list(img.getdata())  # type: ignore[arg-type]
    flat_indices = _floyd_steinberg(flat_rgb, target_w, target_h, palette_rgb)
    return [flat_indices[row * target_w: (row + 1) * target_w] for row in range(target_h)]


def fit_dimensions(
    img_w: int,
    img_h: int,
    max_w: int,
    max_h: int,
) -> Tuple[int, int]:
    """Scale (*img_w*, *img_h*) to fit within (*max_w*, *max_h*), keeping aspect ratio.

    Returns ``(target_w, target_h)`` — always at least 1×1.
    """
    if img_w <= 0 or img_h <= 0:
        return max(1, max_w), max(1, max_h)
    scale = min(max_w / img_w, max_h / img_h, 1.0)  # never upscale
    return max(1, int(img_w * scale)), max(1, int(img_h * scale))
