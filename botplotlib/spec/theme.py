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
    title_font_weight: str = "normal"  # "normal" or "bold"
    title_align: str = "center"  # "left", "center", or "right"
    subtitle_font_size: float = 13
    subtitle_color: str | None = None  # None → use text_color
    label_font_size: float = 12
    tick_font_size: float = 10
    footnote_font_size: float = 10
    footnote_color: str | None = None  # None → use text_color

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
    y_label_position: str = "side"  # "side" (rotated, default) or "top" (horizontal)

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
        "#333333",
        "#555555",
        "#666666",
        "#777777",
        "#888888",
        "#222222",
        "#444444",
        "#111111",
        "#383838",
    ],
)

THEME_PDF = ThemeSpec(
    font_family="Georgia, Times New Roman, serif",
    font_name="arial",  # still use arial metrics for layout
    text_color="#2D2D2D",
    axis_color="#2D2D2D",
    grid_color="#E0E0E0",
    show_y_axis=True,
    axis_stroke_width=0.75,
    point_radius=3.5,
    line_width=1.8,
    palette=[
        "#2B5B8A",  # navy
        "#B5342E",  # brick red
        "#2D7A46",  # forest green
        "#7B4EA3",  # purple
        "#8B6914",  # dark gold
        "#1A7A7A",  # teal
        "#5A5A8A",  # slate blue
        "#8B5A2B",  # brown
        "#A03050",  # crimson
        "#555555",  # gray
    ],
)

THEME_MAGAZINE = ThemeSpec(
    background_color="#F2EDE4",
    font_family="Georgia, Times New Roman, serif",
    font_name="arial",
    title_font_size=22,
    title_font_weight="bold",
    title_align="left",
    subtitle_font_size=14,
    subtitle_color="#555555",
    label_font_size=12,
    tick_font_size=11,
    footnote_font_size=10,
    footnote_color="#666666",
    text_color="#333333",
    axis_color="#CCCCCC",
    grid_color="#D8D2C6",
    show_x_grid=False,
    show_y_grid=True,
    show_x_axis=True,
    show_y_axis=False,
    axis_stroke_width=1.0,
    y_label_position="top",
    point_radius=4.0,
    line_width=2.5,
    bar_padding=0.2,
    palette=[
        "#388EC1",  # blue
        "#8C1B2B",  # dark red
        "#2D8B61",  # green
        "#7B4EA3",  # purple
        "#A86800",  # dark amber
        "#1A6B6B",  # dark teal
        "#C44E52",  # salmon red
        "#5A5A8A",  # slate blue
        "#8B5A2B",  # brown
        "#555555",  # gray
    ],
    margin_top=30,
    margin_right=20,
    margin_bottom=40,
    margin_left=50,
)

THEME_REGISTRY: dict[str, ThemeSpec] = {
    "default": DEFAULT_THEME,
    "bluesky": THEME_BLUESKY,
    "social": THEME_BLUESKY,  # alias
    "substack": THEME_SUBSTACK,
    "print": THEME_PRINT,
    "pdf": THEME_PDF,
    "arxiv": THEME_PDF,  # alias
    "magazine": THEME_MAGAZINE,
    "economist": THEME_MAGAZINE,  # alias
}


def resolve_theme(name: str) -> ThemeSpec:
    """Look up a theme by name. Raises ValueError for unknown themes."""
    if name not in THEME_REGISTRY:
        available = ", ".join(sorted(THEME_REGISTRY.keys()))
        raise ValueError(f"Unknown theme '{name}'. Available themes: {available}")
    return THEME_REGISTRY[name]
