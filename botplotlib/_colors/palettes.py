"""Color palette utilities for botplotlib.

Provides a colorblind-friendly default palette and helpers for hex/RGB
conversion, group-to-color assignment, and WCAG luminance / contrast
calculations.
"""

from __future__ import annotations

DEFAULT_PALETTE: list[str] = [
    "#4E79A7",  # steel blue
    "#C56A00",  # orange (WCAG AA compliant)
    "#E15759",  # red
    "#4A8B86",  # teal (WCAG AA compliant)
    "#59A14F",  # green
    "#A68B00",  # gold (WCAG AA compliant)
    "#B07AA1",  # purple
    "#C4636E",  # rose (WCAG AA compliant)
    "#9C755F",  # brown
    "#7B7573",  # gray (WCAG AA compliant)
]


# ---------------------------------------------------------------------------
# Hex / RGB conversion
# ---------------------------------------------------------------------------


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Parse a hex color string to an ``(r, g, b)`` tuple.

    Accepts both short (``#abc`` or ``abc``) and long (``#aabbcc`` or
    ``aabbcc``) forms, with or without the leading ``#``.
    """
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) != 6:
        raise ValueError(
            f"Invalid hex color: {hex_color!r}. Expected format: '#RRGGBB' or '#RGB'."
        )
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert an ``(r, g, b)`` tuple to a hex color string with ``#``."""
    return f"#{r:02X}{g:02X}{b:02X}"


# ---------------------------------------------------------------------------
# Color assignment
# ---------------------------------------------------------------------------


def assign_colors(
    groups: list[str],
    palette: list[str] | None = None,
) -> dict[str, str]:
    """Assign a color to each unique group name.

    Colors are drawn from *palette* (defaulting to :data:`DEFAULT_PALETTE`)
    in order.  If there are more groups than palette entries the palette
    cycles.

    Returns a ``{group_name: hex_color}`` mapping that preserves the
    insertion order of *groups* (first occurrence).
    """
    if palette is None:
        palette = DEFAULT_PALETTE
    seen: dict[str, str] = {}
    idx = 0
    for group in groups:
        if group not in seen:
            seen[group] = palette[idx % len(palette)]
            idx += 1
    return seen


# ---------------------------------------------------------------------------
# WCAG luminance & contrast
# ---------------------------------------------------------------------------


def _linearize(channel: float) -> float:
    """Linearize an sRGB channel value in [0, 1]."""
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Compute the WCAG relative luminance of a hex color.

    The luminance is a value between 0.0 (black) and 1.0 (white).

    See https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = hex_to_rgb(hex_color)
    r_lin = _linearize(r / 255.0)
    g_lin = _linearize(g / 255.0)
    b_lin = _linearize(b / 255.0)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(color1: str, color2: str) -> float:
    """Compute the WCAG contrast ratio between two hex colors.

    The result is a value between 1.0 (identical luminance) and 21.0
    (black vs. white).

    See https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio
    """
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    if l2 > l1:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)
