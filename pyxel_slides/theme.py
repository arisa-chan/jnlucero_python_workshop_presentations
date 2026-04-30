"""Theme + palette definitions.

Phase 1: Game Boy DMG 4-shade palette (kept for reference).
Phase 5+: VS Code Light theme — 16 distinct colours covering syntax
highlighting, UI chrome, and layout roles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


# --------------------------------------------------------------------------- #
# Shared palette-index constants (same slot numbers in every theme)
# --------------------------------------------------------------------------- #

COL_BG       = 0   # slide background
COL_FG       = 1   # primary body text
COL_ACCENT   = 2   # links, bullets, active UI chrome
COL_MUTED    = 3   # secondary / subdued text
COL_KEYWORD  = 4   # keyword colour (syntax)
COL_STRING   = 5   # string literal colour (syntax)
COL_COMMENT  = 6   # comment colour (syntax)
COL_NUMBER   = 7   # numeric literal colour (syntax)
COL_BUILTIN  = 8   # built-in / type name colour (syntax)
COL_PANEL_BG = 9   # code-block panel background
COL_HEADING  = 10  # H1 / section-title colour
COL_SPECIAL  = 11  # decorators, type annotations (syntax)
COL_HILIGHT  = 12  # ==highlight== pill background
COL_CPILL    = 13  # inline ``code`` pill background
COL_BORDER   = 14  # subtle borders / separators
COL_ALT      = 15  # spare / per-theme use


# --------------------------------------------------------------------------- #
# Theme dataclass
# --------------------------------------------------------------------------- #

@dataclass
class Theme:
    """All colours are Pyxel palette indices (integers 0-15)."""

    name: str
    palette: List[int]       # 16 RGB ints (0xRRGGBB)

    # ---- Basic four roles (required) ------------------------------------
    bg: int = COL_BG         # slide background
    fg: int = COL_FG         # default body text
    accent: int = COL_ACCENT # active elements (headings, links, bullets)
    muted: int = COL_MUTED   # secondary / subdued text

    # ---- Extended syntax roles (-1 → resolved from basic four) ---------
    keyword:     int = -1    # keyword colour     (-1 → accent)
    string_col:  int = -1    # string colour      (-1 → accent)
    comment_col: int = -1    # comment colour     (-1 → muted)
    number_col:  int = -1    # number colour      (-1 → muted)
    builtin_col: int = -1    # built-in colour    (-1 → fg)
    code_fg:     int = -1    # default code text  (-1 → bg)

    # ---- UI decoration roles (-1 → resolved from basic four) -----------
    panel_bg:      int = -1  # code block background  (-1 → fg)
    heading:       int = -1  # H1/section-title       (-1 → fg)
    link:          int = -1  # hyperlink text         (-1 → accent)
    code_pill:     int = -1  # inline code pill bg    (-1 → fg)
    code_pill_fg:  int = -1  # text on code pill      (-1 → bg)
    highlight_bg:  int = -1  # ==highlight== pill bg  (-1 → accent)
    highlight_fg:  int = -1  # text on highlight pill (-1 → bg)

    # ---- Layout ---------------------------------------------------------
    padding:      int = 8
    line_spacing: int = 2

    # ---- Internals ------------------------------------------------------

    def _eff(self, val: int, default: int) -> int:
        return val if val >= 0 else default

    @property
    def eff_keyword(self)     -> int: return self._eff(self.keyword,     self.accent)
    @property
    def eff_string(self)      -> int: return self._eff(self.string_col,  self.accent)
    @property
    def eff_comment(self)     -> int: return self._eff(self.comment_col, self.muted)
    @property
    def eff_number(self)      -> int: return self._eff(self.number_col,  self.muted)
    @property
    def eff_builtin(self)     -> int: return self._eff(self.builtin_col, self.fg)
    @property
    def eff_code_fg(self)     -> int: return self._eff(self.code_fg,     self.bg)
    @property
    def eff_panel_bg(self)    -> int: return self._eff(self.panel_bg,    self.fg)
    @property
    def eff_heading(self)     -> int: return self._eff(self.heading,     self.fg)
    @property
    def eff_link(self)        -> int: return self._eff(self.link,        self.accent)
    @property
    def eff_code_pill(self)   -> int: return self._eff(self.code_pill,   self.fg)
    @property
    def eff_code_pill_fg(self)-> int: return self._eff(self.code_pill_fg,self.bg)
    @property
    def eff_highlight_bg(self)-> int: return self._eff(self.highlight_bg,self.accent)
    @property
    def eff_highlight_fg(self)-> int: return self._eff(self.highlight_fg,self.bg)

    @property
    def palette_as_rgb(self) -> List[Tuple[int, int, int]]:
        """Return the palette as a list of (R, G, B) tuples."""
        return [((c >> 16) & 0xFF, (c >> 8) & 0xFF, c & 0xFF)
                for c in self.palette]


# --------------------------------------------------------------------------- #
# VS Code Light+ theme  (default)
# --------------------------------------------------------------------------- #
#
# Colours sourced from the VS Code "Default Light+" token-colour theme:
#   Background    #FFFFFF   Editor foreground  #1E1E1E
#   Keywords      #0000FF   Strings            #A31515
#   Comments      #008000   Numbers            #098658
#   Types/builtin #267F99   Code panel bg      #F3F3F3
#   VS Code blue  #0078D4   Section-title blue #005FB8
#   Highlight bg  #ADD6FF   Inline code pill   #E8E8E8
#   Border        #C8C8C8   Decorators/special #AF00DB

def _vscode_light_palette() -> List[int]:
    return [
        0xFFFFFF,  #  0  COL_BG       – slide background (white)
        0x1E1E1E,  #  1  COL_FG       – primary text (near-black)
        0x0078D4,  #  2  COL_ACCENT   – VS Code blue (links, bullets, chrome)
        0x6E6E6E,  #  3  COL_MUTED    – medium gray (secondary text)
        0x0000FF,  #  4  COL_KEYWORD  – keyword blue
        0xA31515,  #  5  COL_STRING   – string red
        0x008000,  #  6  COL_COMMENT  – comment green
        0x098658,  #  7  COL_NUMBER   – number teal
        0x267F99,  #  8  COL_BUILTIN  – type/builtin cyan
        0xF3F3F3,  #  9  COL_PANEL_BG – code block background (light gray)
        0x005FB8,  # 10  COL_HEADING  – section title blue (darker)
        0xAF00DB,  # 11  COL_SPECIAL  – decorators / type annotations (purple)
        0xADD6FF,  # 12  COL_HILIGHT  – selection / highlight background
        0xE8E8E8,  # 13  COL_CPILL    – inline code pill background
        0xC8C8C8,  # 14  COL_BORDER   – subtle border / separator
        0x000000,  # 15  COL_ALT      – pure black (spare)
    ]


VSCODE_LIGHT = Theme(
    name="vscode_light",
    palette=_vscode_light_palette(),
    bg=COL_BG,              # 0 – white
    fg=COL_FG,              # 1 – near-black
    accent=COL_ACCENT,      # 2 – VS Code blue
    muted=COL_MUTED,        # 3 – medium gray
    # syntax
    keyword=COL_KEYWORD,    # 4 – keyword blue
    string_col=COL_STRING,  # 5 – string red
    comment_col=COL_COMMENT,# 6 – comment green
    number_col=COL_NUMBER,  # 7 – number teal
    builtin_col=COL_BUILTIN,# 8 – type/builtin cyan
    code_fg=COL_FG,         # 1 – dark text inside code panels
    # UI
    panel_bg=COL_PANEL_BG,  # 9 – light gray panel
    heading=COL_HEADING,    # 10 – darker blue for section titles
    link=COL_ACCENT,        # 2 – same as accent
    code_pill=COL_CPILL,    # 13 – light gray pill
    code_pill_fg=COL_FG,    # 1 – dark text on pill
    highlight_bg=COL_HILIGHT,# 12 – light blue highlight
    highlight_fg=COL_FG,    # 1 – dark text on light highlight
    padding=8,
    line_spacing=2,
)


# --------------------------------------------------------------------------- #
# Classic Game Boy DMG theme  (retained as an alternative)
# --------------------------------------------------------------------------- #

GB_DARKEST  = 0x0F380F
GB_DARK     = 0x306230
GB_LIGHT    = 0x8BAC0F
GB_LIGHTEST = 0x9BBC0F


def _gameboy_palette() -> List[int]:
    base = [GB_LIGHTEST, GB_DARKEST, GB_DARK, GB_LIGHT]
    return [base[i % 4] for i in range(16)]


GAMEBOY = Theme(
    name="gameboy",
    palette=_gameboy_palette(),
    bg=0,   # 0x9BBC0F – lightest green
    fg=1,   # 0x0F380F – darkest green
    accent=2,  # 0x306230 – dark green
    muted=3,   # 0x8BAC0F – light green
    # syntax (preserve original role_to_color semantics)
    keyword=3,      # muted (light green)
    string_col=2,   # accent (dark green)
    comment_col=2,  # accent (dark green)
    number_col=3,   # muted (light green)
    builtin_col=0,  # bg (lightest, light text on dark panel)
    code_fg=0,      # bg (lightest)
    # UI
    panel_bg=1,     # fg (darkest green panel)
    heading=1,      # fg (darkest)
    link=2,         # accent
    code_pill=1,    # fg (dark pill)
    code_pill_fg=0, # bg (light text on dark pill)
    highlight_bg=2, # accent
    highlight_fg=0, # bg (light text on highlight)
    padding=8,
    line_spacing=2,
)

