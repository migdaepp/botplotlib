from __future__ import annotations

from pydantic import BaseModel, Field

from botplotlib._colors.palettes import DEFAULT_PALETTE


class ThemeSpec(BaseModel):
    """Visual theme for a plot."""

    # Background
    background_color: str = "#FFFFFF"

    # Fonts
    font_family: str = "Inter, Helvetica Neue, Arial, sans-serif"
    font_name: str = "arial"  # which font metrics to use for layout
    title_font_size: float = 16
    label_font_size: float = 12
    tick_font_size: float = 10

    # Colors
    text_color: str = "#333333"
    axis_color: str = "#333333"
    grid_color: str = "#EEEEEE"

    # Grid
    show_x_grid: bool = False
    show_y_grid: bool = True

    # Axes
    show_x_axis: bool = True
    show_y_axis: bool = False
    axis_stroke_width: float = 1.0

    # Plot elements
    point_radius: float = 4.0
    line_width: float = 2.0
    bar_padding: float = 0.2  # fraction of band width

    # Palette (WCAG AA compliant against white background)
    palette: list[str] = Field(default_factory=lambda: list(DEFAULT_PALETTE))

    # Margins (pixels)
    margin_top: float = 40
    margin_right: float = 20
    margin_bottom: float = 50
    margin_left: float = 60


# Default theme
DEFAULT_THEME = ThemeSpec()

# Platform presets
THEME_BLUESKY = ThemeSpec(
    title_font_size=20,
    label_font_size=14,
    tick_font_size=12,
    point_radius=5.0,
    line_width=2.5,
    margin_top=50,
    margin_bottom=60,
)

THEME_SUBSTACK = ThemeSpec(
    title_font_size=18,
    label_font_size=13,
    tick_font_size=11,
    line_width=2.5,
)

THEME_PRINT = ThemeSpec(
    font_family="Georgia, Times New Roman, serif",
    font_name="arial",  # still use arial metrics for layout
    text_color="#000000",
    axis_color="#000000",
    grid_color="#DDDDDD",
    show_y_axis=True,
    axis_stroke_width=0.75,
    point_radius=3.0,
    line_width=1.5,
    palette=[
        "#000000",
        "#555555",
        "#888888",
        "#AAAAAA",
        "#333333",
        "#666666",
        "#999999",
        "#BBBBBB",
        "#444444",
        "#777777",
    ],
)

THEME_REGISTRY: dict[str, ThemeSpec] = {
    "default": DEFAULT_THEME,
    "bluesky": THEME_BLUESKY,
    "social": THEME_BLUESKY,  # alias
    "substack": THEME_SUBSTACK,
    "print": THEME_PRINT,
}


def resolve_theme(name: str) -> ThemeSpec:
    """Look up a theme by name. Raises ValueError for unknown themes."""
    if name not in THEME_REGISTRY:
        available = ", ".join(sorted(THEME_REGISTRY.keys()))
        raise ValueError(f"Unknown theme '{name}'. Available themes: {available}")
    return THEME_REGISTRY[name]
