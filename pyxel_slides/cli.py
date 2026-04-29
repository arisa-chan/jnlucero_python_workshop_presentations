"""Command-line entry point: ``pyxel-slides path/to/deck.md``."""

from __future__ import annotations

import argparse
from pathlib import Path

from .app import SlidesApp
from .theme import GAMEBOY


def _parse_resolution(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError(
            f"Invalid resolution {s!r}, expected WIDTHxHEIGHT (e.g. 384x216)"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pyxel-slides", description=__doc__)
    parser.add_argument("markdown", type=Path, help="Path to the deck .md file.")
    parser.add_argument(
        "--resolution",
        type=_parse_resolution,
        default=(384, 216),
        help="Window resolution WIDTHxHEIGHT (default: 384x216).",
    )
    parser.add_argument("--fps", type=int, default=30, help="Target frame rate.")
    parser.add_argument(
        "--pyxres",
        type=Path,
        default=None,
        help="Optional .pyxres sprite sheet to load (defaults to <deck>.pyxres if present).",
    )
    parser.add_argument(
        "--title",
        default="pyxel-slides",
        help="Window title.",
    )
    parser.add_argument(
        "--no-fonts",
        action="store_true",
        default=False,
        help="Skip downloading Spleen BDF fonts; use built-in 4x6 pixel font.",
    )

    args = parser.parse_args(argv)

    md_path: Path = args.markdown
    if not md_path.exists():
        parser.error(f"Markdown file not found: {md_path}")

    pyxres_path = args.pyxres
    if pyxres_path is None:
        candidate = md_path.with_suffix(".pyxres")
        if candidate.exists():
            pyxres_path = candidate

    width, height = args.resolution
    app = SlidesApp(
        markdown_path=md_path,
        theme=GAMEBOY,
        width=width,
        height=height,
        fps=args.fps,
        title=args.title,
        pyxres_path=pyxres_path,
        download_fonts=not args.no_fonts,
    )
    app.run()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
