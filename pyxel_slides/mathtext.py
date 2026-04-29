"""Math rendering via matplotlib.mathtext (Phase 5).

LaTeX-style math expressions are rasterised with matplotlib's built-in
mathtext renderer (no full TeX installation required) then Floyd-Steinberg
dithered to the GameBoy 4-colour palette.

matplotlib is an *optional* dependency listed under ``[full]``.
``matplotlib_available()`` returns False when it is absent, and all
rendering functions return None gracefully so the renderer can show a
plain-text fallback instead.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

# ------------------------------------------------------------------ #
# Optional-dependency probe
# ------------------------------------------------------------------ #

_MATPLOTLIB: bool = False
try:
    import matplotlib as _mpl

    # Must be set before any matplotlib submodule that touches a display.
    # Calling use() more than once is a no-op when the same backend is given.
    _mpl.use("Agg")
    _MATPLOTLIB = True
except ImportError:
    pass


# GameBoy DMG palette – must match the order in dither.py / theme.py.
_GAMEBOY_PALETTE: List[Tuple[int, int, int]] = [
    (0x9B, 0xBC, 0x0F),  # 0 – COL_BG    (lightest green)
    (0x0F, 0x38, 0x0F),  # 1 – COL_FG    (darkest)
    (0x30, 0x62, 0x30),  # 2 – COL_ACCENT (dark green)
    (0x8B, 0xAC, 0x0F),  # 3 – COL_MUTED  (light green)
]


def matplotlib_available() -> bool:
    """Return True when matplotlib is importable (and Agg backend usable)."""
    return _MATPLOTLIB


def render_math(
    expr: str,
    max_w: int,
    max_h: int,
    font_size: float = 14.0,
    palette_rgb: Optional[List[Tuple[int, int, int]]] = None,
) -> Optional[List[List[int]]]:
    """Render a mathtext expression to a 2-D list of palette indices.

    The expression must be valid *matplotlib mathtext* – a subset of LaTeX
    maths that does **not** require a real TeX installation.  Dollar signs
    are added automatically if the expression does not start with ``$``.

    Parameters
    ----------
    expr:
        The raw LaTeX-like math expression, e.g. ``r"\\frac{a}{b}"``.
    max_w, max_h:
        Maximum pixel dimensions of the rendered image.  The actual image
        is tight-cropped around the rendered expression (with a small pad)
        so it is typically smaller.
    font_size:
        Point size passed to matplotlib.  14 pt at 100 DPI gives reasonable
        results for most slide dimensions.
    palette_rgb:
        Optional custom palette (list of (R,G,B) tuples).  Defaults to the
        GameBoy DMG 4-colour palette.

    Returns
    -------
    A list of rows, each row being a list of palette indices, or ``None``
    when matplotlib is unavailable or the expression cannot be rendered.
    """
    if not _MATPLOTLIB:
        return None

    pal = palette_rgb if palette_rgb is not None else _GAMEBOY_PALETTE
    wrapped = f"${expr}$" if not expr.startswith("$") else expr

    try:
        import numpy as np  # noqa: PLC0415 – guarded by _MATPLOTLIB
        from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: PLC0415
        from matplotlib.figure import Figure  # noqa: PLC0415

        dpi = 100

        # ---- Pass 1: measure the bounding box of the rendered expression ----
        fig1 = Figure(facecolor="white")
        canvas1 = FigureCanvasAgg(fig1)
        fig1.set_dpi(dpi)
        # Use generous initial size; we crop it down afterwards.
        fig1.set_size_inches(max(0.1, max_w / dpi), max(0.1, max_h / dpi))
        ax1 = fig1.add_axes([0, 0, 1, 1])
        ax1.set_axis_off()
        text_obj = ax1.text(
            0.5,
            0.5,
            wrapped,
            fontsize=font_size,
            ha="center",
            va="center",
            transform=ax1.transAxes,
            color="black",
        )
        canvas1.draw()
        bbox = text_obj.get_window_extent(canvas1.get_renderer())

        # ---- Pass 2: render at tight size ----------------------------------
        pad_px = 6
        tw = min(max_w, max(4, int(bbox.width) + 2 * pad_px))
        th = min(max_h, max(4, int(bbox.height) + 2 * pad_px))

        fig2 = Figure(facecolor="white")
        canvas2 = FigureCanvasAgg(fig2)
        fig2.set_dpi(dpi)
        fig2.set_size_inches(tw / dpi, th / dpi)
        ax2 = fig2.add_axes([0, 0, 1, 1])
        ax2.set_axis_off()
        ax2.text(
            0.5,
            0.5,
            wrapped,
            fontsize=font_size,
            ha="center",
            va="center",
            transform=ax2.transAxes,
            color="black",
        )
        canvas2.draw()

        w_px, h_px = canvas2.get_width_height()
        raw = np.frombuffer(canvas2.buffer_rgba(), dtype=np.uint8).copy()
        buf = raw.reshape((h_px, w_px, 4))

        # Alpha-blend against a pure-white background.
        alpha = buf[:, :, 3:4].astype(float) / 255.0
        rgb_f = buf[:, :, :3].astype(float)
        blended = (rgb_f * alpha + 255.0 * (1.0 - alpha)).clip(0, 255).astype(int)

        # Flatten to list of (R, G, B) tuples for the ditherer.
        pixels: List[Tuple[int, int, int]] = list(
            zip(
                blended[:, :, 0].flatten().tolist(),
                blended[:, :, 1].flatten().tolist(),
                blended[:, :, 2].flatten().tolist(),
            )
        )

        # Floyd-Steinberg dither to the chosen palette.
        from .dither import _floyd_steinberg  # noqa: PLC0415

        flat = _floyd_steinberg(pixels, w_px, h_px, pal)
        return [flat[r * w_px: (r + 1) * w_px] for r in range(h_px)]

    except Exception:  # noqa: BLE001
        return None
