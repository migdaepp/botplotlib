"""Box-model layout engine with bounding-box collision avoidance.

Handles:
- Margin-based layout (title, axes, plot area, legend)
- Tick label positioning
- Legend layout
- Bounding-box collision detection for text labels (ggrepel-style nudging)
"""

from __future__ import annotations

from dataclasses import dataclass

from botplotlib._fonts.metrics import text_bbox, text_height
from botplotlib._types import Rect


@dataclass
class LayoutResult:
    """Result of the layout computation."""

    canvas_width: float
    canvas_height: float
    plot_area: Rect
    title_pos: tuple[float, float] | None = None
    subtitle_pos: tuple[float, float] | None = None
    x_label_pos: tuple[float, float] | None = None
    y_label_pos: tuple[float, float] | None = None
    footnote_pos: tuple[float, float] | None = None
    legend_area: Rect | None = None


def compute_layout(
    canvas_width: float,
    canvas_height: float,
    margin_top: float,
    margin_right: float,
    margin_bottom: float,
    margin_left: float,
    has_title: bool = False,
    has_subtitle: bool = False,
    has_x_label: bool = False,
    has_y_label: bool = False,
    has_footnote: bool = False,
    has_legend: bool = False,
    legend_position: str = "right",
    title_font_size: float = 16.0,
    title_align: str = "center",
    subtitle_font_size: float = 13.0,
    subtitle_lines: int = 1,
    label_font_size: float = 12.0,
    footnote_font_size: float = 10.0,
    y_label_position: str = "side",
    legend_width: float = 120.0,
    legend_height: float = 30.0,
) -> LayoutResult:
    """Compute box-model layout for a plot.

    Returns a LayoutResult with pixel coordinates for all plot regions.
    """
    # Adjust margins for labels
    effective_top = margin_top
    effective_bottom = margin_bottom
    effective_left = margin_left
    effective_right = margin_right

    title_pos = None
    subtitle_pos = None
    x_label_pos = None
    y_label_pos = None
    footnote_pos = None
    legend_area = None

    if has_title:
        effective_top += title_font_size + 10

    if has_subtitle:
        n_lines = max(subtitle_lines, 1)
        effective_top += subtitle_font_size * 1.3 * n_lines + 6

    if has_x_label:
        effective_bottom += label_font_size + 5

    if has_y_label and y_label_position == "side":
        # Rotated -90°: text height becomes horizontal width
        effective_left += text_height(label_font_size) + 5
    elif has_y_label and y_label_position == "top":
        effective_top += label_font_size + 4

    if has_footnote:
        effective_bottom += footnote_font_size + 20

    if has_legend and legend_position == "right":
        effective_right += legend_width
    elif has_legend and legend_position == "top":
        effective_top += legend_height

    plot_area = Rect(
        x=effective_left,
        y=effective_top,
        width=max(1, canvas_width - effective_left - effective_right),
        height=max(1, canvas_height - effective_top - effective_bottom),
    )

    # Title position
    if has_title:
        if title_align == "left":
            title_x = plot_area.x
        elif title_align == "right":
            title_x = plot_area.right
        else:
            title_x = plot_area.x + plot_area.width / 2
        title_pos = (title_x, margin_top + title_font_size)

    # Subtitle position (below title)
    if has_subtitle:
        title_space = (title_font_size + 10) if has_title else 0
        subtitle_y = margin_top + title_space + subtitle_font_size
        if title_align == "left":
            subtitle_x = plot_area.x
        elif title_align == "right":
            subtitle_x = plot_area.right
        else:
            subtitle_x = plot_area.x + plot_area.width / 2
        subtitle_pos = (subtitle_x, subtitle_y)

    if has_x_label:
        x_label_pos = (
            plot_area.x + plot_area.width / 2,
            canvas_height
            - margin_bottom / 2
            - (footnote_font_size + 16 if has_footnote else 0),
        )

    if has_y_label:
        if y_label_position == "top":
            # Left-aligned above the plot area
            y_label_pos = (
                plot_area.x,
                plot_area.y - 4,
            )
        else:
            # Rotated -90°: text height becomes horizontal width.
            # Place x so the left edge of the rotated bbox stays >= 0.
            y_label_pos = (
                text_height(label_font_size),
                plot_area.y + plot_area.height / 2,
            )

    if has_footnote:
        footnote_pos = (
            plot_area.x,
            canvas_height - footnote_font_size,
        )

    if has_legend and legend_position == "right":
        legend_area = Rect(
            x=plot_area.right + 15,
            y=plot_area.y,
            width=legend_width - 15,
            height=plot_area.height,
        )
    elif has_legend and legend_position == "top":
        legend_area = Rect(
            x=plot_area.x,
            y=plot_area.y - legend_height,
            width=plot_area.width,
            height=legend_height,
        )

    return LayoutResult(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        plot_area=plot_area,
        title_pos=title_pos,
        subtitle_pos=subtitle_pos,
        x_label_pos=x_label_pos,
        y_label_pos=y_label_pos,
        footnote_pos=footnote_pos,
        legend_area=legend_area,
    )


# ---------------------------------------------------------------------------
# Collision detection and avoidance
# ---------------------------------------------------------------------------


@dataclass
class TextLabel:
    """A positioned text label for collision avoidance."""

    text: str
    x: float
    y: float
    font_size: float
    font_name: str = "arial"
    anchor: str = "middle"

    def bbox(self) -> Rect:
        """Compute bounding box for this label."""
        return text_bbox(
            self.text,
            self.font_size,
            self.x,
            self.y,
            font_name=self.font_name,
            anchor=self.anchor,
        )


def avoid_collisions(
    labels: list[TextLabel],
    max_iterations: int = 50,
    nudge_step: float = 2.0,
) -> list[TextLabel]:
    """Nudge overlapping labels apart (ggrepel-style).

    Iteratively moves labels vertically to resolve overlaps.
    Returns a new list of TextLabel objects with adjusted positions.
    """
    if len(labels) <= 1:
        return list(labels)

    # Work with mutable copies
    result = [
        TextLabel(
            text=lbl.text,
            x=lbl.x,
            y=lbl.y,
            font_size=lbl.font_size,
            font_name=lbl.font_name,
            anchor=lbl.anchor,
        )
        for lbl in labels
    ]

    for _ in range(max_iterations):
        any_overlap = False
        for i in range(len(result)):
            for j in range(i + 1, len(result)):
                bbox_i = result[i].bbox()
                bbox_j = result[j].bbox()
                if bbox_i.intersects(bbox_j):
                    any_overlap = True
                    # Nudge apart vertically
                    if result[i].y <= result[j].y:
                        result[i].y -= nudge_step
                        result[j].y += nudge_step
                    else:
                        result[i].y += nudge_step
                        result[j].y -= nudge_step
        if not any_overlap:
            break

    return result
