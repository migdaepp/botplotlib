"""Optional PNG export via CairoSVG.

Requires the ``png`` extras group: ``pip install botplotlib[png]``
"""

from __future__ import annotations


def svg_to_png(svg_string: str, output_path: str) -> None:
    """Convert an SVG string to a PNG file.

    Raises
    ------
    ImportError
        If CairoSVG is not installed.
    """
    try:
        import cairosvg
    except ImportError:
        raise ImportError(
            "PNG export requires CairoSVG. "
            "Install it with: pip install botplotlib[png]"
        ) from None

    cairosvg.svg2png(bytestring=svg_string.encode("utf-8"), write_to=output_path)
