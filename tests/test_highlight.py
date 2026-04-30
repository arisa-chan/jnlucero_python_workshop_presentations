"""Unit tests for pyxel_slides.highlight — pure logic, no Pyxel required."""

import pytest

from pyxel_slides.highlight import (
    ROLE_BUILTIN,
    ROLE_COMMENT,
    ROLE_DEFAULT,
    ROLE_KEYWORD,
    ROLE_NUMBER,
    ROLE_STRING,
    _token_role,
    pygments_available,
    role_to_color,
    tokenize_lines,
)


# --------------------------------------------------------------------------- #
# _token_role string matching
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("tstr,expected", [
    ("Token.Keyword",                     ROLE_KEYWORD),
    ("Token.Keyword.Declaration",         ROLE_KEYWORD),
    ("Token.Keyword.Reserved",            ROLE_KEYWORD),
    ("Token.Comment",                     ROLE_COMMENT),
    ("Token.Comment.Single",              ROLE_COMMENT),
    ("Token.Comment.Multiline",           ROLE_COMMENT),
    ("Token.Literal.String",              ROLE_STRING),
    ("Token.Literal.String.Single",       ROLE_STRING),
    ("Token.Literal.String.Double",       ROLE_STRING),
    ("Token.Literal.Scalar",              ROLE_STRING),
    ("Token.Literal.Number",              ROLE_NUMBER),
    ("Token.Literal.Number.Integer",      ROLE_NUMBER),
    ("Token.Literal.Number.Float",        ROLE_NUMBER),
    ("Token.Name.Builtin",                ROLE_BUILTIN),
    ("Token.Name.Builtin.Pseudo",         ROLE_BUILTIN),
    ("Token.Name.Exception",              ROLE_BUILTIN),
    ("Token.Name.Class",                  ROLE_BUILTIN),
    ("Token.Name.Decorator",              ROLE_BUILTIN),
    ("Token.Name",                        ROLE_DEFAULT),
    ("Token.Operator",                    ROLE_DEFAULT),
    ("Token.Punctuation",                 ROLE_DEFAULT),
    ("Token.Text",                        ROLE_DEFAULT),
    ("Token.Text.Whitespace",             ROLE_DEFAULT),
])
def test_token_role_mapping(tstr, expected):
    assert _token_role(tstr) == expected


# --------------------------------------------------------------------------- #
# role_to_color — uses a mock theme object
# --------------------------------------------------------------------------- #

class _FakeTheme:
    bg = 10
    fg = 11
    accent = 12
    muted = 13
    # Extended syntax colour properties expected by role_to_color
    eff_keyword  = 20
    eff_string   = 21
    eff_comment  = 22
    eff_number   = 23
    eff_builtin  = 24
    eff_code_fg  = 25


_THEME = _FakeTheme()


@pytest.mark.parametrize("role,expected_attr", [
    (ROLE_DEFAULT, "eff_code_fg"),
    (ROLE_BUILTIN, "eff_builtin"),
    (ROLE_KEYWORD, "eff_keyword"),
    (ROLE_NUMBER,  "eff_number"),
    (ROLE_STRING,  "eff_string"),
    (ROLE_COMMENT, "eff_comment"),
])
def test_role_to_color(role, expected_attr):
    assert role_to_color(role, _THEME) == getattr(_THEME, expected_attr)


# --------------------------------------------------------------------------- #
# tokenize_lines — structure
# --------------------------------------------------------------------------- #

def test_tokenize_plain_text_fallback():
    """Non-empty language with no Pygments → plain default spans."""
    if pygments_available():
        pytest.skip("Pygments installed; fallback not triggered.")
    lines = tokenize_lines("x = 1\n# comment\n", "python")
    all_roles = {role for line in lines for _, role in line}
    assert all_roles == {ROLE_DEFAULT}


def test_tokenize_returns_correct_line_count():
    code = "def foo():\n    return 42\n"
    lines = tokenize_lines(code, "python")
    # Two non-empty lines of code → 2 lines
    assert len(lines) == 2


def test_tokenize_empty_code():
    lines = tokenize_lines("", "python")
    assert isinstance(lines, list)
    # Should not raise; returns at least one (possibly empty) line.
    assert len(lines) >= 1


def test_tokenize_single_line_no_newline():
    code = "x = 42"
    lines = tokenize_lines(code, "python")
    assert len(lines) == 1
    full = "".join(t for t, _ in lines[0])
    assert "x" in full
    assert "42" in full


def test_tokenize_unknown_language_fallback():
    code = "this is not a language"
    lines = tokenize_lines(code, "thislanguagedoesnotexist12345")
    assert isinstance(lines, list)
    assert len(lines) >= 1


@pytest.mark.skipif(not pygments_available(), reason="Pygments not installed")
def test_tokenize_python_has_keyword():
    code = "def hello():\n    pass\n"
    lines = tokenize_lines(code, "python")
    all_pairs = [(t, r) for line in lines for t, r in line]
    keyword_texts = [t for t, r in all_pairs if r == ROLE_KEYWORD]
    # "def" should be classified as a keyword.
    assert any("def" in kw for kw in keyword_texts), f"No keywords in {all_pairs}"


@pytest.mark.skipif(not pygments_available(), reason="Pygments not installed")
def test_tokenize_python_has_comment():
    code = "x = 1  # a comment\n"
    lines = tokenize_lines(code, "python")
    all_pairs = [(t, r) for line in lines for t, r in line]
    comment_roles = [r for t, r in all_pairs if r == ROLE_COMMENT]
    assert comment_roles, f"No comment tokens in {all_pairs}"


@pytest.mark.skipif(not pygments_available(), reason="Pygments not installed")
def test_tokenize_python_has_string():
    code = 'greeting = "hello"\n'
    lines = tokenize_lines(code, "python")
    all_pairs = [(t, r) for line in lines for t, r in line]
    string_roles = [r for _, r in all_pairs if r == ROLE_STRING]
    assert string_roles, f"No string tokens in {all_pairs}"


@pytest.mark.skipif(not pygments_available(), reason="Pygments not installed")
def test_tokenize_python_has_number():
    code = "n = 42\n"
    lines = tokenize_lines(code, "python")
    all_pairs = [(t, r) for line in lines for t, r in line]
    number_roles = [r for _, r in all_pairs if r == ROLE_NUMBER]
    assert number_roles, f"No number tokens in {all_pairs}"


@pytest.mark.skipif(not pygments_available(), reason="Pygments not installed")
def test_tokenize_text_preservation():
    """All characters from the original code appear in the token stream."""
    code = "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\n"
    lines = tokenize_lines(code, "python")
    reconstructed = "\n".join("".join(t for t, _ in line) for line in lines)
    # Strip trailing newlines for comparison.
    assert reconstructed.rstrip() == code.rstrip()
