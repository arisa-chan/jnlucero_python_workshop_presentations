"""Canvas and graph helpers for pyxel-slides.

The classes here are deliberately Pyxel-free.  They build a small command
stream and can rasterize primitive geometry into a 16-colour indexed pixel
buffer.  The slide renderer turns that buffer into a Pyxel image and draws text
commands with Pyxel's built-in font so everything stays clipped to the canvas.
"""

from __future__ import annotations

import ast
import math
from dataclasses import dataclass, field
from typing import Callable, Iterable, Literal, Sequence


Point = tuple[int, int]
FloatPoint = tuple[float, float]
FunctionLike = Callable[[float], float] | str


def _clamp_color(col: int) -> int:
    return max(0, min(15, int(col)))


def _as_point(x: float, y: float) -> Point:
    return int(round(x)), int(round(y))


@dataclass
class CanvasCommand:
    kind: Literal["point", "line", "polyline", "curve", "area", "rect", "circle", "text"]
    points: list[Point] = field(default_factory=list)
    color: int = 1
    fill: int | None = None
    text: str = ""
    size: int = 1
    steps: int = 32
    thickness: int = 1
    radius: int = 0
    text_size: int = 1


@dataclass
class Canvas:
    """A small 16-colour indexed drawing surface for slide diagrams.

    Coordinates are local to the canvas, with ``(0, 0)`` at the top-left.
    Colours are Pyxel palette indices and are clamped to the range ``0..15``.
    """

    width: int = 240
    height: int = 120
    bg: int = 0
    border: int = -1
    commands: list[CanvasCommand] = field(default_factory=list)
    default_thickness: int = 1
    default_text_size: int = 1

    def __post_init__(self) -> None:
        self.width = max(1, int(self.width))
        self.height = max(1, int(self.height))
        self.bg = _clamp_color(self.bg)
        self.border = int(self.border)
        if self.border >= 0:
            self.border = _clamp_color(self.border)
        self.default_thickness = max(1, int(self.default_thickness))
        self.default_text_size = max(1, int(self.default_text_size))

    def clear(self) -> None:
        self.commands.clear()

    def point(
        self,
        x: float,
        y: float,
        color: int = 1,
        size: int = 1,
        thickness: int | None = None,
    ) -> "Canvas":
        """Draw a filled square of ``size`` pixels, drawn with ``thickness``."""

        self.commands.append(CanvasCommand(
            kind="point",
            points=[_as_point(x, y)],
            color=_clamp_color(color),
            size=max(1, int(size)),
            thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
        ))
        return self

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: int = 1,
        thickness: int | None = None,
    ) -> "Canvas":
        """Draw a line with the given stroke thickness in pixels."""

        self.commands.append(CanvasCommand(
            kind="line",
            points=[_as_point(x1, y1), _as_point(x2, y2)],
            color=_clamp_color(color),
            thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
        ))
        return self

    def polyline(
        self,
        points: Sequence[tuple[float, float]],
        color: int = 1,
        thickness: int | None = None,
    ) -> "Canvas":
        pts = [_as_point(x, y) for x, y in points]
        if pts:
            self.commands.append(CanvasCommand(
                kind="polyline",
                points=pts,
                color=_clamp_color(color),
                thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
            ))
        return self

    def curve(
        self,
        points: Sequence[tuple[float, float]],
        color: int = 1,
        steps: int = 32,
        thickness: int | None = None,
    ) -> "Canvas":
        """Draw a Bezier curve through the given control points.

        Two points degrade to a line; three or more points use the generic
        De Casteljau algorithm, so quadratic and cubic curves both work.
        """

        pts = [_as_point(x, y) for x, y in points]
        if len(pts) >= 2:
            self.commands.append(CanvasCommand(
                kind="curve",
                points=pts,
                color=_clamp_color(color),
                steps=max(2, int(steps)),
                thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
            ))
        return self

    def area(
        self,
        points: Sequence[tuple[float, float]],
        color: int = 1,
        fill: bool | int | None = None,
        thickness: int | None = None,
    ) -> "Canvas":
        """Draw a polygon outline, optionally with a shaded fill."""

        pts = [_as_point(x, y) for x, y in points]
        if len(pts) < 2:
            return self
        fill_col: int | None
        if fill is None or fill is False:
            fill_col = None
        elif fill is True:
            fill_col = _clamp_color(color)
        else:
            fill_col = _clamp_color(int(fill))
        self.commands.append(CanvasCommand(
            kind="area",
            points=pts,
            color=_clamp_color(color),
            fill=fill_col,
            thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
        ))
        return self

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: int = 1,
        fill: bool | int | None = None,
        thickness: int | None = None,
    ) -> "Canvas":
        fill_col: int | None
        if fill is None or fill is False:
            fill_col = None
        elif fill is True:
            fill_col = _clamp_color(color)
        else:
            fill_col = _clamp_color(int(fill))
        self.commands.append(CanvasCommand(
            kind="rect",
            points=[_as_point(x, y), _as_point(x + w - 1, y + h - 1)],
            color=_clamp_color(color),
            fill=fill_col,
            thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
        ))
        return self

    def circle(
        self,
        x: float,
        y: float,
        r: float,
        color: int = 1,
        fill: bool | int | None = None,
        thickness: int | None = None,
    ) -> "Canvas":
        """Draw a circle outline centered at ``(x, y)``, optionally filled.

        ``r`` is the radius in canvas pixels; the outline is drawn just
        inside that radius.
        """

        fill_col: int | None
        if fill is None or fill is False:
            fill_col = None
        elif fill is True:
            fill_col = _clamp_color(color)
        else:
            fill_col = _clamp_color(int(fill))
        self.commands.append(CanvasCommand(
            kind="circle",
            points=[_as_point(x, y)],
            color=_clamp_color(color),
            fill=fill_col,
            radius=max(1, int(round(r))),
            thickness=max(1, int(thickness)) if thickness is not None else self.default_thickness,
        ))
        return self

    def text(
        self,
        x: float,
        y: float,
        text: str,
        color: int = 1,
        size: int | None = None,
    ) -> "Canvas":
        """Draw text with an integer pixel-scale of the built-in 4x6 font."""

        self.commands.append(CanvasCommand(
            kind="text",
            points=[_as_point(x, y)],
            color=_clamp_color(color),
            text=str(text),
            text_size=max(1, int(size)) if size is not None else self.default_text_size,
        ))
        return self

    @property
    def text_commands(self) -> list[CanvasCommand]:
        return [cmd for cmd in self.commands if cmd.kind == "text"]

    def rasterize(self) -> list[list[int]]:
        """Return a ``height x width`` buffer of Pyxel palette indices."""

        pixels = [[self.bg for _ in range(self.width)] for _ in range(self.height)]

        for cmd in self.commands:
            if cmd.kind == "text":
                continue
            thickness = max(1, int(cmd.thickness))
            if cmd.kind == "point" and cmd.points:
                _draw_point(pixels, cmd.points[0], cmd.color, cmd.size, thickness)
            elif cmd.kind == "line" and len(cmd.points) >= 2:
                _draw_line(pixels, cmd.points[0], cmd.points[1], cmd.color, thickness)
            elif cmd.kind == "polyline":
                _draw_polyline(pixels, cmd.points, cmd.color, thickness)
            elif cmd.kind == "curve":
                _draw_curve(pixels, cmd.points, cmd.color, cmd.steps, thickness)
            elif cmd.kind == "area":
                if cmd.fill is not None and len(cmd.points) >= 3:
                    _fill_polygon(pixels, cmd.points, cmd.fill)
                _draw_polygon_outline(pixels, cmd.points, cmd.color, thickness)
            elif cmd.kind == "rect" and len(cmd.points) >= 2:
                _draw_rect(pixels, cmd.points[0], cmd.points[1], cmd.color, cmd.fill, thickness)
            elif cmd.kind == "circle" and cmd.points:
                _draw_circle(pixels, cmd.points[0], cmd.radius, cmd.color, cmd.fill, thickness)

        if self.border >= 0:
            _draw_rect(
                pixels,
                (0, 0),
                (self.width - 1, self.height - 1),
                self.border,
                None,
                max(1, self.default_thickness),
            )

        return pixels


def _set_pixel(pixels: list[list[int]], x: int, y: int, color: int) -> None:
    if 0 <= y < len(pixels) and 0 <= x < len(pixels[0]):
        pixels[y][x] = color


def _thick_span(pixels: list[list[int]], x: int, y: int, color: int, thickness: int) -> None:
    """Set a pixel plus an (even) thickness halo around it, clipped to bounds."""

    _set_pixel(pixels, x, y, color)
    if thickness <= 1:
        return
    r = thickness // 2
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    lo_y, hi_y = max(0, y - r), min(height - 1, y + r)
    lo_x, hi_x = max(0, x - r), min(width - 1, x + r)
    for py in range(lo_y, hi_y + 1):
        for px in range(lo_x, hi_x + 1):
            pixels[py][px] = color


def _draw_point(
    pixels: list[list[int]],
    point: Point,
    color: int,
    size: int = 1,
    thickness: int = 1,
) -> None:
    x, y = point
    size = max(1, int(size))
    thickness = max(1, int(thickness))
    half = size // 2
    for py in range(y - half, y - half + size):
        for px in range(x - half, x - half + size):
            _thick_span(pixels, px, py, color, thickness)


def _draw_line(
    pixels: list[list[int]],
    p0: Point,
    p1: Point,
    color: int,
    thickness: int = 1,
) -> None:
    x0, y0 = p0
    x1, y1 = p1
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        _thick_span(pixels, x0, y0, color, thickness)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _draw_polyline(
    pixels: list[list[int]],
    points: Sequence[Point],
    color: int,
    thickness: int = 1,
) -> None:
    for p0, p1 in zip(points, points[1:]):
        _draw_line(pixels, p0, p1, color, thickness)


def _bezier_point(points: Sequence[Point], t: float) -> FloatPoint:
    work: list[FloatPoint] = [(float(x), float(y)) for x, y in points]
    while len(work) > 1:
        work = [
            (
                (1.0 - t) * work[i][0] + t * work[i + 1][0],
                (1.0 - t) * work[i][1] + t * work[i + 1][1],
            )
            for i in range(len(work) - 1)
        ]
    return work[0]


def _draw_curve(
    pixels: list[list[int]],
    points: Sequence[Point],
    color: int,
    steps: int,
    thickness: int = 1,
) -> None:
    if len(points) < 2:
        return
    if len(points) == 2:
        _draw_line(pixels, points[0], points[1], color, thickness)
        return
    sampled = [_as_point(*_bezier_point(points, i / steps)) for i in range(steps + 1)]
    _draw_polyline(pixels, sampled, color, thickness)


def _draw_polygon_outline(
    pixels: list[list[int]],
    points: Sequence[Point],
    color: int,
    thickness: int = 1,
) -> None:
    if len(points) < 2:
        return
    _draw_polyline(pixels, points, color, thickness)
    if len(points) > 2:
        _draw_line(pixels, points[-1], points[0], color, thickness)


def _draw_rect(
    pixels: list[list[int]],
    p0: Point,
    p1: Point,
    color: int,
    fill: int | None,
    thickness: int = 1,
) -> None:
    x0, y0 = p0
    x1, y1 = p1
    left, right = sorted((x0, x1))
    top, bottom = sorted((y0, y1))

    if fill is not None:
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                _set_pixel(pixels, x, y, fill)

    _draw_line(pixels, (left, top), (right, top), color, thickness)
    _draw_line(pixels, (right, top), (right, bottom), color, thickness)
    _draw_line(pixels, (right, bottom), (left, bottom), color, thickness)
    _draw_line(pixels, (left, bottom), (left, top), color, thickness)


def _draw_circle(
    pixels: list[list[int]],
    center: Point,
    radius: int,
    color: int,
    fill: int | None,
    thickness: int = 1,
) -> None:
    """Rasterize a circle outline, optionally filled, clipped to the canvas."""

    cx, cy = center
    radius = max(1, int(radius))
    thickness = max(1, int(thickness))
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    if width == 0:
        return

    if fill is not None:
        for y in range(cy - radius, cy + radius + 1):
            dy = y - cy
            if abs(dy) > radius:
                continue
            half_w = int(round(math.sqrt(radius * radius - dy * dy)))
            for x in range(cx - half_w, cx + half_w + 1):
                _set_pixel(pixels, x, y, fill)

    inner = max(0, radius - thickness)
    inner2 = inner * inner
    outer2 = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        dy = y - cy
        if abs(dy) > radius:
            continue
        half_w = int(round(math.sqrt(radius * radius - dy * dy)))
        for x in range(cx - half_w, cx + half_w + 1):
            d2 = (x - cx) * (x - cx) + dy * dy
            if d2 <= outer2 and d2 >= inner2:
                _set_pixel(pixels, x, y, color)


def _fill_polygon(pixels: list[list[int]], points: Sequence[Point], color: int) -> None:
    if len(points) < 3:
        return
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    if width == 0:
        return

    min_y = max(0, min(y for _, y in points))
    max_y = min(height - 1, max(y for _, y in points))

    for y in range(min_y, max_y + 1):
        intersections: list[float] = []
        for (x0, y0), (x1, y1) in zip(points, [*points[1:], points[0]]):
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                t = (y - y0) / (y1 - y0)
                intersections.append(x0 + t * (x1 - x0))

        intersections.sort()
        for x_start, x_end in zip(intersections[0::2], intersections[1::2]):
            left = max(0, int(math.ceil(min(x_start, x_end))))
            right = min(width - 1, int(math.floor(max(x_start, x_end))))
            for x in range(left, right + 1):
                pixels[y][x] = color


_MATH_ENV = {
    name: getattr(math, name)
    for name in dir(math)
    if not name.startswith("_")
}
_MATH_ENV.update({
    "abs": abs,
    "max": max,
    "min": min,
    "round": round,
})


class UnsafeExpressionError(ValueError):
    """Raised when a graph expression is not in the safe math subset."""


class _MathExpressionValidator(ast.NodeVisitor):
    _allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
    )
    _allowed_binops = (
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
    )
    _allowed_unaryops = (ast.UAdd, ast.USub)

    def visit(self, node):  # type: ignore[override]
        if not isinstance(node, self._allowed_nodes + self._allowed_binops + self._allowed_unaryops):
            raise UnsafeExpressionError(f"Unsupported expression syntax: {type(node).__name__}")
        return super().visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if not isinstance(node.op, self._allowed_binops):
            raise UnsafeExpressionError(f"Unsupported operator: {type(node.op).__name__}")
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        if not isinstance(node.op, self._allowed_unaryops):
            raise UnsafeExpressionError(f"Unsupported unary operator: {type(node.op).__name__}")
        self.visit(node.operand)

    def visit_Call(self, node: ast.Call) -> None:
        if not isinstance(node.func, ast.Name) or node.func.id not in _MATH_ENV:
            raise UnsafeExpressionError("Only named math functions are allowed")
        if node.keywords:
            raise UnsafeExpressionError("Keyword arguments are not allowed in graph expressions")
        for arg in node.args:
            self.visit(arg)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id != "x" and node.id not in _MATH_ENV:
            raise UnsafeExpressionError(f"Unknown graph expression name: {node.id}")

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, (int, float)):
            raise UnsafeExpressionError("Only numeric constants are allowed")


def compile_math_expression(expr: str) -> Callable[[float], float]:
    """Compile a safe one-variable math expression into ``f(x)``."""

    normalized = expr.strip().replace("^", "**")
    if not normalized:
        raise UnsafeExpressionError("Graph expression is empty")
    tree = ast.parse(normalized, mode="eval")
    _MathExpressionValidator().visit(tree)
    code = compile(tree, "<pyxel-slides-graph>", "eval")

    def _func(x: float) -> float:
        value = eval(code, {"__builtins__": {}}, {**_MATH_ENV, "x": x})  # noqa: S307
        return float(value)

    return _func


def _coerce_function(fn: FunctionLike) -> Callable[[float], float]:
    if callable(fn):
        return fn
    return compile_math_expression(fn)


@dataclass
class FunctionPlot:
    fn: FunctionLike
    color: int = 2
    samples: int | None = None
    thickness: int | None = None


@dataclass
class ShadedRegion:
    upper: FunctionLike
    lower: FunctionLike | float = 0.0
    color: int = 12
    x_min: float | None = None
    x_max: float | None = None
    samples: int | None = None
    thickness: int | None = None


@dataclass
class Graph:
    """Draw math functions into a ``Canvas``."""

    canvas: Canvas
    x_min: float = -10.0
    x_max: float = 10.0
    y_min: float = -10.0
    y_max: float = 10.0
    axes: bool = True
    grid: bool = False
    axis_color: int = 3
    grid_color: int = 14
    samples: int = 160
    axis_thickness: int = 1
    grid_thickness: int = 1
    plot_thickness: int = 2
    shading_thickness: int = 1
    plots: list[FunctionPlot] = field(default_factory=list)
    shadings: list[ShadedRegion] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.x_min == self.x_max:
            self.x_max = self.x_min + 1.0
        if self.y_min == self.y_max:
            self.y_max = self.y_min + 1.0
        if self.x_min > self.x_max:
            self.x_min, self.x_max = self.x_max, self.x_min
        if self.y_min > self.y_max:
            self.y_min, self.y_max = self.y_max, self.y_min
        self.axis_color = _clamp_color(self.axis_color)
        self.grid_color = _clamp_color(self.grid_color)
        self.samples = max(2, int(self.samples))
        self.axis_thickness = max(1, int(self.axis_thickness))
        self.grid_thickness = max(1, int(self.grid_thickness))
        self.plot_thickness = max(1, int(self.plot_thickness))
        self.shading_thickness = max(1, int(self.shading_thickness))

    def plot(
        self,
        fn: FunctionLike,
        color: int = 2,
        samples: int | None = None,
        thickness: int | None = None,
    ) -> "Graph":
        if isinstance(fn, str):
            compile_math_expression(fn)
        self.plots.append(FunctionPlot(
            fn=fn,
            color=_clamp_color(color),
            samples=samples,
            thickness=max(1, int(thickness)) if thickness is not None else None,
        ))
        return self

    def shade_under(
        self,
        fn: FunctionLike,
        baseline: FunctionLike | float = 0.0,
        color: int = 12,
        x_min: float | None = None,
        x_max: float | None = None,
        samples: int | None = None,
        thickness: int | None = None,
    ) -> "Graph":
        if isinstance(fn, str):
            compile_math_expression(fn)
        if isinstance(baseline, str):
            compile_math_expression(baseline)
        self.shadings.append(ShadedRegion(
            upper=fn,
            lower=baseline,
            color=_clamp_color(color),
            x_min=x_min,
            x_max=x_max,
            samples=samples,
            thickness=max(1, int(thickness)) if thickness is not None else None,
        ))
        return self

    def shade_between(
        self,
        upper: FunctionLike,
        lower: FunctionLike,
        color: int = 12,
        x_min: float | None = None,
        x_max: float | None = None,
        samples: int | None = None,
        thickness: int | None = None,
    ) -> "Graph":
        if isinstance(upper, str):
            compile_math_expression(upper)
        if isinstance(lower, str):
            compile_math_expression(lower)
        self.shadings.append(ShadedRegion(
            upper=upper,
            lower=lower,
            color=_clamp_color(color),
            x_min=x_min,
            x_max=x_max,
            samples=samples,
            thickness=max(1, int(thickness)) if thickness is not None else None,
        ))
        return self

    def to_pixel(self, x: float, y: float) -> Point:
        px = (x - self.x_min) / (self.x_max - self.x_min) * (self.canvas.width - 1)
        py = (self.y_max - y) / (self.y_max - self.y_min) * (self.canvas.height - 1)
        return _as_point(px, py)

    def draw(self) -> Canvas:
        if self.grid:
            self._draw_grid()
        self._draw_shadings()
        if self.axes:
            self._draw_axes()
        self._draw_plots()
        return self.canvas

    def _draw_grid(self) -> None:
        for x in _tick_values(self.x_min, self.x_max):
            p0 = self.to_pixel(x, self.y_min)
            p1 = self.to_pixel(x, self.y_max)
            self.canvas.line(p0[0], p0[1], p1[0], p1[1], self.grid_color, self.grid_thickness)
        for y in _tick_values(self.y_min, self.y_max):
            p0 = self.to_pixel(self.x_min, y)
            p1 = self.to_pixel(self.x_max, y)
            self.canvas.line(p0[0], p0[1], p1[0], p1[1], self.grid_color, self.grid_thickness)

    def _draw_axes(self) -> None:
        if self.x_min <= 0 <= self.x_max:
            p0 = self.to_pixel(0, self.y_min)
            p1 = self.to_pixel(0, self.y_max)
            self.canvas.line(p0[0], p0[1], p1[0], p1[1], self.axis_color, self.axis_thickness)
        if self.y_min <= 0 <= self.y_max:
            p0 = self.to_pixel(self.x_min, 0)
            p1 = self.to_pixel(self.x_max, 0)
            self.canvas.line(p0[0], p0[1], p1[0], p1[1], self.axis_color, self.axis_thickness)

    def _draw_plots(self) -> None:
        for plot in self.plots:
            fn = _coerce_function(plot.fn)
            samples = max(2, int(plot.samples or self.samples))
            thickness = plot.thickness if plot.thickness is not None else self.plot_thickness
            current: list[Point] = []
            for x, y in self._sample(fn, self.x_min, self.x_max, samples):
                if y is None:
                    if len(current) >= 2:
                        self.canvas.polyline(current, plot.color, thickness)
                    current = []
                    continue
                current.append(self.to_pixel(x, y))
            if len(current) >= 2:
                self.canvas.polyline(current, plot.color, thickness)

    def _draw_shadings(self) -> None:
        for region in self.shadings:
            upper_fn = _coerce_function(region.upper)
            lower_fn = _coerce_function(region.lower) if isinstance(region.lower, str) else None
            x_min = self.x_min if region.x_min is None else max(self.x_min, region.x_min)
            x_max = self.x_max if region.x_max is None else min(self.x_max, region.x_max)
            if x_min >= x_max:
                continue
            samples = max(2, int(region.samples or self.samples))
            top: list[Point] = []
            bottom: list[Point] = []
            for i in range(samples):
                x = x_min + (x_max - x_min) * i / max(1, samples - 1)
                y_top = _safe_eval(upper_fn, x)
                if y_top is None:
                    continue
                if lower_fn is not None:
                    y_bottom = _safe_eval(lower_fn, x)
                    if y_bottom is None:
                        continue
                else:
                    y_bottom = float(region.lower)
                top.append(self.to_pixel(x, _clamp_float(y_top, self.y_min, self.y_max)))
                bottom.append(self.to_pixel(x, _clamp_float(y_bottom, self.y_min, self.y_max)))
            if len(top) >= 2 and len(bottom) >= 2:
                thickness = region.thickness if region.thickness is not None else self.shading_thickness
                self.canvas.area(
                    [*top, *reversed(bottom)],
                    color=region.color,
                    fill=region.color,
                    thickness=thickness,
                )

    def _sample(
        self,
        fn: Callable[[float], float],
        x_min: float,
        x_max: float,
        samples: int,
    ) -> Iterable[tuple[float, float | None]]:
        for i in range(samples):
            x = x_min + (x_max - x_min) * i / max(1, samples - 1)
            y = _safe_eval(fn, x)
            if y is None or y < self.y_min or y > self.y_max:
                yield x, None
            else:
                yield x, y


def _safe_eval(fn: Callable[[float], float], x: float) -> float | None:
    try:
        y = float(fn(x))
    except (ArithmeticError, ValueError, OverflowError):
        return None
    if not math.isfinite(y):
        return None
    return y


def _clamp_float(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


def _tick_values(lo: float, hi: float, target_count: int = 8) -> list[float]:
    span = abs(hi - lo)
    if span <= 0:
        return []
    raw = span / max(1, target_count)
    magnitude = 10 ** math.floor(math.log10(raw))
    multiplier = raw / magnitude
    if multiplier <= 1:
        nice = 1
    elif multiplier <= 2:
        nice = 2
    elif multiplier <= 5:
        nice = 5
    else:
        nice = 10
    step = nice * magnitude
    start = math.ceil(lo / step) * step
    values: list[float] = []
    value = start
    while value <= hi + step * 0.001:
        values.append(value)
        value += step
    return values
