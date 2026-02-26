"""WCAG accessibility checks for botplotlib.

Structural quality gate: themes that fail AA contrast produce errors,
not warnings. This implements the "structural, not supervisory" quality
gate from the Cyborg Social Contract.
"""

from __future__ import annotations

from botplotlib._colors.palettes import contrast_ratio


class ContrastError(Exception):
    """Raised when a theme fails WCAG contrast requirements."""


# WCAG 2.1 AA minimum contrast ratios
WCAG_AA_NORMAL_TEXT = 4.5  # normal text (< 18pt or < 14pt bold)
WCAG_AA_LARGE_TEXT = 3.0  # large text (>= 18pt or >= 14pt bold)
LARGE_TEXT_THRESHOLD = 18.0  # font size in px considered "large"


def check_text_contrast(
    text_color: str,
    background_color: str,
    font_size: float = 12.0,
) -> None:
    """Check that text meets WCAG AA contrast against its background.

    Parameters
    ----------
    text_color:
        Hex color of the text.
    background_color:
        Hex color of the background.
    font_size:
        Font size in pixels.

    Raises
    ------
    ContrastError
        If the contrast ratio is below the WCAG AA threshold.
    """
    ratio = contrast_ratio(text_color, background_color)
    threshold = (
        WCAG_AA_LARGE_TEXT if font_size >= LARGE_TEXT_THRESHOLD else WCAG_AA_NORMAL_TEXT
    )
    if ratio < threshold:
        raise ContrastError(
            f"Text color {text_color} on background {background_color} "
            f"has contrast ratio {ratio:.2f}:1, which is below the "
            f"WCAG AA "
            f"{'large text' if font_size >= LARGE_TEXT_THRESHOLD else 'normal text'} "
            f"minimum of {threshold}:1. "
            f"Nobody reads what nobody can see. "
            f"Try darkening the text or lightening the background."
        )


def check_palette_contrast(
    palette: list[str],
    background_color: str,
    min_ratio: float = 3.0,
) -> None:
    """Check that all palette colors have sufficient contrast against the background.

    Parameters
    ----------
    palette:
        List of hex colors in the palette.
    background_color:
        Hex color of the plot background.
    min_ratio:
        Minimum contrast ratio required (default 3.0 for graphical elements).

    Raises
    ------
    ContrastError
        If any palette color fails the contrast check.
    """
    for i, color in enumerate(palette):
        ratio = contrast_ratio(color, background_color)
        if ratio < min_ratio:
            raise ContrastError(
                f"Palette color {i} ({color}) on background {background_color} "
                f"has contrast ratio {ratio:.2f}:1, which is below the "
                f"minimum of {min_ratio}:1. "
                f"Darken the color or lighten the background."
            )


def check_adjacent_contrast(
    palette: list[str],
    min_ratio: float = 1.5,
) -> None:
    """Check that adjacent palette colors are visually distinguishable.

    Parameters
    ----------
    palette:
        List of hex colors.
    min_ratio:
        Minimum contrast ratio between adjacent colors.

    Raises
    ------
    ContrastError
        If adjacent colors are too similar.
    """
    for i in range(len(palette) - 1):
        ratio = contrast_ratio(palette[i], palette[i + 1])
        if ratio < min_ratio:
            raise ContrastError(
                f"Adjacent palette colors {i} ({palette[i]}) and "
                f"{i + 1} ({palette[i + 1]}) have contrast ratio "
                f"{ratio:.2f}:1, which is below the minimum of {min_ratio}:1. "
                f"Two colors that look identical aren't pulling their weight."
            )


def validate_theme_accessibility(
    text_color: str,
    background_color: str,
    palette: list[str],
    title_font_size: float = 16.0,
    label_font_size: float = 12.0,
    tick_font_size: float = 10.0,
) -> None:
    """Run all accessibility checks for a theme.

    Parameters
    ----------
    text_color:
        Theme text color.
    background_color:
        Theme background color.
    palette:
        Theme color palette.
    title_font_size:
        Title font size in pixels.
    label_font_size:
        Axis label font size in pixels.
    tick_font_size:
        Tick label font size in pixels.

    Raises
    ------
    ContrastError
        If any check fails.
    """
    # Check text contrast at each font size
    check_text_contrast(text_color, background_color, title_font_size)
    check_text_contrast(text_color, background_color, label_font_size)
    check_text_contrast(text_color, background_color, tick_font_size)

    # Check palette against background
    check_palette_contrast(palette, background_color)
