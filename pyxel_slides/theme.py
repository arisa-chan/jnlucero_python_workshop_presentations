"""Theme + palette definitions.

Phase 1: Game Boy DMG 4-shade palette (kept for reference).
Phase 5+: VS Code Light theme — 16 distinct colours covering syntax
highlighting, UI chrome, and layout roles.
Phase 9+: Gradient theme — inspired by the "Rising Along the Gradient"
event poster: deep purple background, lavender text, violet/pink/gold accents.
Phase 10+: Arcade Space theme — inspired by the Python Workshop O-Day poster:
starfield navy, chunky black outlines, rocket blues, and hot yellow/orange type.
Phase 12+: ASEP Structural theme — matched to the ASEP presentation template:
deep navy (#3C3E95), periwinkle/lavender (#8A8BBF / #B1B2D5), pale slide
background (#DFE0EA), and warm gold (#B38B3E / #EEBD54).
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

    # ---- Decorative motif (title & section-header slides) ---------------
    motif: str = "none"                     # "none" | "masonry"
    motif_blocks: List[Tuple[float, float, float, float, int]] = field(default_factory=list)
    # Each block: (x_frac, bottom_frac, w_frac, h_frac, colour_index).
    # x/w are fractions of slide width; bottom/h are fractions of slide
    # height with the block's bottom edge anchored bottom_frac above the
    # slide's bottom edge.  Only consulted when motif != "none".

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
# Gradient theme  ("Rising Along the Gradient" event palette)
# --------------------------------------------------------------------------- #
#
# Colours sampled from the event poster:
#   Background    #12082A   Primary text       #DCC8F8
#   Accent violet #B44FE8   Muted purple       #7868A8
#   Hot pink      #F030A8   Coral orange       #FF8050
#   Blue-purple   #6858B0   Golden yellow      #FFB830
#   Orchid        #D068E0   Dark panel         #220E40
#   Warm gold     #FFD070   Vivid violet       #CC44FF
#   Highlight bg  #5030B8   Code pill bg       #2A1850
#   Border        #503FC8   Near-white cream   #FFF0E0

def _gradient_palette() -> List[int]:
    return [
        0x12082A,  #  0  COL_BG       – deep dark purple (background)
        0xDCC8F8,  #  1  COL_FG       – light lavender (primary text)
        0xB44FE8,  #  2  COL_ACCENT   – bright violet (links, bullets, chrome)
        0x7868A8,  #  3  COL_MUTED    – muted purple (secondary text)
        0xF030A8,  #  4  COL_KEYWORD  – hot pink / magenta
        0xFF8050,  #  5  COL_STRING   – coral orange
        0x6858B0,  #  6  COL_COMMENT  – blue-purple (comments)
        0xFFB830,  #  7  COL_NUMBER   – golden yellow
        0xD068E0,  #  8  COL_BUILTIN  – orchid / pink-purple
        0x220E40,  #  9  COL_PANEL_BG – darker purple panel
        0xFFD070,  # 10  COL_HEADING  – warm gold (section titles)
        0xCC44FF,  # 11  COL_SPECIAL  – vivid violet (decorators)
        0x5030B8,  # 12  COL_HILIGHT  – deep blue-purple (highlight pill bg)
        0x2A1850,  # 13  COL_CPILL    – dark purple (inline code pill bg)
        0x503FC8,  # 14  COL_BORDER   – medium purple-blue (borders)
        0xFFF0E0,  # 15  COL_ALT      – near-white cream
    ]


GRADIENT = Theme(
    name="gradient",
    palette=_gradient_palette(),
    bg=COL_BG,              # 0 – deep dark purple
    fg=COL_FG,              # 1 – light lavender
    accent=COL_ACCENT,      # 2 – bright violet
    muted=COL_MUTED,        # 3 – muted purple
    # syntax
    keyword=COL_KEYWORD,    # 4 – hot pink
    string_col=COL_STRING,  # 5 – coral orange
    comment_col=COL_COMMENT,# 6 – blue-purple
    number_col=COL_NUMBER,  # 7 – golden yellow
    builtin_col=COL_BUILTIN,# 8 – orchid
    code_fg=COL_FG,         # 1 – lavender text inside code panels
    # UI
    panel_bg=COL_PANEL_BG,  # 9  – darker purple panel
    heading=COL_HEADING,    # 10 – warm gold for section titles
    link=COL_ACCENT,        # 2  – bright violet links
    code_pill=COL_CPILL,    # 13 – dark purple pill
    code_pill_fg=COL_FG,    # 1  – lavender text on dark pill
    highlight_bg=COL_HILIGHT,# 12 – deep blue-purple highlight
    highlight_fg=COL_FG,    # 1  – lavender text on highlight
    padding=8,
    line_spacing=2,
)


# --------------------------------------------------------------------------- #
# Arcade Space theme  (Python Workshop O-Day poster palette)
# --------------------------------------------------------------------------- #
#
# Colours sampled by eye from the supplied retro workshop poster:
#   Background    #0B1A33   Primary text       #FFF4D6
#   Arcade yellow #FFE34A   Muted blue         #6F91B8
#   Red-orange    #FF3D13   Solar orange       #FF9F2A
#   Pixel green   #50B83C   Sky blue           #5BA9E8
#   Rocket cyan   #8BD4D9   Black panel        #05070D
#   Title yellow  #FFF069   Deep red           #D32922
#   Highlight bg  #245A9A   Code pill bg       #102142
#   Outline black #000000   Star white         #FFFFFF

def _arcade_space_palette() -> List[int]:
    return [
        0x0B1A33,  #  0  COL_BG       – deep starfield navy
        0xFFF4D6,  #  1  COL_FG       – warm off-white text
        0xFFE34A,  #  2  COL_ACCENT   – arcade yellow chrome
        0x6F91B8,  #  3  COL_MUTED    – muted distant-blue secondary text
        0xFF3D13,  #  4  COL_KEYWORD  – hot red-orange title stripe
        0xFF9F2A,  #  5  COL_STRING   – solar orange planet tone
        0x50B83C,  #  6  COL_COMMENT  – pixel green accent
        0x5BA9E8,  #  7  COL_NUMBER   – bright earth/space blue
        0x8BD4D9,  #  8  COL_BUILTIN  – rocket glass cyan
        0x05070D,  #  9  COL_PANEL_BG – chunky black code panel
        0xFFF069,  # 10  COL_HEADING  – bright poster-title yellow
        0xD32922,  # 11  COL_SPECIAL  – deep comic red
        0x245A9A,  # 12  COL_HILIGHT  – saturated blue highlight bg
        0x102142,  # 13  COL_CPILL    – dark blue inline-code pill
        0x000000,  # 14  COL_BORDER   – heavy pixel-art outline black
        0xFFFFFF,  # 15  COL_ALT      – star white / high contrast
    ]


ARCADE_SPACE = Theme(
    name="arcade_space",
    palette=_arcade_space_palette(),
    bg=COL_BG,              # 0  – deep starfield navy
    fg=COL_FG,              # 1  – warm off-white
    accent=COL_ACCENT,      # 2  – arcade yellow
    muted=COL_MUTED,        # 3  – muted distant-blue
    # syntax
    keyword=COL_KEYWORD,    # 4  – red-orange keywords
    string_col=COL_STRING,  # 5  – solar orange strings
    comment_col=COL_COMMENT,# 6  – pixel green comments
    number_col=COL_NUMBER,  # 7  – bright blue numbers
    builtin_col=COL_BUILTIN,# 8  – rocket cyan builtins
    code_fg=COL_FG,         # 1  – warm off-white code text
    # UI
    panel_bg=COL_PANEL_BG,  # 9  – black arcade panel
    heading=COL_HEADING,    # 10 – poster-title yellow headings
    link=COL_NUMBER,        # 7  – bright blue links
    code_pill=COL_CPILL,    # 13 – dark blue code pill
    code_pill_fg=COL_FG,    # 1  – off-white text on pill
    highlight_bg=COL_HILIGHT,# 12 – saturated blue highlight
    highlight_fg=COL_ALT,   # 15 – star-white highlight text
    padding=8,
    line_spacing=2,
)


# --------------------------------------------------------------------------- #
# ASEP Structural theme  (ASEP presentation template palette)
# --------------------------------------------------------------------------- #
#
# Colours are taken from the template's embedded brand-guide slide and slide
# XML. The formal palette is:
#   Navy          #3C3E95   Periwinkle      #8A8BBF
#   Lavender      #B1B2D5   Pale background #DFE0EA
#   Dark gold     #B38B3E   Gold            #EEBD54
# Additional slide colors used by the template:
#   Subtitle gray #7D7F76   Deep title blue #002060 / #2B2F84
#   Off-white     #F5F5F5   Section white   #F2F3F9

def _asep_palette() -> List[int]:
    return [
        0xDFE0EA,  #  0  COL_BG       – pale lavender slide background
        0x3C3E95,  #  1  COL_FG       – deep navy primary text
        0x3C3E95,  #  2  COL_ACCENT   – deep navy accents / bullets
        0x8A8BBF,  #  3  COL_MUTED    – periwinkle motif / secondary accent
        0xB38B3E,  #  4  COL_KEYWORD  – dark gold
        0xB1B2D5,  #  5  COL_STRING   – lavender
        0x7D7F76,  #  6  COL_COMMENT  – template subtitle gray
        0xEEBD54,  #  7  COL_NUMBER   – template gold
        0x002060,  #  8  COL_BUILTIN  – deep title blue used on photo slides
        0xFFFFFF,  #  9  COL_PANEL_BG – white panels
        0x3C3E95,  # 10  COL_HEADING  – deep navy headings
        0x2B2F84,  # 11  COL_SPECIAL  – alternate title navy from template XML
        0xEEBD54,  # 12  COL_HILIGHT  – gold highlight / divider
        0xF5F5F5,  # 13  COL_CPILL    – off-white text/pill fill
        0xB1B2D5,  # 14  COL_BORDER   – lavender borders / rules
        0xF2F3F9,  # 15  COL_ALT      – section-title off-white
    ]


ASEP_STRUCTURAL = Theme(
    name="asep_structural",
    palette=_asep_palette(),
    bg=COL_BG,              # 0  – pale lavender background
    fg=COL_FG,              # 1  – deep navy
    accent=COL_ACCENT,      # 2  – deep navy
    muted=COL_MUTED,        # 3  – periwinkle
    # syntax (rendered on white panels in this presentation template)
    keyword=COL_KEYWORD,    # 4  – dark gold keywords
    string_col=COL_STRING,  # 5  – lavender strings
    comment_col=COL_COMMENT,# 6  – subtitle gray comments
    number_col=COL_NUMBER,  # 7  – gold numbers
    builtin_col=COL_BUILTIN,# 8  – deep title blue builtins
    code_fg=COL_FG,         # 1  – navy code text on white panels
    # UI
    panel_bg=COL_PANEL_BG,  # 9  – white panels
    heading=COL_HEADING,    # 10 – deep navy headings
    link=COL_ACCENT,        # 2  – deep navy links
    code_pill=COL_CPILL,    # 13 – off-white inline-code pill
    code_pill_fg=COL_FG,    # 1  – navy text on pill
    highlight_bg=COL_HILIGHT,# 12 – gold highlight
    highlight_fg=COL_FG,    # 1  – navy text on gold
    padding=13,
    line_spacing=2,
    # Rectangular fallback motif. The renderer uses the template's extracted
    # bitmap motifs for the full ASEP layout, while this keeps the generic
    # motif helper useful in tests and non-asset environments.
    motif="masonry",
    motif_blocks=[
        (0.75, 0.02, 0.15, 0.28, COL_ACCENT),
        (0.64, 0.02, 0.13, 0.18, COL_MUTED),
        (0.91, 0.18, 0.05, 0.11, COL_BORDER),
        (0.66, 0.21, 0.03, 0.05, COL_SPECIAL),
        (0.90, 0.02, 0.05, 0.12, COL_HILIGHT),
    ],
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
