"""Markdown -> Slide IR conversion.

Phase 2 rules:
  * Slide breaks: thematic break (`---`) ONLY.
  * H1 (`#`) on its own slide -> section-title slide (centered, large).
  * H2 (`##`) -> page title (top-left, large, accent underline).
  * Paragraphs, bullet/numbered lists, and fenced code blocks are captured.
  * Inline styling is fully parsed into TextRun lists:
      **bold**, *italic*, `code`, [link](url)

Phase 5 additions:
  * Block math ``$$...$$`` -> MathBlock IR node.
  * Inline math ``$...$`` -> TextRun(math=True) with raw expr in .text.
"""

from __future__ import annotations

import shlex
from typing import List, Literal, Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

from .canvas import Canvas, Graph, UnsafeExpressionError
from .ir import Block, BoxBlock, CanvasBlock, CodeBlock, ColumnBreak, Heading, ImageBlock, ListBlock, MathBlock, Paragraph, Slide, SpriteBlock, TableBlock, TextRun


# --------------------------------------------------------------------------- #
# SpriteBlock key=value parser
# --------------------------------------------------------------------------- #

def _parse_sprite_block(content: str) -> SpriteBlock:
    """Parse ``key=value`` lines from a ``pyxel-sprite`` fence body.

    Unknown keys are silently ignored.  Values that cannot be coerced to
    the expected type are also silently ignored (field default is kept).
    """
    fields: dict = {}
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        try:
            if key in ("img", "u", "v", "w", "h", "colkey", "frames", "frame_w", "anim_fps"):
                fields[key] = int(val)
            elif key == "scale":
                fields[key] = float(val)
        except ValueError:
            pass  # ignore bad values
    return SpriteBlock(**fields)


# --------------------------------------------------------------------------- #
# Canvas / Graph fenced block parsers
# --------------------------------------------------------------------------- #

def _parse_bool(value: str, default: bool = False) -> bool:
    val = value.strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


def _parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_pair(value: str, default: tuple[float, float]) -> tuple[float, float]:
    if "," not in value:
        return default
    left, _, right = value.partition(",")
    return _parse_float(left, default[0]), _parse_float(right, default[1])


def _parse_align(value: str) -> Literal["left", "center", "right"]:
    if value in ("left", "center", "right"):
        return value
    return "center"


def _split_command_options(tokens: list[str]) -> tuple[list[str], dict[str, str]]:
    args: list[str] = []
    options: dict[str, str] = {}
    for token in tokens:
        if "=" in token:
            key, _, value = token.partition("=")
            options[key.strip().lower().replace("-", "_")] = value.strip()
        else:
            args.append(token)
    return args, options


def _parse_point_tokens(tokens: list[str]) -> list[tuple[float, float]]:
    numbers: list[float] = []
    for token in tokens:
        if "," in token:
            left, _, right = token.partition(",")
            numbers.append(_parse_float(left))
            numbers.append(_parse_float(right))
        else:
            numbers.append(_parse_float(token))
    points: list[tuple[float, float]] = []
    for i in range(0, len(numbers) - 1, 2):
        points.append((numbers[i], numbers[i + 1]))
    return points


def _parse_fill_option(value: Optional[str], color: int) -> bool | int | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in ("", "none", "false", "no", "off"):
        return None
    if lowered in ("true", "yes", "on", "fill"):
        return True
    return _parse_int(value, color)


def _iter_directive_lines(content: str):
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            tokens = shlex.split(line)
        except ValueError:
            continue
        if tokens:
            yield tokens


def _parse_canvas_block(content: str, step: int = 1) -> CanvasBlock:
    """Parse a ``pyxel-canvas`` fence into a CanvasBlock.

    Supported command examples:
      ``point 12 10 color=2 size=2``
      ``line 0 0 80 40 color=2``
      ``curve 5,50 40,5 75,50 color=4 steps=32``
      ``area 10,30 30,10 50,30 fill=12 color=2``
      ``text 8 8 "hello" color=1``
    """

    canvas_kwargs: dict = {}
    scale = 1.0
    align: Literal["left", "center", "right"] = "center"
    pending_commands: list[list[str]] = []

    for tokens in _iter_directive_lines(content):
        if len(tokens) == 1 and "=" in tokens[0]:
            key, _, value = tokens[0].partition("=")
            key = key.strip().lower().replace("-", "_")
            value = value.strip()
            if key in ("width", "w"):
                canvas_kwargs["width"] = _parse_int(value, 240)
            elif key in ("height", "h"):
                canvas_kwargs["height"] = _parse_int(value, 120)
            elif key in ("bg", "background"):
                canvas_kwargs["bg"] = _parse_int(value, 0)
            elif key == "border":
                canvas_kwargs["border"] = _parse_int(value, -1)
            elif key == "scale":
                scale = max(0.1, _parse_float(value, 1.0))
            elif key == "align":
                align = _parse_align(value)
            continue
        pending_commands.append(tokens)

    canvas = Canvas(**canvas_kwargs)

    for tokens in pending_commands:
        verb = tokens[0].strip().lower().replace("-", "_")
        args, opts = _split_command_options(tokens[1:])
        color = _parse_int(opts.get("color", "1"), 1)

        if verb == "point" and len(args) >= 2:
            canvas.point(
                _parse_float(args[0]),
                _parse_float(args[1]),
                color=color,
                size=_parse_int(opts.get("size", "1"), 1),
            )
        elif verb == "line" and len(args) >= 4:
            canvas.line(
                _parse_float(args[0]),
                _parse_float(args[1]),
                _parse_float(args[2]),
                _parse_float(args[3]),
                color=color,
            )
        elif verb in ("polyline", "path"):
            canvas.polyline(_parse_point_tokens(args), color=color)
        elif verb == "curve":
            canvas.curve(
                _parse_point_tokens(args),
                color=color,
                steps=_parse_int(opts.get("steps", "32"), 32),
            )
        elif verb in ("area", "polygon"):
            canvas.area(
                _parse_point_tokens(args),
                color=color,
                fill=_parse_fill_option(opts.get("fill"), color),
            )
        elif verb == "rect" and len(args) >= 4:
            canvas.rect(
                _parse_float(args[0]),
                _parse_float(args[1]),
                _parse_float(args[2]),
                _parse_float(args[3]),
                color=color,
                fill=_parse_fill_option(opts.get("fill"), color),
            )
        elif verb == "text" and len(args) >= 3:
            canvas.text(
                _parse_float(args[0]),
                _parse_float(args[1]),
                " ".join(args[2:]),
                color=color,
            )

    return CanvasBlock(canvas=canvas, scale=scale, align=align, step=step)


def _parse_graph_block(content: str, step: int = 1) -> CanvasBlock:
    """Parse a ``pyxel-graph`` fence into a CanvasBlock backed by Graph."""

    width = 240
    height = 120
    bg = 0
    border = 14
    scale = 1.0
    align: Literal["left", "center", "right"] = "center"
    x_min, x_max = -10.0, 10.0
    y_min, y_max = -10.0, 10.0
    axes = True
    grid = False
    axis_color = 3
    grid_color = 14
    samples = 160
    commands: list[list[str]] = []

    for tokens in _iter_directive_lines(content):
        if len(tokens) == 1 and "=" in tokens[0]:
            key, _, value = tokens[0].partition("=")
            key = key.strip().lower().replace("-", "_")
            value = value.strip()
            if key in ("width", "w"):
                width = _parse_int(value, width)
            elif key in ("height", "h"):
                height = _parse_int(value, height)
            elif key in ("bg", "background"):
                bg = _parse_int(value, bg)
            elif key == "border":
                border = _parse_int(value, border)
            elif key == "scale":
                scale = max(0.1, _parse_float(value, scale))
            elif key == "align":
                align = _parse_align(value)
            elif key in ("x", "x_range"):
                x_min, x_max = _parse_pair(value, (x_min, x_max))
            elif key in ("y", "y_range"):
                y_min, y_max = _parse_pair(value, (y_min, y_max))
            elif key == "x_min":
                x_min = _parse_float(value, x_min)
            elif key == "x_max":
                x_max = _parse_float(value, x_max)
            elif key == "y_min":
                y_min = _parse_float(value, y_min)
            elif key == "y_max":
                y_max = _parse_float(value, y_max)
            elif key == "axes":
                axes = _parse_bool(value, axes)
            elif key == "grid":
                grid = _parse_bool(value, grid)
            elif key == "axis_color":
                axis_color = _parse_int(value, axis_color)
            elif key == "grid_color":
                grid_color = _parse_int(value, grid_color)
            elif key == "samples":
                samples = _parse_int(value, samples)
            continue
        commands.append(tokens)

    graph = Graph(
        Canvas(width=width, height=height, bg=bg, border=border),
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        axes=axes,
        grid=grid,
        axis_color=axis_color,
        grid_color=grid_color,
        samples=samples,
    )

    for tokens in commands:
        verb = tokens[0].strip().lower().replace("-", "_")
        args, opts = _split_command_options(tokens[1:])
        color = _parse_int(opts.get("color", "2"), 2)
        expr = opts.get("expr") or " ".join(args)
        command_samples = _parse_int(opts.get("samples", str(samples)), samples)

        try:
            if verb in ("plot", "function", "f") and expr:
                graph.plot(expr, color=color, samples=command_samples)
            elif verb in ("shade", "shade_under") and expr:
                x0 = _parse_float(opts["x_min"], x_min) if "x_min" in opts else None
                x1 = _parse_float(opts["x_max"], x_max) if "x_max" in opts else None
                if "x" in opts:
                    x0, x1 = _parse_pair(opts["x"], (x_min, x_max))
                baseline: str | float
                baseline_raw = opts.get("baseline", "0")
                try:
                    baseline = float(baseline_raw)
                except ValueError:
                    baseline = baseline_raw
                graph.shade_under(
                    expr,
                    baseline=baseline,
                    color=color,
                    x_min=x0,
                    x_max=x1,
                    samples=command_samples,
                )
            elif verb in ("shade_between", "between"):
                upper = opts.get("upper")
                lower = opts.get("lower")
                if upper is None or lower is None:
                    if len(args) >= 2:
                        upper, lower = args[0], args[1]
                if upper and lower:
                    x0 = _parse_float(opts["x_min"], x_min) if "x_min" in opts else None
                    x1 = _parse_float(opts["x_max"], x_max) if "x_max" in opts else None
                    if "x" in opts:
                        x0, x1 = _parse_pair(opts["x"], (x_min, x_max))
                    graph.shade_between(
                        upper,
                        lower,
                        color=color,
                        x_min=x0,
                        x_max=x1,
                        samples=command_samples,
                    )
        except (SyntaxError, UnsafeExpressionError, ValueError):
            continue

    return CanvasBlock(canvas=graph.draw(), scale=scale, align=align, step=step)


# --------------------------------------------------------------------------- #
# Inline token -> List[TextRun]
# --------------------------------------------------------------------------- #
# ==mark== inline rule for text highlighting
# --------------------------------------------------------------------------- #

def _add_mark_rule(md: MarkdownIt) -> None:
    """Register a markdown-it inline rule for ``==mark==`` highlighted text.

    Emits ``mark_open`` / ``mark_close`` tokens and re-tokenizes the inner
    content, so nested bold/italic/underline all work inside ``==...==``.
    """
    def _mark(state, silent):
        pos = state.pos
        src = state.src
        if pos + 1 >= state.posMax:
            return False
        if src[pos] != '=' or src[pos + 1] != '=':
            return False
        start = pos + 2
        found = src.find("==", start)
        if found == -1 or found >= state.posMax:
            return False
        if silent:
            return True
        # Opening token.
        token = state.push("mark_open", "mark", 1)
        token.markup = "=="
        # Tokenize the content between the == delimiters.
        old_pos, old_max = state.pos, state.posMax
        state.pos = start
        state.posMax = found
        state.md.inline.tokenize(state)
        state.pos = old_pos
        state.posMax = old_max
        # Closing token.
        token = state.push("mark_close", "mark", -1)
        token.markup = "=="
        state.pos = found + 2
        return True
    md.inline.ruler.push("mark", _mark)


# --------------------------------------------------------------------------- #

def _parse_inline(token) -> List[TextRun]:
    """Parse an inline token's children into a styled TextRun list."""
    if token is None:
        return [TextRun("")]
    children = token.children or []

    runs: list[TextRun] = []
    bold = 0
    italic = 0
    highlight = 0
    underline = 0
    link_url = ""

    for child in children:
        t = child.type

        if t == "strong_open":
            bold += 1
        elif t == "strong_close":
            bold = max(0, bold - 1)
        elif t == "em_open":
            italic += 1
        elif t == "em_close":
            italic = max(0, italic - 1)
        elif t == "link_open":
            link_url = (child.attrs or {}).get("href", "")
        elif t == "link_close":
            link_url = ""
        elif t == "mark_open":
            highlight += 1
        elif t == "mark_close":
            highlight = max(0, highlight - 1)
        elif t == "text":
            runs.append(TextRun(
                text=child.content,
                bold=bold > 0,
                italic=italic > 0,
                highlight=highlight > 0,
                underline=underline > 0,
                url=link_url,
            ))
        elif t == "code_inline":
            # Check if code span contains a markdown link: [text](url)
            content = child.content
            import re
            link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', content)
            if link_match:
                # Extract link text and URL, keep the code highlighting
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                runs.append(TextRun(text=link_text, code=True, url=link_url))
            else:
                runs.append(TextRun(text=content, code=True))
        elif t == "math_inline":
            if child.content.strip():
                runs.append(TextRun(text=child.content, math=True))
        elif t == "softbreak":
            runs.append(TextRun(" ", bold=bold > 0, italic=italic > 0, highlight=highlight > 0, underline=underline > 0, url=link_url))
        elif t == "hardbreak":
            runs.append(TextRun("", bold=bold > 0, italic=italic > 0, highlight=highlight > 0, underline=underline > 0, url=link_url, newline=True))
        elif t == "html_inline":
            # Check if it's a <br> or <br/> tag (from user input)
            if "<br" in child.content:
                runs.append(TextRun("", bold=bold > 0, italic=italic > 0, highlight=highlight > 0, url=link_url, newline=True))
            elif child.content.strip().lower() == "<u>":
                underline += 1
            elif child.content.strip().lower() == "</u>":
                underline = max(0, underline - 1)
        # image / html_inline in mixed content → render alt text as plain run
        elif t == "image":
            alt = "".join(c.content for c in (child.children or []) if c.type == "text")
            if alt:
                runs.append(TextRun(alt, bold=bold > 0, italic=italic > 0, highlight=highlight > 0, underline=underline > 0, url=link_url))
        # other token types silently ignored

    return runs if runs else [TextRun("")]


def _plain_text(token) -> str:
    """Flatten an inline token to plain text (used for headings)."""
    parts: list[str] = []
    for run in _parse_inline(token):
        if run.newline:
            parts.append("\n")
        parts.append(run.text)
    return "".join(parts)


def _extract_image(inline_token) -> Optional[tuple[str, str, float]]:
    """If the inline consists solely of one image, return (src, alt, scale). Else None."""
    if inline_token is None:
        return None
    # Strip whitespace/softbreak tokens to find the meaningful children.
    meaningful = [
        c for c in (inline_token.children or [])
        if c.type not in ("softbreak", "hardbreak")
        and not (c.type == "text" and not c.content.strip())
    ]
    if len(meaningful) == 1 and meaningful[0].type == "image":
        img = meaningful[0]
        src = (img.attrs or {}).get("src", "")
        alt = "".join(c.content for c in (img.children or []) if c.type == "text")
        
        # Parse scale from URL query parameter (e.g., path?scale=0.5)
        scale = 1.0
        if "?" in src:
            base_url, query = src.split("?", 1)
            src = base_url
            for param in query.split("&"):
                if "=" in param:
                    key, val = param.split("=", 1)
                    if key.strip() == "scale":
                        try:
                            scale = float(val.strip())
                        except ValueError:
                            scale = 1.0
        
        return src, alt, scale
    return None


# --------------------------------------------------------------------------- #
# Main parser
# --------------------------------------------------------------------------- #

def parse_markdown(source: str) -> List[Slide]:
    md = MarkdownIt("commonmark", {"breaks": True})
    md.enable("table")
    dollarmath_plugin(md, allow_labels=False, allow_digits=False)
    _add_mark_rule(md)  # enable ==mark== highlighting syntax
    tokens = md.parse(source)

    slides: List[Slide] = []
    current = Slide(blocks=[])
    current_step = 1  # Track current step number for progressive display

    def flush_slide() -> None:
        nonlocal current, current_step
        if current.blocks:
            slides.append(current)
        current = Slide(blocks=[])
        current_step = 1

    source_lines = source.splitlines()

    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        ttype = tok.type

        # Debug: print token type and content
        if tok.content and ("step" in tok.content.lower() or "<!--" in tok.content):
            print(f"[DEBUG] Token: {ttype}, content: {tok.content[:100]}")

        if ttype == "hr":
            flush_slide()
            i += 1
            continue

        if ttype == "html_block":
            import re
            content = tok.content
            if re.search(r'<!--\s*(?:step|incremental)\s*-->', content, re.IGNORECASE):
                current_step += 1
            i += 1
            continue

        if ttype in ("math_block", "math_block_label"):
            expr = tok.content.strip()
            if expr:
                current.blocks.append(MathBlock(expr=expr, step=current_step))
            i += 1
            continue

        if ttype == "heading_open":
            level = int(tok.tag[1])  # 'h1' -> 1
            inline = tokens[i + 1] if i + 1 < n else None
            text = _plain_text(inline).strip()
            current.blocks.append(Heading(level=level, text=text, step=current_step))  # type: ignore[arg-type]
            i += 3  # heading_open, inline, heading_close
            continue

        if ttype == "paragraph_open":
            inline = tokens[i + 1] if i + 1 < n else None
            # Check if this paragraph contains step marker
            if inline and inline.type == "inline":
                import re
                if re.search(r'<!--\s*step\s*-->', inline.content, re.IGNORECASE):
                    # Increment step counter
                    current_step += 1
                    print(f"[DEBUG] Step marker found, current_step now = {current_step}")
                    i += 3
                    continue
                if re.search(r'<!--\s*incremental\s*-->', inline.content, re.IGNORECASE):
                    current_step += 1
                    i += 3
                    continue
                # Check if this paragraph contains col_widths= pattern (table metadata)
                if re.search(r'col_widths\s*=\s*(\d+(?:,\s*\d+)*)', inline.content):
                    # This is a table metadata paragraph - skip it
                    # The table parser will handle extracting the widths
                    i += 3
                    continue
            
            # Detect image-only paragraph → emit ImageBlock.
            img = _extract_image(inline)
            if img is not None:
                src, alt, scale = img
                print(f"[DEBUG] ImageBlock created with step={current_step}")
                current.blocks.append(ImageBlock(path=src, alt=alt, scale=scale, step=current_step))
            else:
                runs = _parse_inline(inline)
                # Strip leading/trailing whitespace from first/last run.
                if runs:
                    runs[0] = TextRun(
                        text=runs[0].text.lstrip(),
                        bold=runs[0].bold, italic=runs[0].italic,
                        highlight=runs[0].highlight, code=runs[0].code, url=runs[0].url,
                        underline=runs[0].underline,
                    )
                    runs[-1] = TextRun(
                        text=runs[-1].text.rstrip(),
                        bold=runs[-1].bold, italic=runs[-1].italic,
                        highlight=runs[-1].highlight, code=runs[-1].code, url=runs[-1].url,
                        underline=runs[-1].underline,
                    )
                # Filter out empty-text runs, but keep newline-only runs (<br/>).
                runs = [r for r in runs if r.text or r.newline]
                if runs:
                    # A paragraph whose sole text is "|||" becomes a ColumnBreak.
                    if len(runs) == 1 and runs[0].text == "|||":
                        current.blocks.append(ColumnBreak())
                    else:
                        print(f"[DEBUG] Paragraph created with step={current_step}")
                        current.blocks.append(Paragraph(runs=runs, step=current_step))
            i += 3
            continue

        if ttype in ("bullet_list_open", "ordered_list_open"):
            ordered = ttype == "ordered_list_open"

            # Starting number for ordered lists (e.g. "2. item" → start=2).
            start = 1
            if ordered:
                try:
                    start = int((tok.attrs or {}).get("start", 1))
                except (ValueError, TypeError):
                    start = 1

            # Derive indentation depth from how many spaces precede the list
            # marker in the source.  Handles the case where <!-- incremental -->
            # at column 0 breaks a list so that "  - sub item" becomes its own
            # top-level ListBlock but should still render indented.
            base_depth = 0
            if tok.map is not None:
                line_idx = tok.map[0]
                if 0 <= line_idx < len(source_lines):
                    raw = source_lines[line_idx]
                    leading = len(raw) - len(raw.lstrip())
                    base_depth = leading // 2

            items: list[list[TextRun]] = []
            depths: list[int] = []
            j = i + 1
            depth = 1
            while j < n and depth > 0:
                t = tokens[j]
                if t.type in ("bullet_list_open", "ordered_list_open"):
                    depth += 1
                elif t.type in ("bullet_list_close", "ordered_list_close"):
                    depth -= 1
                    if depth == 0:
                        break
                elif t.type == "inline":
                    item_runs = _parse_inline(t)
                    item_runs = [r for r in item_runs if r.text or r.newline]
                    items.append(item_runs if item_runs else [TextRun("")])
                    depths.append(base_depth + depth - 1)
                j += 1
            current.blocks.append(ListBlock(items=items, ordered=ordered, step=current_step, start=start, depths=depths))
            i = j + 1
            continue

        if ttype == "blockquote_open":
            # Collect all inline content from within the blockquote.
            collected_runs: List[TextRun] = []
            j = i + 1
            while j < n and tokens[j].type != "blockquote_close":
                inner = tokens[j]
                if inner.type == "inline":
                    collected_runs.extend(_parse_inline(inner))
                j += 1
            # Trim leading/trailing whitespace (same as paragraph handling).
            if collected_runs:
                collected_runs[0] = TextRun(
                    text=collected_runs[0].text.lstrip(),
                    bold=collected_runs[0].bold, italic=collected_runs[0].italic,
                    highlight=collected_runs[0].highlight, code=collected_runs[0].code,
                    url=collected_runs[0].url, underline=collected_runs[0].underline,
                )
                collected_runs[-1] = TextRun(
                    text=collected_runs[-1].text.rstrip(),
                    bold=collected_runs[-1].bold, italic=collected_runs[-1].italic,
                    highlight=collected_runs[-1].highlight, code=collected_runs[-1].code,
                    url=collected_runs[-1].url, underline=collected_runs[-1].underline,
                )
            collected_runs = [r for r in collected_runs if r.text or r.newline]
            if collected_runs:
                current.blocks.append(BoxBlock(runs=collected_runs, step=current_step))
            i = j + 1
            continue

        if ttype == "fence":
            import re as _re
            info = (tok.info or "").strip()
            info_parts = info.split() if info else []
            lang = info_parts[0] if info_parts else ""
            highlight_lines: List[int] = []
            for _part in info_parts[1:]:
                _m = _re.match(r'(?:hl|highlight)=(.+)', _part)
                if _m:
                    try:
                        highlight_lines = [int(x.strip()) for x in _m.group(1).split(",") if x.strip()]
                    except ValueError:
                        highlight_lines = []
                    break
            if lang == "pyxel-sprite":
                current.blocks.append(_parse_sprite_block(tok.content))
            elif lang in ("pyxel-canvas", "canvas"):
                current.blocks.append(_parse_canvas_block(tok.content, step=current_step))
            elif lang in ("pyxel-graph", "graph"):
                current.blocks.append(_parse_graph_block(tok.content, step=current_step))
            else:
                current.blocks.append(
                    CodeBlock(code=tok.content.rstrip("\n"), language=lang,
                              step=current_step, highlight_lines=highlight_lines)
                )
            i += 1
            continue

        if ttype == "table_open":
            # Parse GFM table tokens into TableBlock.
            headers: list[str] = []
            rows: list[list[str]] = []
            col_widths: list[int] = []
            in_head = False
            cur_row: list[str] = []
            j = i + 1
            while j < n:
                t = tokens[j]
                if t.type == "table_close":
                    break
                elif t.type == "thead_open":
                    in_head = True
                elif t.type == "thead_close":
                    in_head = False
                elif t.type == "tr_open":
                    cur_row = []
                elif t.type == "tr_close":
                    if in_head:
                        headers = cur_row[:]
                    else:
                        rows.append(cur_row[:])
                    cur_row = []
                elif t.type == "inline":
                    cur_row.append(t.content.strip())
                j += 1
            
            # Check for column widths in the last paragraph block (before this table)
            if current.blocks and isinstance(current.blocks[-1], Paragraph):
                import re
                last_para_text = "".join(r.text for r in current.blocks[-1].runs)
                match = re.search(r'col_widths\s*=\s*(\d+(?:,\s*\d+)*)', last_para_text)
                if match:
                    try:
                        col_widths = [int(w.strip()) for w in match.group(1).split(',')]
                        # Remove the paragraph block since it's just metadata
                        current.blocks.pop()
                    except ValueError:
                        col_widths = []
            
            if headers:
                # Only include col_widths if at least one width was specified and matches column count
                final_col_widths = col_widths if col_widths and len(col_widths) == len(headers) else None
                current.blocks.append(TableBlock(headers=headers, rows=rows, col_widths=final_col_widths, step=current_step))
            i = j + 1
            continue

        if ttype == "code_block":  # indented code
            current.blocks.append(CodeBlock(code=tok.content.rstrip("\n"), language="", step=current_step))
            i += 1
            continue

        i += 1  # unknown token — skip

    flush_slide()
    return slides
