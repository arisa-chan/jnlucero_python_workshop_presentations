# pyxel-slides

A Markdown-driven retro presentation engine built on [Pyxel](https://github.com/kitao/pyxel).

`pyxel-slides` turns a Markdown deck into a pixel-art presentation with
keyboard navigation, hot reload, themed palettes, syntax-highlighted code,
dithered images, math rendering, custom canvas/graph blocks, flowcharts,
sprites, tables, two-column layouts, incremental reveal, presenter tools,
and PNG export.

Example decks live in `examples/`: the ASEP Webtalk FEA deck
(`webtalk4_python_fea.md`), the DLSU Data Society workshop, and the PUP
Mathematics Gradient 2026 workshop.

## Features

- Markdown decks with `---` slide breaks, H1 section-title slides, H2 page-title slides, headings, paragraphs, ordered lists, bullet lists, and fenced code.
- Styled inline text: `**bold**`, `*italic*`, inline `` `code` ``, hard line breaks, inline links, and inline math.
- Clickable hyperlinks: hover shows the URL in the status bar, left-click opens the link in the default browser.
- Code panels with line numbers and optional Pygments syntax highlighting.
- Local and remote image blocks, resized and Floyd-Steinberg dithered into the active 16-color palette.
- Display math via Matplotlib mathtext, plus inline math rendered at text height when optional dependencies are installed.
- Pipe tables with header styling, alternating row backgrounds, content-fit or explicit column widths, cell text wrapping, and left/center/right table alignment.
- Two-column slide layout with a standalone `|||` separator.
- Incremental reveal with `<!-- incremental -->` or `<!-- step -->` comments.
- `pyxel-canvas` blocks for points, lines, curves, filled areas, rectangles, and text.
- `pyxel-flow` blocks for auto-laid-out flowcharts with arrow-connected boxes.
- `pyxel-graph` blocks for safe one-variable math plots, grids, axes, and shaded regions.
- `pyxel-sprite` blocks that render static or animated sprites from a `.pyxres` resource file.
- Built-in themes: `vscode_light` (default), `gameboy`, `gradient`, `arcade_space`, and `asep_structural` (with a decorative masonry motif on title slides).
- Downloaded BDF fonts with a built-in Pyxel 4x6 fallback.
- Presenter chrome: slide counter, progress bar, presenter timer, overview grid, and hot reload.
- Export mode that renders every slide to `slide_NNN.png`.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For the full rendering experience, install optional dependencies too:

```bash
pip install -e ".[full]"
```

The `full` extra enables Pygments syntax highlighting, Pillow image handling and
PNG export, and Matplotlib math rendering. For development and tests:

```bash
pip install -e ".[full,dev]"
```

## Run

```bash
pyxel-slides examples/webtalk4_python_fea.md
```

Useful options:

```bash
pyxel-slides examples/webtalk4_python_fea.md --theme gradient
pyxel-slides examples/webtalk4_python_fea.md --theme arcade_space
pyxel-slides examples/webtalk4_python_fea.md --theme asep_structural
pyxel-slides examples/webtalk4_python_fea.md --resolution 480x270 --fps 60
pyxel-slides examples/webtalk4_python_fea.md --title "Python Workshop"
pyxel-slides examples/webtalk4_python_fea.md --pyxres examples/demo.pyxres
pyxel-slides examples/webtalk4_python_fea.md --typewriter
pyxel-slides examples/webtalk4_python_fea.md --no-hot-reload
pyxel-slides examples/webtalk4_python_fea.md --no-fonts
pyxel-slides examples/webtalk4_python_fea.md --export-dir exported-slides
```

The default resolution is `384x216`.
If a `<deck>.pyxres` file exists next to the Markdown file, it is loaded
automatically. The first normal run may download BDF fonts into
`~/.cache/pyxel_slides/fonts/`; pass `--no-fonts` to use Pyxel's built-in font.

## Themes

Pass `--theme NAME` to pick one of the built-in palettes:

| Theme | Description |
| --- | --- |
| `vscode_light` (default) | White slides with VS Code Light+ syntax colors, blue chrome |
| `gameboy` | Classic Game Boy DMG 4-shade green palette |
| `gradient` | "Rising Along the Gradient" poster: deep purple, lavender text, violet/pink/gold accents |
| `arcade_space` | Python Workshop O-Day poster: starfield navy, arcade yellow, rocket blues |
| `asep_structural` | ASEP Webtalk deck: deep navy `#3C3E95`, mustard gold `#EEBD54`/`#B38B3E`, and periwinkle/lavender accents on white content slides |

Themes can define a decorative motif that renders behind title and
section-header slides. `asep_structural` uses a "masonry" motif: clusters of
rounded-rectangle blocks in navy, gold, and lavender anchored to the bottom
corners, evoking the structural-engineering branding of the deck.

## Controls

| Key / input | Action |
| --- | --- |
| Right / Space / PgDn / Enter | Next incremental step, then next slide |
| Left / PgUp / Backspace | Previous incremental step, then previous slide |
| Down / Up | Step forward / backward, crossing slides at the ends |
| Home / End | First / last slide |
| R | Reload Markdown from disk |
| O | Open overview grid |
| Up / Down in overview | Scroll overview rows |
| Click a slide in overview | Jump to that slide |
| T | Reset presenter timer |
| Hover a link | Show URL in the status bar |
| Left-click a link | Open URL in the default browser |
| Esc | Close overview, or quit outside overview |
| Q | Quit |

## Markdown

Slide breaks are explicit: only `---` starts a new slide. A `##` heading creates
a page title, but it does not split the deck.

````markdown
![Workshop logo](../picture_python_logo.png?scale=0.45)

# Workshop Title

## Workshop Subtitle

Presenter Name<br/>
Position / Work<br/>
Date

---

# Section Title

Optional subtitle text.

---

## Page Title

This is a paragraph with **bold**, *italic*, `code`, [a link](https://example.com),
and inline math $x^2 + y^2 = z^2$.

<!-- incremental -->
- This appears on the next step.
- Nested list indentation is preserved.

|||

![Image alt](../picture_python_logo.png?scale=1.2)

---

## Code

```python
def greet(name: str) -> None:
    print(f"Hello, {name}")
```
````

Supported Markdown and block syntax:

The first slide gets a dedicated cover layout when it starts with an optional
logo image followed by an H1. Use this order: logo, H1 title, H2 subtitle,
then name, position/work, and date as separate lines.

| Source | Rendered as |
| --- | --- |
| `---` | Slide break |
| First slide: image + `# Title` + `## Subtitle` + details | Cover slide |
| `# Title` | Section-title slide |
| `## Title` | Page title with accent underline |
| `### Title` and lower | Subheadings |
| Paragraphs | Wrapped styled text |
| `- item` / `1. item` | Bullet and numbered lists |
| `` `code` `` | Inline code pill |
| `[text](url)` | Clickable hyperlink |
| `$...$` | Inline math |
| `$$...$$` | Display math block |
| `![alt](path.png)` | Dithered image block |
| `![alt](path.png?scale=1.5)` | Image block with scale factor |
| Markdown pipe table | Rendered table |
| `|||` on its own paragraph | Two-column break |
| `<!-- incremental -->` / `<!-- step -->` | Increment following blocks to the next reveal step |
| ```` ```pyxel-canvas ```` | Pixel canvas diagram |
| ```` ```pyxel-flow ```` | Auto-laid-out flowchart |
| ```` ```pyxel-graph ```` | Function graph canvas |
| ```` ```pyxel-sprite ```` | Pyxel image-bank sprite |

### Tables

Pipe tables render with a styled header row and alternating row backgrounds.
By default each column is sized to fit its content (not split equally), and
cell text that overflows its column wraps onto extra lines instead of being
clipped.

A paragraph placed immediately above the table can set layout metadata:

- `col_widths=140,220` - explicit column widths in pixels. A value of `0`
  leaves that column on auto (it shares whatever width remains). When the
  widths total more than the slide width, they are scaled down proportionally.
- `align=left|center|right` - horizontal position of the whole table within
  the slide (default `left`).

```markdown
align=center
col_widths=80,0

| Aspect | Description |
| --- | --- |
| Cost | Free |
| Customize | A much longer description that wraps inside its column |
```

## Canvas Blocks

Use a `pyxel-canvas` fence for small 16-color diagrams:

````markdown
```pyxel-canvas
width=220
height=120
bg=9
border=14
scale=1
align=center
thickness=2
text_size=1
line 10 100 210 20 color=2
arrow 20 60 200 60 color=2 head=8 thickness=2
curve 20,100 80,10 140,10 200,100 color=4 steps=48 thickness=3
area 40,85 90,45 140,85 fill=12 color=2 thickness=2
rect 152 62 42 28 color=5 fill=13 thickness=2
circle 120 45 18 color=11 fill=0 thickness=2
text 12 10 "Canvas demo" color=1 size=2
```
````

Supported commands include `point`, `line`, `polyline` / `path`, `curve`,
`area` / `polygon`, `rect`, `circle`, `text`, and `arrow` (a line with a
filled triangular arrowhead; `head=N` sets its length in pixels).

Readability options:

| Option | Where | Meaning |
| --- | --- | --- |
| `thickness=N` | fence header, or any stroke command | Line/outline stroke width in pixels (default `1`) |
| `text_size=N` | fence header, or `text` as `size=N` | Integer scale of the 4x6 built-in text font (default `1`) |
| `size=N` | `point` | Point diameter in pixels |
| `fill=COLOR` / `fill=true` | `area`, `rect`, `circle` | Fill interior with a color index |
| `color=N` | any command | Pyxel palette index `0..15` |
| `steps=N` | `curve` | Bezier sampling resolution |

The header `thickness=` and `text_size=` set the default for every command in
the block; per-command `thickness=` and `size=` override them.

## Flowcharts

Use a `pyxel-flow` fence for auto-laid-out flowcharts. Each line is a node
box; boxes are chained with arrows either top-to-bottom (`direction=down`,
the default) or left-to-right (`direction=right`). A `|` inside a label
forces a line break; the whole chart is centered horizontally.

````markdown
```pyxel-flow
direction=down
color=2
gap=8
Loads and supports|F, fixed
Solve F = K d|np.linalg.solve
Post-process|reactions, member forces
```
````

Flow options:

| Option | Meaning |
| --- | --- |
| `direction=down` / `right` | Chain direction (default `down`) |
| `color=N` | Box outline and arrow colour (palette index) |
| `gap=N` | Spacing between boxes in pixels (default `10`) |
| `fill=N` | Box fill colour; default is the theme code-panel background with code-panel text |

Horizontal chains are width-capped so they never overflow the slide; labels
that don't fit wrap onto extra lines inside their box.

## Graph Blocks

Use a `pyxel-graph` fence to plot safe one-variable math expressions into a
canvas. The graph expression language allows numeric constants, `x`, arithmetic
operators, and functions from Python's `math` module.

````markdown
```pyxel-graph
width=260
height=140
x=-6.28,6.28
y=-1.5,1.5
grid=true
grid_thickness=1
axis_thickness=2
plot_thickness=3
plot sin(x) color=2
plot cos(x) color=5 thickness=2
shade_under sin(x) baseline=0 color=12 x=0,3.14
shade_between upper=cos(x) lower=sin(x) color=13 x=-1.57,1.57 thickness=1
```
````

Graph readability options (all accept per-command `thickness=` overrides on
`plot`, `shade_under`, and `shade_between`):

| Option | Meaning |
| --- | --- |
| `axis_thickness=N` | Stroke width of the x/y axes (default `1`) |
| `grid_thickness=N` | Stroke width of grid lines (default `1`) |
| `plot_thickness=N` | Stroke width of function plots (default `2`) |
| `shading_thickness=N` | Stroke width of shaded region outlines (default `1`) |
| `samples=N` | Number of sampled points per plot/region (default `160`) |
| `axis_color=N` / `grid_color=N` | Palette indices for axes/grid |

The same primitives are available from Python:

```python
from pyxel_slides import Canvas, Graph

canvas = Canvas(width=220, height=120, bg=9, border=14,
                default_thickness=2, default_text_size=1)
graph = Graph(canvas, x_min=-5, x_max=5, y_min=-2, y_max=2, grid=True,
              axis_thickness=2, grid_thickness=1, plot_thickness=3,
              shading_thickness=1)
graph.plot("x^2 - 1", color=2).shade_under("sin(x)", color=12).draw()
```

Every `Canvas` stroke method (`point`, `line`, `polyline`, `curve`, `area`,
`rect`, `circle`, `arrow`) takes a `thickness` keyword in pixels, and `text`
takes a `size` keyword for integer font scaling. Omitting the keyword falls
back to the canvas default. `arrow` additionally takes `head=` for the
arrowhead length.

## Sprites

Pyxel resource files (`.pyxres`) can hold image-bank sprites for a deck. Create
or edit one with Pyxel's resource editor:

```bash
pyxel edit examples/demo.pyxres
```

Once the `.pyxres` exists beside the deck, `pyxel-slides` auto-loads it. You can
also pass one explicitly with `--pyxres`.

````markdown
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
````

Sprite fields:

| Field | Meaning |
| --- | --- |
| `img` | Pyxel image bank index |
| `u`, `v` | Source position in the image bank |
| `w`, `h` | Source sprite size |
| `scale` | Draw scale |
| `colkey` | Transparent palette index; omit or use `-1` for no transparency |
| `frames` | Number of animation frames in a horizontal strip |
| `frame_w` | Width of one animation frame; defaults to `w` |
| `anim_fps` | Animation rate |

## Export

Render every slide to PNG and quit:

```bash
pyxel-slides examples/webtalk4_python_fea.md --theme asep_structural --export-dir exported-slides
```

Files are written as:

```text
exported-slides/
  slide_000.png
  slide_001.png
  slide_002.png
```

PNG export requires Pillow, so use `pip install -e ".[full]"`.

## Python API

The package exposes the parser, IR objects, renderer, app, themes, drawing
helpers, and optional-dependency probes:

```python
from pathlib import Path

from pyxel_slides import ASEP_STRUCTURAL, ARCADE_SPACE, Canvas, FlowBlock, Graph, SlidesApp, parse_markdown

slides = parse_markdown(Path("examples/webtalk4_python_fea.md").read_text(encoding="utf-8"))

canvas = Canvas(width=120, height=80).line(0, 0, 119, 79, color=2)
canvas.arrow(10, 40, 110, 40, color=2, head=6)   # line with arrowhead
graph = Graph(Canvas(width=120, height=80), x_min=-3, x_max=3).plot("sin(x)")

app = SlidesApp(Path("examples/webtalk4_python_fea.md"), theme=ASEP_STRUCTURAL, width=480, height=270)
app.run()
```

`TableBlock` exposes `col_widths` (pixel widths per column, `0` = auto) and
`align` (`"left"`, `"center"`, or `"right"`) for programmatic table layout.
`FlowBlock` holds flowchart nodes (`nodes`, `direction`, `color`, `gap`) as
parsed from `pyxel-flow` fences.

## Project Layout

```text
pyxel_slides/
  app.py          # Pyxel window, input, navigation, timer, overview, export
  canvas.py       # Canvas, Graph primitives, arrow drawing
  cli.py          # pyxel-slides command-line entry point
  dither.py       # Image resizing and Floyd-Steinberg dithering
  highlight.py    # Pygments token mapping
  ir.py           # Slide/block dataclasses (incl. FlowBlock, TableBlock)
  mathtext.py     # Matplotlib mathtext rasterization
  parser.py       # Markdown to slide IR (canvas/graph/flow/sprite fences)
  renderer.py     # Slide IR to Pyxel draw calls (incl. table + flowchart layout)
  theme.py        # Built-in palettes and theme roles
  assets/fonts.py # BDF font download/cache/loading
examples/
  webtalk4_python_fea.md
  dlsu_data_society_python_workshop_2.md
  pup_mathematics_gradient_2026 copy.md
tests/
  test_*.py
pyproject.toml
```

## License

MIT.
