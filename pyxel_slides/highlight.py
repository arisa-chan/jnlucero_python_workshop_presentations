"""Syntax highlighting for code blocks using Pygments.

Converts a code string + language name into per-line token spans:

    List[List[Tuple[str, int]]]
      ^line  ^token  text  role

Where role is one of the ROLE_* constants below.  The renderer maps roles
to palette colour indices via :func:`role_to_color`.

Falls back gracefully if Pygments is not installed or the language is
unrecognised — every fragment gets ROLE_DEFAULT.
"""

from __future__ import annotations

from typing import List, Tuple

# --------------------------------------------------------------------------- #
# Semantic colour roles (theme-agnostic)
# --------------------------------------------------------------------------- #

ROLE_DEFAULT = 0  # identifiers, operators, punctuation, whitespace
ROLE_KEYWORD = 1  # language keywords (def, class, if, return …)
ROLE_STRING  = 2  # string / bytes / template literals
ROLE_COMMENT = 3  # line and block comments
ROLE_NUMBER  = 4  # numeric literals
ROLE_BUILTIN = 5  # built-in names, exceptions, type names

# --------------------------------------------------------------------------- #
# Pygments availability check (optional dependency)
# --------------------------------------------------------------------------- #

try:
    from pygments import highlight as _pg_highlight  # noqa: F401
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.lexers import TextLexer
    from pygments.token import Token
    from pygments.util import ClassNotFound
    _PYGMENTS = True
except ImportError:
    _PYGMENTS = False

# --------------------------------------------------------------------------- #
# Token-type → role mapping
# --------------------------------------------------------------------------- #

def _token_role(ttype_str: str) -> int:
    """Map a Pygments token type string to a ROLE_* constant."""
    if ttype_str.startswith("Token.Keyword"):
        return ROLE_KEYWORD
    if ttype_str.startswith("Token.Comment"):
        return ROLE_COMMENT
    if (ttype_str.startswith("Token.Literal.String")
            or ttype_str.startswith("Token.Literal.Scalar")):
        return ROLE_STRING
    if ttype_str.startswith("Token.Literal.Number"):
        return ROLE_NUMBER
    if (ttype_str.startswith("Token.Name.Builtin")
            or ttype_str.startswith("Token.Name.Exception")
            or ttype_str.startswith("Token.Name.Class")
            or ttype_str.startswith("Token.Name.Decorator")):
        return ROLE_BUILTIN
    return ROLE_DEFAULT


# --------------------------------------------------------------------------- #
# Internal flat tokenizer
# --------------------------------------------------------------------------- #

def _tokenize_flat(code: str, language: str) -> List[Tuple[str, int]]:
    """Return a flat list of (text, role) for the entire code string.

    Newlines are kept inside the text fragments — callers split on them.
    Falls back to single ROLE_DEFAULT span on any error.
    """
    if not _PYGMENTS:
        return [(code, ROLE_DEFAULT)]

    # Resolve lexer.
    lexer = None
    if language:
        try:
            lexer = get_lexer_by_name(language, stripall=False, stripnl=False)
        except ClassNotFound:
            pass
    if lexer is None:
        try:
            lexer = guess_lexer(code, stripall=False, stripnl=False)
        except ClassNotFound:
            pass
    if lexer is None or isinstance(lexer, TextLexer):
        return [(code, ROLE_DEFAULT)]

    result: list[Tuple[str, int]] = []
    try:
        for ttype, value in lexer.get_tokens(code):
            result.append((value, _token_role(str(ttype))))
    except Exception:  # noqa: BLE001
        return [(code, ROLE_DEFAULT)]

    return result


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def tokenize_lines(code: str, language: str) -> List[List[Tuple[str, int]]]:
    """Tokenize *code* and return per-line token spans.

    Returns ``List[List[Tuple[str, role_int]]]`` — one inner list per display
    line.  Trailing empty token lists (from a final newline) are stripped.

    Example::

        lines = tokenize_lines("x = 1\\n# hi\\n", "python")
        # → [[("x", 0), (" = ", 0), ("1", 4)],
        #    [("# hi", 3)]]
    """
    flat = _tokenize_flat(code, language)

    lines: list[list[Tuple[str, int]]] = [[]]
    for text, role in flat:
        parts = text.split("\n")
        for i, part in enumerate(parts):
            if part:
                lines[-1].append((part, role))
            if i < len(parts) - 1:
                lines.append([])

    # Drop trailing empty lines (artifact of Pygments appending a final "\n").
    while lines and not lines[-1]:
        lines.pop()

    return lines if lines else [[]]


def role_to_color(role: int, theme: object) -> int:
    """Map a ROLE_* constant to a Pyxel palette index using *theme* attributes.

    The mapping targets a dark code-panel background (``theme.fg``):

    * ``ROLE_DEFAULT`` / ``ROLE_BUILTIN`` → ``theme.bg``   (brightest — normal text)
    * ``ROLE_KEYWORD`` / ``ROLE_NUMBER``  → ``theme.muted`` (light green — stands out)
    * ``ROLE_STRING``  / ``ROLE_COMMENT`` → ``theme.accent`` (dim green — secondary)
    """
    if role in (ROLE_KEYWORD, ROLE_NUMBER):
        return theme.muted  # type: ignore[attr-defined]
    if role in (ROLE_STRING, ROLE_COMMENT):
        return theme.accent  # type: ignore[attr-defined]
    # ROLE_DEFAULT, ROLE_BUILTIN, anything else
    return theme.bg  # type: ignore[attr-defined]


def pygments_available() -> bool:
    """Return True if Pygments is installed and usable."""
    return _PYGMENTS
