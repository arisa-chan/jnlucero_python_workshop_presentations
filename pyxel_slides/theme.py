"""Theme + palette definitions.

Phase 1 ships the classic Game Boy DMG 4-shade palette. Pyxel uses a 16-entry
palette; we duplicate the 4 shades across the 16 slots so existing draw calls
never accidentally land on an unset color.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# Game Boy DMG palette (darkest -> lightest)
GB_DARKEST = 0x0F380F
GB_DARK = 0x306230
GB_LIGHT = 0x8BAC0F
GB_LIGHTEST = 0x9BBC0F


# Palette indices (semantic roles)
COL_BG = 0          # screen background (lightest)
COL_FG = 1          # default text (darkest)
COL_ACCENT = 2      # title accent (dark)
COL_MUTED = 3       # secondary / list bullets (light)


@dataclass
class Theme:
    name: str
    palette: List[int]  # 16 RGB ints (0xRRGGBB)
    bg: int = COL_BG
    fg: int = COL_FG
    accent: int = COL_ACCENT
    muted: int = COL_MUTED
    padding: int = 8
    line_spacing: int = 2  # extra px between text lines


def _gameboy_palette() -> List[int]:
    base = [GB_LIGHTEST, GB_DARKEST, GB_DARK, GB_LIGHT]
    # Pad to 16 entries by repeating the 4-color cycle.
    pal = [base[i % 4] for i in range(16)]
    return pal


GAMEBOY = Theme(
    name="gameboy",
    palette=_gameboy_palette(),
    bg=COL_BG,
    fg=COL_FG,
    accent=COL_ACCENT,
    muted=COL_MUTED,
    padding=8,
    line_spacing=2,
)
