# pyxel-slides

A Markdown-driven retro presentation engine built on [Pyxel](https://github.com/kitao/pyxel).

This repository is following a phased build plan. **Phase 1** (this commit) ships:

- Markdown parser → slide IR (headings, paragraphs, lists, fenced code blocks)
- Game Boy DMG palette (4 shades, 16-slot)
- Section-title slides (`#` centered, large) and page-title slides (`##` top-left, large)
- Slide breaks on `---` only
- Pyxel app with keyboard navigation, slide counter, progress bar, and hot reload

Later phases add: BDF fonts, syntax-highlighted code panels, image dithering,
LaTeX math via `mathtext`, clickable hyperlinks, sprite/animation directives,
multi-column layout, and an overview mode.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run the demo

```bash
pyxel-slides examples/demo.md
```

Optional flags:

```bash
pyxel-slides examples/demo.md --resolution 480x270 --fps 60
pyxel-slides examples/demo.md --pyxres examples/demo.pyxres
```

If a `<deck>.pyxres` file exists next to your `.md`, it's auto-loaded.

## Controls

| Key | Action |
| --- | --- |
| Right / Space / PgDn / Enter | Next slide |
| Left / PgUp / Backspace | Previous slide |
| Home / End | First / last slide |
| R | Reload Markdown from disk |
| Q / Esc | Quit |

## Markdown rules (Phase 1)

| Source | Rendered as |
| --- | --- |
| `---` | Slide break |
| `# Title` (alone on slide) | Section-title slide, centered, very large |
| `## Title` | Page title, top-left, large, with accent underline |
| `### Title` | Subheading |
| Paragraph | Wrapped body text |
| `- item` / `1. item` | Bulleted / numbered list |
| ```` ``` ```` fences | Code block (monochrome panel; syntax highlighting coming in Phase 3) |
| ```` ```pyxel-canvas ```` | Pixel canvas for points, lines, curves, filled areas, and text |
| ```` ```pyxel-graph ```` | Function plot rendered into a canvas |

Inline styling (`**bold**`, `*italic*`, links, images, math) parses but renders
as plain text in Phase 1.

## Canvas and Graph blocks

Use a `pyxel-canvas` fence for small 16-color diagrams:

````markdown
```pyxel-canvas
width=220
height=120
bg=9
border=14
line 10 100 210 20 color=2
curve 20,100 80,10 140,10 200,100 color=4 steps=48
area 40,85 90,45 140,85 fill=12 color=2
text 12 10 "Canvas demo" color=1
```
````

Use a `pyxel-graph` fence to plot math expressions into a canvas. Quote
expressions when they contain spaces.

````markdown
```pyxel-graph
width=260
height=140
x=-6.28,6.28
y=-1.5,1.5
grid=true
plot sin(x) color=2
plot cos(x) color=5
shade_under sin(x) baseline=0 color=12 x=0,3.14
```
````

The same primitives are available from Python:

```python
from pyxel_slides import Canvas, Graph

canvas = Canvas(width=220, height=120, bg=9, border=14)
graph = Graph(canvas, x_min=-5, x_max=5, y_min=-2, y_max=2, grid=True)
graph.plot("x^2 - 1", color=2).draw()
```

## Creating a `.pyxres` sprite sheet for your deck

Pyxel ships a built-in resource editor. Run:

```bash
pyxel edit examples/demo.pyxres
```

That opens the editor and creates the file on save. Once present, it will be
auto-loaded by `pyxel-slides`. Phase 7 will introduce HTML-comment directives
for spawning sprites/animations on specific slides, e.g.:

```html
<!-- pyxel: sprite actor=cat x=200 y=150 anim=walk -->
```

## Resolution

Default is **384×216** (16:9), Pyxel's universally-supported landscape maximum.
Pyxel 2.x builds may accept larger sizes (try `--resolution 480x270` or
`600x338`); pyxel-slides will pass them through unchanged.

## Project layout

```
pyxel_slides/
  __init__.py
  app.py        # Pyxel App: window, input, navigation
  cli.py        # `pyxel-slides` CLI entry point
  ir.py         # Slide / Block dataclasses
  parser.py     # Markdown → IR
  renderer.py   # IR → Pyxel draw calls
  theme.py      # Game Boy palette + theme
examples/
  demo.md
tests/
  test_parser.py
pyproject.toml
```

## License

MIT.
