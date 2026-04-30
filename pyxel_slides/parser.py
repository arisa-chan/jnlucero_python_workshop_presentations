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

from typing import List, Optional

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

from .ir import Block, CodeBlock, Heading, ImageBlock, ListBlock, MathBlock, Paragraph, Slide, SpriteBlock, TextRun


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
# Inline token -> List[TextRun]
# --------------------------------------------------------------------------- #

def _parse_inline(token) -> List[TextRun]:
    """Parse an inline token's children into a styled TextRun list."""
    if token is None:
        return [TextRun("")]
    children = token.children or []

    runs: list[TextRun] = []
    bold = 0
    italic = 0
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
        elif t == "text":
            runs.append(TextRun(
                text=child.content,
                bold=bold > 0,
                italic=italic > 0,
                url=link_url,
            ))
        elif t == "code_inline":
            runs.append(TextRun(text=child.content, code=True))
        elif t == "math_inline":
            if child.content.strip():
                runs.append(TextRun(text=child.content, math=True))
        elif t == "softbreak":
            runs.append(TextRun(" ", bold=bold > 0, italic=italic > 0, url=link_url))
        elif t == "hardbreak":
            runs.append(TextRun("\n", bold=bold > 0, italic=italic > 0, url=link_url))
        # image / html_inline in mixed content → render alt text as plain run
        elif t == "image":
            alt = "".join(c.content for c in (child.children or []) if c.type == "text")
            if alt:
                runs.append(TextRun(alt, bold=bold > 0, italic=italic > 0, url=link_url))
        # other token types silently ignored

    return runs if runs else [TextRun("")]


def _plain_text(token) -> str:
    """Flatten an inline token to plain text (used for headings)."""
    return "".join(r.text for r in _parse_inline(token))


def _extract_image(inline_token) -> Optional[tuple[str, str]]:
    """If the inline consists solely of one image, return (src, alt). Else None."""
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
        return src, alt
    return None


# --------------------------------------------------------------------------- #
# Main parser
# --------------------------------------------------------------------------- #

def parse_markdown(source: str) -> List[Slide]:
    md = MarkdownIt("commonmark")
    dollarmath_plugin(md, allow_labels=False, allow_digits=False)
    tokens = md.parse(source)

    slides: List[Slide] = []
    current = Slide()

    def flush_slide() -> None:
        nonlocal current
        if current.blocks:
            slides.append(current)
        current = Slide()

    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        ttype = tok.type

        if ttype == "hr":
            flush_slide()
            i += 1
            continue

        if ttype in ("math_block", "math_block_label"):
            expr = tok.content.strip()
            if expr:
                current.blocks.append(MathBlock(expr=expr))
            i += 1
            continue

        if ttype == "heading_open":
            level = int(tok.tag[1])  # 'h1' -> 1
            inline = tokens[i + 1] if i + 1 < n else None
            text = _plain_text(inline).strip()
            current.blocks.append(Heading(level=level, text=text))  # type: ignore[arg-type]
            i += 3  # heading_open, inline, heading_close
            continue

        if ttype == "paragraph_open":
            inline = tokens[i + 1] if i + 1 < n else None
            # Detect image-only paragraph → emit ImageBlock.
            img = _extract_image(inline)
            if img is not None:
                src, alt = img
                current.blocks.append(ImageBlock(path=src, alt=alt))
            else:
                runs = _parse_inline(inline)
                # Strip leading/trailing whitespace from first/last run.
                if runs:
                    runs[0] = TextRun(
                        text=runs[0].text.lstrip(),
                        bold=runs[0].bold, italic=runs[0].italic,
                        highlight=runs[0].highlight, code=runs[0].code, url=runs[0].url,
                    )
                    runs[-1] = TextRun(
                        text=runs[-1].text.rstrip(),
                        bold=runs[-1].bold, italic=runs[-1].italic,
                        highlight=runs[-1].highlight, code=runs[-1].code, url=runs[-1].url,
                    )
                # Filter out empty-text runs at start/end.
                runs = [r for r in runs if r.text]
                if runs:
                    current.blocks.append(Paragraph(runs=runs))
            i += 3
            continue

        if ttype in ("bullet_list_open", "ordered_list_open"):
            ordered = ttype == "ordered_list_open"
            items: list[list[TextRun]] = []
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
                elif t.type == "inline" and depth == 1:
                    item_runs = _parse_inline(t)
                    item_runs = [r for r in item_runs if r.text]
                    items.append(item_runs if item_runs else [TextRun("")])
                j += 1
            current.blocks.append(ListBlock(items=items, ordered=ordered))
            i = j + 1
            continue

        if ttype == "fence":
            lang = (tok.info or "").strip()
            if lang == "pyxel-sprite":
                current.blocks.append(_parse_sprite_block(tok.content))
            else:
                current.blocks.append(
                    CodeBlock(code=tok.content.rstrip("\n"), language=lang)
                )
            i += 1
            continue

        if ttype == "code_block":  # indented code
            current.blocks.append(CodeBlock(code=tok.content.rstrip("\n"), language=""))
            i += 1
            continue

        i += 1  # unknown token — skip

    flush_slide()
    return slides
