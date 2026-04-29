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

Inline styling (`**bold**`, `*italic*`, links, images, math) parses but renders
as plain text in Phase 1.

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
