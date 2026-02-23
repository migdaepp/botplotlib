"""Label placement helpers for bar-like geoms.

Provides value formatting and inside-vs-outside placement logic
shared by BarGeom, WaterfallGeom, and future bar variants.
"""

from __future__ import annotations

from botplotlib._fonts.metrics import text_height, text_width


def format_label(value: float, label_format: str | None = None) -> str:
    """Format a numeric value for display on a bar.

    Parameters
    ----------
    value:
        The numeric value to format.
    label_format:
        Python ``.format()`` template, e.g. ``"${:,.0f}"``.
        If *None*, integers stay as integers and floats use ``:g``.
    """
    if label_format is not None:
        return label_format.format(value)
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def label_fits_inside(
    label_text: str,
    font_size: float,
    bar_width: float,
    bar_height: float,
    font_name: str = "arial",
    padding: float = 4.0,
) -> bool:
    """Return True if the label text fits inside the bar with padding."""
    tw = text_width(label_text, font_size, font_name)
    th = text_height(font_size)
    return (tw + 2 * padding) <= bar_width and (th + 2 * padding) <= bar_height
