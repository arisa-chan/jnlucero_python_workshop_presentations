from pyxel_slides.parser import parse_markdown
from pyxel_slides.ir import CodeBlock, ColumnBreak, Heading, ImageBlock, ListBlock, Paragraph, TextRun


def test_slide_breaks_on_hr_only():
    md = "# Intro\n\n## Not a break\n\n---\n\n## Page two\n"
    slides = parse_markdown(md)
    assert len(slides) == 2
    assert isinstance(slides[0].blocks[0], Heading)
    assert slides[0].blocks[0].level == 1
    assert slides[0].blocks[0].text == "Intro"
    assert isinstance(slides[0].blocks[1], Heading)
    assert slides[0].blocks[1].level == 2
    assert slides[1].blocks[0].text == "Page two"


def test_section_title_detection():
    md = "# Big Title\n\nSome subtitle\n"
    slides = parse_markdown(md)
    assert len(slides) == 1
    assert slides[0].is_section_title
    assert slides[0].title == "Big Title"


def test_section_title_detection_allows_leading_logo():
    md = "![Logo](logo.png?scale=0.5)\n\n# Big Title\n\nSome subtitle\n"
    slides = parse_markdown(md)
    assert len(slides) == 1
    assert isinstance(slides[0].blocks[0], ImageBlock)
    assert slides[0].is_section_title
    assert slides[0].title == "Big Title"


def test_heading_br_preserved_for_h1_h2_h3():
    md = "# Big<br/>Title\n\n## Page<br>Title\n\n### Small<br />Heading\n"
    slides = parse_markdown(md)
    blocks = slides[0].blocks
    assert isinstance(blocks[0], Heading)
    assert blocks[0].text == "Big\nTitle"
    assert isinstance(blocks[1], Heading)
    assert blocks[1].text == "Page\nTitle"
    assert isinstance(blocks[2], Heading)
    assert blocks[2].text == "Small\nHeading"


def test_paragraph_runs_plain():
    md = "## Topic\n\nHello world.\n\n- one\n- two\n- three\n"
    slides = parse_markdown(md)
    blocks = slides[0].blocks
    assert isinstance(blocks[0], Heading) and blocks[0].level == 2
    assert isinstance(blocks[1], Paragraph)
    assert blocks[1].text == "Hello world."
    # Plain paragraph = single TextRun with no styling.
    assert len(blocks[1].runs) == 1
    assert blocks[1].runs[0].is_plain
    # List items are now List[List[TextRun]].
    assert isinstance(blocks[2], ListBlock)
    item_texts = ["".join(r.text for r in item) for item in blocks[2].items]
    assert item_texts == ["one", "two", "three"]
    assert blocks[2].ordered is False


def test_ordered_list_and_code_block():
    md = "1. first\n2. second\n\n```python\nprint('hi')\n```\n"
    slides = parse_markdown(md)
    blocks = slides[0].blocks
    assert isinstance(blocks[0], ListBlock) and blocks[0].ordered
    item_texts = ["".join(r.text for r in item) for item in blocks[0].items]
    assert item_texts == ["first", "second"]
    assert isinstance(blocks[1], CodeBlock)
    assert blocks[1].language == "python"
    assert blocks[1].code == "print('hi')"


def test_bold_preserved():
    md = "This is **bold** text.\n"
    slides = parse_markdown(md)
    p = slides[0].blocks[0]
    assert isinstance(p, Paragraph)
    bold_runs = [r for r in p.runs if r.bold]
    assert len(bold_runs) == 1
    assert bold_runs[0].text == "bold"


def test_italic_preserved():
    md = "This is *italic* text.\n"
    slides = parse_markdown(md)
    p = slides[0].blocks[0]
    assert isinstance(p, Paragraph)
    italic_runs = [r for r in p.runs if r.italic]
    assert len(italic_runs) == 1
    assert italic_runs[0].text == "italic"


def test_inline_code_preserved():
    md = "Use `pyxel.text()` to draw.\n"
    slides = parse_markdown(md)
    p = slides[0].blocks[0]
    code_runs = [r for r in p.runs if r.code]
    assert len(code_runs) == 1
    assert code_runs[0].text == "pyxel.text()"


def test_link_url_preserved():
    md = "See [Pyxel](https://github.com/kitao/pyxel) for docs.\n"
    slides = parse_markdown(md)
    p = slides[0].blocks[0]
    link_runs = [r for r in p.runs if r.url]
    assert len(link_runs) == 1
    assert link_runs[0].text == "Pyxel"
    assert link_runs[0].url == "https://github.com/kitao/pyxel"


def test_combined_inline_styles():
    md = "Here is **bold**, *italic*, `code`, and [link](https://x.com).\n"
    slides = parse_markdown(md)
    p = slides[0].blocks[0]
    assert isinstance(p, Paragraph)
    full_text = p.text
    assert "bold" in full_text
    assert "italic" in full_text
    assert "code" in full_text
    assert "link" in full_text
    # Verify correct run types.
    assert any(r.bold for r in p.runs)
    assert any(r.italic for r in p.runs)
    assert any(r.code for r in p.runs)
    assert any(r.url for r in p.runs)


def test_body_char_count():
    md = "## Title\n\nHello world!\n\n- item a\n- item b\n"
    slides = parse_markdown(md)
    s = slides[0]
    # Heading chars are NOT counted (only Paragraph + ListBlock).
    # "Hello world!" = 12, "item a" = 6, "item b" = 6 → total 24
    assert s.body_char_count() == 24


def test_column_break_parsed():
    md = "## Two Columns\n\nLeft text\n\n|||\n\nRight text\n"
    slides = parse_markdown(md)
    assert len(slides) == 1
    blocks = slides[0].blocks
    assert isinstance(blocks[0], Heading)
    assert isinstance(blocks[1], Paragraph) and blocks[1].text == "Left text"
    assert isinstance(blocks[2], ColumnBreak)
    assert isinstance(blocks[3], Paragraph) and blocks[3].text == "Right text"
    assert slides[0].two_column is True


def test_column_break_not_in_plain_slide():
    md = "## Normal Slide\n\nJust a paragraph.\n"
    slides = parse_markdown(md)
    assert slides[0].two_column is False


def test_pipe_text_not_column_break():
    md = "a || b\n"
    slides = parse_markdown(md)
    assert slides[0].two_column is False
    assert isinstance(slides[0].blocks[0], Paragraph)


def test_body_char_count_ignores_column_break():
    md = "Left\n\n|||\n\nRight\n"
    slides = parse_markdown(md)
    # "Left" = 4, "Right" = 5 → total 9 (ColumnBreak contributes 0)
    assert slides[0].body_char_count() == 9
