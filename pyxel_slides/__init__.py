"""pyxel-slides: a Markdown-driven retro presentation engine on top of Pyxel."""

from .ir import Block, CodeBlock, ColumnBreak, Heading, ImageBlock, ListBlock, MathBlock, Paragraph, Slide, SpriteBlock, TextRun, plain
from .parser import parse_markdown
from .theme import Theme, GAMEBOY, VSCODE_LIGHT, GRADIENT
from .app import SlidesApp
from .assets.fonts import FontSet, ensure_fonts
from .highlight import tokenize_lines, role_to_color, pygments_available
from .dither import dither_to_palette, fit_dimensions, pillow_available
from .mathtext import render_math, matplotlib_available

__all__ = [
    "Slide",
    "Block",
    "Heading",
    "Paragraph",
    "ListBlock",
    "CodeBlock",
    "ImageBlock",
    "MathBlock",
    "SpriteBlock",
    "ColumnBreak",
    "TextRun",
    "plain",
    "parse_markdown",
    "Theme",
    "GAMEBOY",
    "VSCODE_LIGHT",
    "GRADIENT",
    "SlidesApp",
    "SlideRenderer",
    "draw_run_line",
    "_hit_test",
    "FontSet",
    "ensure_fonts",
    "tokenize_lines",
    "role_to_color",
    "pygments_available",
    "dither_to_palette",
    "fit_dimensions",
    "pillow_available",
    "render_math",
    "matplotlib_available",
]

__version__ = "0.9.0"
