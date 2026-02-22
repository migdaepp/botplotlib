"""Font metrics for estimating text dimensions without a rendering engine."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from botplotlib._types import Rect

_FONTS_DIR = Path(__file__).parent

_DEFAULT_CHAR_WIDTH = 0.5


@lru_cache(maxsize=None)
def _load_font_table(font_name: str) -> dict[str, float]:
    """Load a character-width JSON table for *font_name*.

    The JSON file must live in the same directory as this module and be
    named ``<font_name>.json``.  Results are cached so each file is read
    at most once per process.
    """
    path = _FONTS_DIR / f"{font_name}.json"
    with path.open() as fh:
        table: dict[str, float] = json.load(fh)
    return table


def text_width(
    text: str,
    font_size: float,
    font_name: str = "arial",
) -> float:
    """Return the estimated pixel width of *text* at *font_size*.

    Each character's relative width (as a fraction of font size) is
    looked up in the font table.  Characters not present in the table
    fall back to a default width of 0.5.
    """
    table = _load_font_table(font_name)
    return sum(table.get(ch, _DEFAULT_CHAR_WIDTH) for ch in text) * font_size


def text_height(font_size: float) -> float:
    """Return the estimated line height for *font_size*.

    Uses the standard 1.2x multiplier (matching CSS ``line-height: normal``
    for most Western fonts).
    """
    return font_size * 1.2


def text_bbox(
    text: str,
    font_size: float,
    x: float,
    y: float,
    font_name: str = "arial",
    anchor: str = "start",
) -> Rect:
    """Return a :class:`Rect` bounding box for *text* rendered at (*x*, *y*).

    Parameters
    ----------
    text:
        The string to measure.
    font_size:
        Font size in pixels.
    x, y:
        Anchor position (top of the text line).
    font_name:
        Name of the font metrics table to use.
    anchor:
        Horizontal anchor — ``"start"`` (left-aligned), ``"middle"``
        (centred), or ``"end"`` (right-aligned).

    Returns
    -------
    Rect
        The bounding box with ``x`` adjusted according to *anchor*.
    """
    w = text_width(text, font_size, font_name)
    h = text_height(font_size)

    if anchor == "middle":
        rect_x = x - w / 2
    elif anchor == "end":
        rect_x = x - w
    else:  # "start" or any unrecognised value
        rect_x = x

    return Rect(x=rect_x, y=y, width=w, height=h)
