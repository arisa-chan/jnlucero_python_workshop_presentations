"""Font download, caching, and FontSet construction.

Two font families are supported:

  efont-unicode (from shimizukawa/pyxel-slide-pyasia-2026):
    b12.bdf    body / code (12 px, regular)
    b12_b.bdf  inline bold (12 px, bold)
    b12_i.bdf  inline italic (12 px, italic)
    b16_b.bdf  heading H3 (16 px, bold)
    b24_b.bdf  heading H1/H2 (24 px, bold)

  Spleen (BSD-2-Clause, fallback monospaced):
    spleen-5x8   5×8
    spleen-8x16  8×16
    spleen-12x24 12×24
    spleen-16x32 16×32

efont fonts are preferred when available.  Fonts are cached under
~/.cache/pyxel_slides/fonts/ and downloaded once on first use.
Pass --no-fonts to the CLI to skip downloading and use the built-in
Pyxel 4×6 font everywhere.
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

# --------------------------------------------------------------------------- #
# efont-unicode (shimizukawa-style)
# --------------------------------------------------------------------------- #

_EFONT_RAW = (
    "https://raw.githubusercontent.com/shimizukawa/pyxel-slide-pyasia-2026"
    "/main/pyxel-slide/assets"
)

EFONT_URLS: dict[str, str] = {
    "b12":   f"{_EFONT_RAW}/b12.bdf",
    "b12_b": f"{_EFONT_RAW}/b12_b.bdf",
    "b12_i": f"{_EFONT_RAW}/b12_i.bdf",
    "b16_b": f"{_EFONT_RAW}/b16_b.bdf",
    "b24_b": f"{_EFONT_RAW}/b24_b.bdf",
}

# Approximate glyph metrics (height; width is variable — use font.text_width()).
EFONT_METRICS: dict[str, tuple[int, int]] = {
    "b12":   (6, 12),
    "b12_b": (7, 12),
    "b12_i": (6, 12),
    "b16_b": (9, 16),
    "b24_b": (14, 24),
}

# --------------------------------------------------------------------------- #
# Spleen (fallback monospaced)
# --------------------------------------------------------------------------- #

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
    for name, url in EFONT_URLS.items():
        dest = CACHE_DIR / f"{name}.bdf"
        if dest.exists():
            continue
        if not quiet:
            print(f"[pyxel-slides] Downloading font {name}.bdf ...", flush=True)
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as exc:  # noqa: BLE001
            if not quiet:
                print(f"[pyxel-slides] Warning: could not fetch {name}.bdf: {exc}")
            all_ok = False
    return all_ok


def font_path(size: str) -> Optional[Path]:
    """Return the cached path for a Spleen BDF, or None if absent."""
    p = CACHE_DIR / f"spleen-{size}.bdf"
    return p if p.exists() else None


def efont_path(name: str) -> Optional[Path]:
    """Return the cached path for an efont BDF, or None if absent."""
    p = CACHE_DIR / f"{name}.bdf"
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

    body: Any = None        # efont b12 or spleen-8x16
    heading_sm: Any = None  # efont b16_b (H3)
    heading_md: Any = None  # efont b24_b (H2)
    heading_lg: Any = None  # efont b24_b (H1 / section title)
    mono: Any = None        # spleen-5x8 (code blocks)
    bold: Any = None        # efont b12_b
    italic: Any = None      # efont b12_i

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
    bold_w: int = 4
    bold_h: int = 6
    italic_w: int = 4
    italic_h: int = 6

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
        """Load efont (preferred) and Spleen fonts from cache.

        Prefers efont-unicode for all roles; falls back to Spleen when efont
        files are absent.  Must be called AFTER pyxel.init() since pyxel.Font
        requires an active Pyxel context.
        """
        # Lazy import so that non-Pyxel unit tests can still import this module.
        try:
            import pyxel  # noqa: PLC0415
        except ImportError:
            return cls.fallback()

        def _load_efont(name: str) -> Optional[Any]:
            p = efont_path(name)
            if p is None:
                return None
            try:
                return pyxel.Font(str(p))
            except Exception as exc:  # noqa: BLE001
                print(f"[pyxel-slides] Warning: failed to load {p.name}: {exc}")
                return None

        def _load(size: str) -> Optional[Any]:
            p = font_path(size)
            if p is None:
                return None
            try:
                return pyxel.Font(str(p))
            except Exception as exc:  # noqa: BLE001
                print(f"[pyxel-slides] Warning: failed to load {p.name}: {exc}")
                return None

        # efont slots
        ef_b12   = _load_efont("b12")
        ef_b12_b = _load_efont("b12_b")
        ef_b12_i = _load_efont("b12_i")
        ef_b16_b = _load_efont("b16_b")
        ef_b24_b = _load_efont("b24_b")

        # Spleen slots (fallbacks)
        font_5x8   = _load("5x8")
        font_8x16  = _load("8x16")
        font_12x24 = _load("12x24")
        font_16x32 = _load("16x32")

        # Body: prefer efont b12, fall back to spleen-8x16 then spleen-5x8.
        body_font = ef_b12 or font_8x16 or font_5x8
        if ef_b12:
            bw, bh = EFONT_METRICS["b12"]
        elif font_8x16:
            bw, bh = SPLEEN_METRICS["8x16"]
        else:
            bw, bh = (4, 6)

        # heading_sm: prefer efont b16_b, fall back to spleen-8x16.
        sm_font = ef_b16_b or font_8x16
        if ef_b16_b:
            smw, smh = EFONT_METRICS["b16_b"]
        elif font_8x16:
            smw, smh = SPLEEN_METRICS["8x16"]
        else:
            smw, smh = (4, 6)

        # heading_md + heading_lg: prefer efont b24_b, fall back to larger Spleen.
        md_font = ef_b24_b or font_12x24
        if ef_b24_b:
            mdw, mdh = EFONT_METRICS["b24_b"]
        elif font_12x24:
            mdw, mdh = SPLEEN_METRICS["12x24"]
        else:
            mdw, mdh = (4, 6)

        lg_font = ef_b24_b or font_16x32
        if ef_b24_b:
            lgw, lgh = EFONT_METRICS["b24_b"]
        elif font_16x32:
            lgw, lgh = SPLEEN_METRICS["16x32"]
        else:
            lgw, lgh = (4, 6)

        # mono: keep spleen-5x8 for code blocks (compact, monospaced feel).
        mono_font = font_5x8
        mw, mh = SPLEEN_METRICS["5x8"] if font_5x8 else (4, 6)

        # bold / italic: efont only.
        bold_font   = ef_b12_b
        italic_font = ef_b12_i
        bold_w_val,   bold_h_val   = EFONT_METRICS["b12_b"] if ef_b12_b else (bw, bh)
        italic_w_val, italic_h_val = EFONT_METRICS["b12_i"] if ef_b12_i else (bw, bh)

        return cls(
            body=body_font,
            heading_sm=sm_font,
            heading_md=md_font,
            heading_lg=lg_font,
            mono=mono_font,
            bold=bold_font,
            italic=italic_font,
            body_w=bw, body_h=bh,
            heading_sm_w=smw, heading_sm_h=smh,
            heading_md_w=mdw, heading_md_h=mdh,
            heading_lg_w=lgw, heading_lg_h=lgh,
            mono_w=mw, mono_h=mh,
            bold_w=bold_w_val, bold_h=bold_h_val,
            italic_w=italic_w_val, italic_h=italic_h_val,
        )
