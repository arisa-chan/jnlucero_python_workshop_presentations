"""Tests for Canvas and Graph slide blocks."""

from __future__ import annotations

import pytest
import math

from pyxel_slides.canvas import Canvas, Graph, UnsafeExpressionError, compile_math_expression
from pyxel_slides.ir import CanvasBlock
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
