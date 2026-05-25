"""Intermediate representation for parsed slides.

Phase 2: TextRun inline styles, typed Paragraph/ListBlock.
Phase 4: ImageBlock for ``![alt](path)`` blocks.
Phase 5: MathBlock for ``$$...$$`` display math; TextRun.math for ``$...$`` inline math.
Phase 7: SpriteBlock for ``pyxel-sprite`` fenced code blocks.
Phase 10: ColumnBreak for two-column slide layout (``|||`` paragraph).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union

from .canvas import Canvas


HeadingLevel = Literal[1, 2, 3, 4, 5, 6]


@dataclass
class TextRun:
    """An atomic piece of inline text with optional style flags."""

    text: str
    bold: bool = False
    italic: bool = False
    highlight: bool = False  # accent-bg rect behind text; parsed in a later phase
    code: bool = False       # inline ``code`` span
    url: str = ""            # non-empty = hyperlink (click handler comes in Phase 6)
    math: bool = False       # inline ``$...$`` math span (expr stored in .text)
    newline: bool = False    # explicit line break (from hardbreak token)

    @property
    def is_plain(self) -> bool:
        return not (self.bold or self.italic or self.highlight or self.code or self.url or self.math)


def plain(text: str) -> List[TextRun]:
    """Wrap a plain string as a single-element TextRun list."""
    return [TextRun(text=text)]


@dataclass
class Heading:
    level: HeadingLevel
    text: str  # Headings always render as plain text
    step: int = 1  # Step number for progressive display


@dataclass
class Paragraph:
    runs: List[TextRun]
    step: int = 1  # Step number for progressive display (1 = first step)

    @property
    def text(self) -> str:
        """Backward-compat: full plain text of all runs."""
        return "".join(r.text for r in self.runs)


@dataclass
class ListBlock:
    items: List[List[TextRun]]  # each list item = a list of TextRun
    ordered: bool = False
    step: int = 1  # Step number for progressive display
    start: int = 1  # Starting number for ordered lists
    depths: List[int] = field(default_factory=list)  # nesting depth of each item (0 = top-level)


@dataclass
class CodeBlock:
    code: str
    language: str = ""
    step: int = 1  # Step number for progressive display


@dataclass
class ImageBlock:
    """A standalone image parsed from ``![alt](path)``."""
    path: str       # path as written in the Markdown source
    alt: str = ""   # alt text
    scale: float = 1.0  # scale factor for resizing (e.g., 0.5 for half size)
    step: int = 1  # Step number for progressive display


@dataclass
class MathBlock:
    """Display-mode math block parsed from ``$$...$$``."""
    expr: str   # raw LaTeX expression (without surrounding dollar signs)
    step: int = 1  # Step number for progressive display


@dataclass
class CanvasBlock:
    """A rendered Canvas object parsed from a ``pyxel-canvas`` or ``pyxel-graph`` fence."""
    canvas: Canvas
    scale: float = 1.0
    align: Literal["left", "center", "right"] = "center"
    step: int = 1  # Step number for progressive display


@dataclass
class TableBlock:
    """A GFM-style pipe table parsed from Markdown."""
    headers: List[str]
    rows: List[List[str]]
    col_widths: Optional[List[int]] = None  # Optional column widths in pixels
    step: int = 1  # Step number for progressive display


@dataclass
class SpriteBlock:
    """A Pyxel image-bank sprite rendered via ``pyxel.blt()``.

    Parsed from a fenced code block whose language tag is ``pyxel-sprite``.
    The block body contains ``key=value`` lines (unrecognised lines are
    silently ignored).

    Example::

        ```pyxel-sprite
        img=0
        u=0
        v=0
        w=16
        h=16
        scale=2
        colkey=0
        frames=4
        frame_w=16
        anim_fps=8
        ```
    """
    img: int = 0         # image bank index (0-2)
    u: int = 0           # source x in bank (pixels)
    v: int = 0           # source y in bank (pixels)
    w: int = 16          # source width  (pixels, before scale)
    h: int = 16          # source height (pixels, before scale)
    scale: float = 1.0   # draw scale factor passed to pyxel.blt()
    colkey: int = -1     # transparent colour index (-1 = no transparency)
    frames: int = 1      # number of animation frames (horizontal strip)
    frame_w: int = -1    # width of one frame (-1 → same as w)
    anim_fps: int = 8    # animation speed (frames per second)


@dataclass
class ColumnBreak:
    """Column-break marker: splits a content slide into two side-by-side columns.

    Parsed from a paragraph whose sole text is ``|||``.
    Blocks before the break render in the left column; blocks after in the right.
    Any leading Heading blocks are drawn full-width above both columns.
    """


Block = Union[Heading, Paragraph, ListBlock, CodeBlock, ImageBlock, MathBlock, CanvasBlock, SpriteBlock, TableBlock, ColumnBreak]


@dataclass
class Slide:
    """A single slide in the presentation."""
    blocks: List[Block]
    step: int = 0  # Current step for progressive display (0 = show all)

    @property
    def two_column(self) -> bool:
        """True if the slide contains a ColumnBreak (two-column layout)."""
        return any(isinstance(b, ColumnBreak) for b in self.blocks)

    @property
    def is_section_title(self) -> bool:
        """A slide whose first non-logo block is an H1 is a section-title slide."""
        for b in self.blocks:
            if isinstance(b, ImageBlock):
                continue
            if isinstance(b, Heading):
                return b.level == 1
            return False
        return False

    @property
    def title(self) -> str | None:
        for b in self.blocks:
            if isinstance(b, Heading):
                return b.text
        return None

    def body_char_count(self) -> int:
        """Count text characters in Paragraph and ListBlock blocks (typewriter budget)."""
        total = 0
        for b in self.blocks:
            if isinstance(b, Paragraph):
                total += sum(len(r.text) for r in b.runs)
            elif isinstance(b, ListBlock):
                for item in b.items:
                    total += sum(len(r.text) for r in item)
        return max(1, total)
