"""Tests for Canvas and Graph slide blocks."""

from __future__ import annotations

import pytest
import math

from pyxel_slides.canvas import Canvas, Graph, UnsafeExpressionError, compile_math_expression
from pyxel_slides.ir import CanvasBlock, FlowBlock
from pyxel_slides.parser import parse_markdown


def test_canvas_line_rasterizes_inside_bounds():
    canvas = Canvas(width=8, height=6, bg=0)
    canvas.line(0, 0, 7, 5, color=2)

    pixels = canvas.rasterize()

    assert pixels[0][0] == 2
    assert pixels[5][7] == 2
    assert len(pixels) == 6
    assert all(len(row) == 8 for row in pixels)


def test_canvas_area_fill_and_outline():
    canvas = Canvas(width=12, height=12, bg=0)
    canvas.area([(2, 2), (9, 2), (9, 9), (2, 9)], color=2, fill=12)

    pixels = canvas.rasterize()

    assert pixels[2][2] == 2
    assert pixels[5][5] == 12


def test_canvas_text_command_is_kept_for_renderer():
    canvas = Canvas(width=32, height=16)
    canvas.text(4, 5, "hello", color=3)

    assert len(canvas.text_commands) == 1
    assert canvas.text_commands[0].text == "hello"
    assert canvas.rasterize()[5][4] == canvas.bg


def test_compile_math_expression_allows_math_subset():
    fn = compile_math_expression("sin(x) + x^2")

    assert fn(0) == pytest.approx(0.0)
    assert fn(2) == pytest.approx(math.sin(2) + 4)


def test_compile_math_expression_rejects_unsafe_code():
    with pytest.raises(UnsafeExpressionError):
        compile_math_expression("__import__('os').system('echo nope')")


def test_graph_draws_plot_into_canvas():
    canvas = Canvas(width=64, height=32, bg=0)
    graph = Graph(canvas, x_min=-1, x_max=1, y_min=-1, y_max=1, axes=True)
    graph.plot("x", color=2, samples=20).draw()

    pixels = canvas.rasterize()

    assert any(2 in row for row in pixels)


def test_canvas_line_thickness_widens_stroke():
    canvas = Canvas(width=16, height=16, bg=0)
    canvas.line(2, 8, 13, 8, color=2, thickness=3)

    pixels = canvas.rasterize()

    assert pixels[8][2] == 2
    assert pixels[7][2] == 2
    assert pixels[9][2] == 2
    assert pixels[6][2] == 0


def test_canvas_thin_line_is_single_pixel():
    canvas = Canvas(width=16, height=16, bg=0)
    canvas.line(2, 8, 13, 8, color=2, thickness=1)

    pixels = canvas.rasterize()

    assert pixels[8][2] == 2
    assert pixels[7][2] == 0
    assert pixels[9][2] == 0


def test_canvas_default_thickness_applies_to_all_commands():
    canvas = Canvas(width=16, height=16, bg=0, default_thickness=2)
    canvas.line(2, 8, 13, 8, color=2)

    pixels = canvas.rasterize()

    assert pixels[8][2] == 2
    assert pixels[7][2] == 2
    assert pixels[6][2] == 0


def test_canvas_rect_and_area_thickness():
    canvas = Canvas(width=20, height=20, bg=0)
    canvas.rect(4, 4, 11, 11, color=2, thickness=3)
    canvas.area([(2, 15), (17, 15), (17, 18)], color=3, thickness=2)

    pixels = canvas.rasterize()

    assert pixels[4][5] == 2
    assert pixels[5][4] == 2
    assert pixels[2][4] == 0
    assert pixels[15][3] == 3
    assert pixels[16][3] == 3


def test_canvas_circle_outline_and_fill():
    canvas = Canvas(width=32, height=32, bg=0)
    canvas.circle(16, 16, 10, color=2, fill=12, thickness=2)

    pixels = canvas.rasterize()

    assert pixels[16][16] == 12
    assert pixels[16][6] == 2
    assert pixels[16][5] == 0
    assert pixels[26][16] == 2


def test_canvas_circle_outline_only():
    canvas = Canvas(width=32, height=32, bg=0)
    canvas.circle(16, 16, 10, color=2)

    pixels = canvas.rasterize()

    assert pixels[16][16] == 0
    assert pixels[16][6] == 2


def test_canvas_curve_thickness():
    canvas = Canvas(width=24, height=24, bg=0)
    canvas.curve([(2, 12), (12, 2), (21, 12)], color=4, steps=32, thickness=3)

    pixels = canvas.rasterize()

    assert pixels[12][2] == 4
    assert pixels[13][2] == 4
    assert pixels[14][2] == 0
    assert pixels[7][12] == 4
    assert pixels[5][12] == 0


def test_canvas_text_size_stored_on_command():
    canvas = Canvas(width=32, height=16)
    canvas.text(4, 5, "hello", color=3, size=2)

    assert canvas.text_commands[0].text_size == 2


def test_canvas_default_text_size():
    canvas = Canvas(width=32, height=16, default_text_size=3)
    canvas.text(4, 5, "hello", color=3)

    assert canvas.text_commands[0].text_size == 3


def test_graph_thickness_fields_applied():
    canvas = Canvas(width=64, height=32, bg=0)
    graph = Graph(
        canvas,
        x_min=-1, x_max=1, y_min=-1, y_max=1,
        axes=True,
        grid=True,
        axis_thickness=3,
        grid_thickness=1,
        plot_thickness=2,
    )
    graph.plot("x", color=2, samples=20).draw()

    pixels = canvas.rasterize()

    assert any(2 in row for row in pixels)
    assert all(cmd.thickness in (1, 2, 3) for cmd in canvas.commands)


def test_graph_plot_thickness_option():
    canvas = Canvas(width=64, height=32, bg=0)
    graph = Graph(canvas, x_min=-1, x_max=1, y_min=-1, y_max=1, axes=False)
    graph.plot("0", color=2, samples=20, thickness=3).draw()

    plots = [cmd for cmd in canvas.commands if cmd.kind == "polyline"]
    assert plots and all(cmd.thickness == 3 for cmd in plots)


def test_parse_canvas_fence_thickness_circle_text():
    md = """\
```pyxel-canvas
width=40
height=20
thickness=2
line 0 0 39 19 color=2
circle 20 10 8 color=5 fill=12 thickness=1
text 2 2 "hello" color=1 size=2
```
"""
    slides = parse_markdown(md)

    block = slides[0].blocks[0]
    assert isinstance(block, CanvasBlock)
    assert block.canvas.default_thickness == 2
    kinds = {cmd.kind for cmd in block.canvas.commands}
    assert "circle" in kinds
    line = next(cmd for cmd in block.canvas.commands if cmd.kind == "line")
    circle = next(cmd for cmd in block.canvas.commands if cmd.kind == "circle")
    text = next(cmd for cmd in block.canvas.commands if cmd.kind == "text")
    assert line.thickness == 2
    assert circle.thickness == 1
    assert circle.fill == 12
    assert text.text_size == 2


def test_parse_graph_fence_thickness_options():
    md = """\
```pyxel-graph
width=80
height=50
x=-3.14,3.14
y=-1.5,1.5
grid=true
plot_thickness=3
axis_thickness=2
plot sin(x) color=2 thickness=1
shade_under cos(x) baseline=0 color=12 x=-1.57,1.57 thickness=2
```
"""
    slides = parse_markdown(md)

    block = slides[0].blocks[0]
    assert isinstance(block, CanvasBlock)
    plots = [cmd for cmd in block.canvas.commands if cmd.kind == "polyline"]
    areas = [cmd for cmd in block.canvas.commands if cmd.kind == "area"]
    assert any(cmd.thickness == 1 for cmd in plots)
    assert any(cmd.thickness == 2 for cmd in areas)
    assert any(cmd.thickness == 2 for cmd in block.canvas.commands if cmd.kind == "line")


def test_parse_canvas_fence_produces_canvas_block():
    md = """\
```pyxel-canvas
width=40
height=20
bg=9
border=14
line 0 0 39 19 color=2
text 2 2 "hello graph" color=1
```
"""
    slides = parse_markdown(md)

    block = slides[0].blocks[0]
    assert isinstance(block, CanvasBlock)
    assert block.canvas.width == 40
    assert block.canvas.height == 20
    assert block.canvas.bg == 9
    assert len(block.canvas.text_commands) == 1


def test_parse_graph_fence_draws_to_canvas_block():
    md = """\
```pyxel-graph
width=80
height=50
x=-3.14,3.14
y=-1.5,1.5
grid=true
plot sin(x) color=2
shade_under cos(x) baseline=0 color=12 x=-1.57,1.57
```
"""
    slides = parse_markdown(md)

    block = slides[0].blocks[0]
    assert isinstance(block, CanvasBlock)
    assert block.canvas.width == 80
    assert block.canvas.height == 50
    assert any(cmd.kind == "polyline" and cmd.color == 2 for cmd in block.canvas.commands)
    assert any(cmd.kind == "area" and cmd.fill == 12 for cmd in block.canvas.commands)


# --------------------------------------------------------------------------- #
# arrow command
# --------------------------------------------------------------------------- #

def test_canvas_arrow_rasterizes_line_and_head():
    canvas = Canvas(width=40, height=20, bg=0)
    canvas.arrow(4, 10, 34, 10, color=2, head=6)

    pixels = canvas.rasterize()
    # Arrow tip at (34, 10); ensure the head triangle pixels are filled.
    assert pixels[10][34] == 2
    assert pixels[10][4] == 2  # start of the shaft
    arrow_px = sum(1 for row in pixels for v in row if v == 2)
    assert arrow_px > 8  # shaft + head

    cmds = [c for c in canvas.commands if c.kind == "arrow"]
    assert len(cmds) == 1
    assert cmds[0].points == [(4, 10), (34, 10)]


def test_parse_canvas_fence_arrow_command():
    md = """\
```pyxel-canvas
width=40
height=20
arrow 2 10 36 10 color=2 head=7 thickness=2
```
"""
    block = parse_markdown(md)[0].blocks[0]
    assert isinstance(block, CanvasBlock)
    arrow = next(cmd for cmd in block.canvas.commands if cmd.kind == "arrow")
    assert arrow.points == [(2, 10), (36, 10)]
    assert arrow.color == 2
    assert arrow.radius == 7
    assert arrow.thickness == 2


# --------------------------------------------------------------------------- #
# pyxel-flow fences
# --------------------------------------------------------------------------- #

def test_parse_flow_fence_basic():
    md = """\
```pyxel-flow
A
B
C
```
"""
    block = parse_markdown(md)[0].blocks[0]
    assert isinstance(block, FlowBlock)
    assert block.nodes == ["A", "B", "C"]
    assert block.direction == "down"


def test_parse_flow_fence_options_and_pipes():
    md = """\
```pyxel-flow
direction=right
color=5
gap=12
Step 1|first
Step 2|second
```
"""
    block = parse_markdown(md)[0].blocks[0]
    assert isinstance(block, FlowBlock)
    assert block.direction == "right"
    assert block.color == 5
    assert block.gap == 12
    assert block.nodes == ["Step 1|first", "Step 2|second"]
