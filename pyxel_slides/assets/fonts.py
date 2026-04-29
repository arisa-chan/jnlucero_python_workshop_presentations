"""Spleen BDF font download, caching, and FontSet construction.

Spleen (BSD-2-Clause) is a clean monospaced bitmap pixel font at four sizes:
  spleen-5x8   body text      (5px wide, 8px tall per glyph)
  spleen-8x16  small heading  (8x16)
  spleen-12x24 medium heading (12x24)
  spleen-16x32 large heading  (16x32)

Fonts are cached under ~/.cache/pyxel_slides/fonts/ and downloaded once on
first use. Pass --no-fonts to the CLI to skip downloading and use the built-in
Pyxel 4x6 font everywhere (pixel-doubling for headings, as in Phase 1).
"""

from __future__ import annotations

import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# --------------------------------------------------------------------------- #
# Cache location
# --------------------------------------------------------------------------- #

CACHE_DIR = Path.home() / ".cache" / "pyxel_slides" / "fonts"

_SPLEEN_RAW = "https://raw.githubusercontent.com/fcambus/spleen/master"

SPLEEN_URLS: dict[str, str] = {
    "5x8":   f"{_SPLEEN_RAW}/spleen-5x8.bdf",
    "8x16":  f"{_SPLEEN_RAW}/spleen-8x16.bdf",
    "12x24": f"{_SPLEEN_RAW}/spleen-12x24.bdf",
    "16x32": f"{_SPLEEN_RAW}/spleen-16x32.bdf",
}

# Glyph metrics (width, height) for each Spleen size.
SPLEEN_METRICS: dict[str, tuple[int, int]] = {
    "5x8":   (5, 8),
    "8x16":  (8, 16),
    "12x24": (12, 24),
    "16x32": (16, 32),
}

# --------------------------------------------------------------------------- #
# Downloading
# --------------------------------------------------------------------------- #

def ensure_fonts(quiet: bool = False) -> bool:
    """Download missing Spleen BDF files into the cache dir.

    Returns True if all four fonts are now present.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    all_ok = True
    for size, url in SPLEEN_URLS.items():
        dest = CACHE_DIR / f"spleen-{size}.bdf"
        if dest.exists():
            continue
        if not quiet:
            print(f"[pyxel-slides] Downloading font spleen-{size}.bdf ...", flush=True)
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:  # noqa: BLE001
            if not quiet:
                print(f"[pyxel-slides] Warning: could not fetch spleen-{size}.bdf: {exc}")
            all_ok = False
    return all_ok


def font_path(size: str) -> Optional[Path]:
    """Return the cached path for a Spleen BDF, or None if absent."""
    p = CACHE_DIR / f"spleen-{size}.bdf"
    return p if p.exists() else None


# --------------------------------------------------------------------------- #
# FontSet dataclass
# --------------------------------------------------------------------------- #

@dataclass
class FontSet:
    """Holds optional pyxel.Font objects for each text role.

    All fields default to None, meaning fall back to the built-in 4x6 font
    (with pixel-doubling for larger sizes).
    """

    body: Any = None        # spleen-5x8 or None
    heading_sm: Any = None  # spleen-8x16  (H3)
    heading_md: Any = None  # spleen-12x24 (H2)
    heading_lg: Any = None  # spleen-16x32 (H1 / section title)
    mono: Any = None        # spleen-5x8   (code blocks)

    body_w: int = 4
    body_h: int = 6
    heading_sm_w: int = 4
    heading_sm_h: int = 6
    heading_md_w: int = 4
    heading_md_h: int = 6
    heading_lg_w: int = 4
    heading_lg_h: int = 6
    mono_w: int = 4
    mono_h: int = 6

    def text_width(self, s: str, role: str = "body") -> int:
        """Pixel width of string s for the given font role."""
        font = getattr(self, role, None)
        if font is not None:
            return font.text_width(s)
        w = getattr(self, f"{role}_w", self.body_w)
        return len(s) * w

    @classmethod
    def fallback(cls) -> "FontSet":
        """Pure fallback: everything uses Pyxel's built-in 4x6 font."""
        return cls()

    @classmethod
    def from_cache(cls) -> "FontSet":
        """Try to load all four Spleen BDFs. Falls back per-slot if missing.

        Must be called AFTER pyxel.init() since pyxel.Font requires an active
        Pyxel context.
        """
        # Lazy import so that non-Pyxel unit tests can still import this module.
        try:
            import pyxel  # noqa: PLC0415
        except ImportError:
            return cls.fallback()

        def _load(size: str) -> Optional[Any]:
            p = font_path(size)
            if p is None:
                return None
            try:
                return pyxel.Font(str(p))
            except Exception as exc:  # noqa: BLE001
                print(f"[pyxel-slides] Warning: failed to load {p.name}: {exc}")
                return None

        font_5x8  = _load("5x8")
        font_8x16 = _load("8x16")
        font_12x24 = _load("12x24")
        font_16x32 = _load("16x32")

        bw, bh = (5, 8) if font_5x8 else (4, 6)
        smw, smh = (8, 16) if font_8x16 else (4, 6)
        mdw, mdh = (12, 24) if font_12x24 else (4, 6)
        lgw, lgh = (16, 32) if font_16x32 else (4, 6)

        return cls(
            body=font_5x8,
            heading_sm=font_8x16,
            heading_md=font_12x24,
            heading_lg=font_16x32,
            mono=font_5x8,
            body_w=bw, body_h=bh,
            heading_sm_w=smw, heading_sm_h=smh,
            heading_md_w=mdw, heading_md_h=mdh,
            heading_lg_w=lgw, heading_lg_h=lgh,
            mono_w=bw, mono_h=bh,
        )
