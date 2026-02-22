"""Compiler: PlotSpec → CompiledPlot.

Orchestrates the full compilation pipeline:
1. Resolve theme
2. Normalize data
3. Compute scales and ticks
4. Run WCAG accessibility checks (structural gate)
5. Compute layout
6. Position all geometry
"""

from __future__ import annotations

from dataclasses import dataclass, field

from botplotlib._colors.palettes import assign_colors
from botplotlib._types import Rect, TickMark
from botplotlib.compiler.accessibility import validate_theme_accessibility
from botplotlib.compiler.layout import (
    TextLabel,
    avoid_collisions,
    compute_layout,
)
from botplotlib.compiler.ticks import format_tick, nice_ticks
from botplotlib.spec.models import PlotSpec
from botplotlib.spec.scales import CategoricalScale, LinearScale
from botplotlib.spec.theme import ThemeSpec, resolve_theme

# ---------------------------------------------------------------------------
# Compiled geometry types
# ---------------------------------------------------------------------------


@dataclass
class CompiledPoint:
    """A positioned scatter point."""

    px: float
    py: float
    color: str
    radius: float
    group: str | None = None


@dataclass
class CompiledLine:
    """A positioned polyline."""

    points: list[tuple[float, float]]
    color: str
    width: float
    group: str | None = None


@dataclass
class CompiledBar:
    """A positioned bar."""

    px: float
    py: float
    bar_width: float
    bar_height: float
    color: str
    group: str | None = None


@dataclass
class CompiledText:
    """A positioned text element."""

    text: str
    x: float
    y: float
    font_size: float
    color: str
    anchor: str = "middle"
    rotation: float = 0.0


@dataclass
class CompiledLegendEntry:
    """A legend entry."""

    label: str
    color: str


@dataclass
class CompiledPlot:
    """Fully positioned geometry ready for rendering."""

    width: float
    height: float
    theme: ThemeSpec
    plot_area: Rect
    points: list[CompiledPoint] = field(default_factory=list)
    lines: list[CompiledLine] = field(default_factory=list)
    bars: list[CompiledBar] = field(default_factory=list)
    x_ticks: list[TickMark] = field(default_factory=list)
    y_ticks: list[TickMark] = field(default_factory=list)
    texts: list[CompiledText] = field(default_factory=list)
    legend_entries: list[CompiledLegendEntry] = field(default_factory=list)
    legend_area: Rect | None = None
    clip_id: str = "plot-clip"


# ---------------------------------------------------------------------------
# Compiler
# ---------------------------------------------------------------------------


def compile_spec(spec: PlotSpec) -> CompiledPlot:
    """Compile a PlotSpec into positioned geometry.

    Raises
    ------
    ContrastError
        If the theme fails WCAG accessibility checks.
    ValueError
        If the spec references unknown columns or themes.
    """
    # 1. Resolve theme
    theme = resolve_theme(spec.theme)

    # 2. Accessibility gate (structural, not supervisory)
    validate_theme_accessibility(
        text_color=theme.text_color,
        background_color=theme.background_color,
        palette=theme.palette,
        title_font_size=theme.title_font_size,
        label_font_size=theme.label_font_size,
        tick_font_size=theme.tick_font_size,
    )

    # 3. Normalize data
    data = spec.data.columns if spec.data.columns else {}

    # 4. Determine what we need to render
    has_legend = False
    color_map: dict[str, str] = {}
    for layer in spec.layers:
        if layer.color and layer.color in data:
            groups = [str(v) for v in data[layer.color]]
            color_map = assign_colors(groups, theme.palette)
            has_legend = spec.legend.show

    # 5. Compute layout
    layout = compute_layout(
        canvas_width=spec.size.width,
        canvas_height=spec.size.height,
        margin_top=theme.margin_top,
        margin_right=theme.margin_right,
        margin_bottom=theme.margin_bottom,
        margin_left=theme.margin_left,
        has_title=spec.labels.title is not None,
        has_x_label=spec.labels.x is not None,
        has_y_label=spec.labels.y is not None,
        has_legend=has_legend,
        legend_position=spec.legend.position,
        title_font_size=theme.title_font_size,
        label_font_size=theme.label_font_size,
    )
    plot_area = layout.plot_area

    # 6. Compile each layer
    compiled = CompiledPlot(
        width=spec.size.width,
        height=spec.size.height,
        theme=theme,
        plot_area=plot_area,
        legend_area=layout.legend_area,
    )

    # Add title, axis labels
    if layout.title_pos:
        compiled.texts.append(
            CompiledText(
                text=spec.labels.title or "",
                x=layout.title_pos[0],
                y=layout.title_pos[1],
                font_size=theme.title_font_size,
                color=theme.text_color,
                anchor="middle",
            )
        )

    if layout.x_label_pos:
        compiled.texts.append(
            CompiledText(
                text=spec.labels.x or "",
                x=layout.x_label_pos[0],
                y=layout.x_label_pos[1],
                font_size=theme.label_font_size,
                color=theme.text_color,
                anchor="middle",
            )
        )

    if layout.y_label_pos:
        compiled.texts.append(
            CompiledText(
                text=spec.labels.y or "",
                x=layout.y_label_pos[0],
                y=layout.y_label_pos[1],
                font_size=theme.label_font_size,
                color=theme.text_color,
                anchor="middle",
                rotation=-90,
            )
        )

    for layer in spec.layers:
        if not data:
            continue

        x_col = data.get(layer.x, [])
        y_col = data.get(layer.y, [])
        color_col = (
            [str(v) for v in data[layer.color]]
            if layer.color and layer.color in data
            else None
        )

        if layer.geom == "bar":
            _compile_bar_layer(
                compiled,
                x_col,
                y_col,
                color_col,
                color_map,
                theme,
                plot_area,
            )
        else:
            # Scatter or line: numeric scales
            _compile_numeric_layer(
                compiled,
                layer.geom,
                x_col,
                y_col,
                color_col,
                color_map,
                theme,
                plot_area,
            )

    # Add legend entries
    if has_legend and color_map:
        for label, color in color_map.items():
            compiled.legend_entries.append(
                CompiledLegendEntry(label=label, color=color)
            )

    # Collision avoidance for tick labels
    _avoid_tick_collisions(compiled, theme)

    return compiled


def _compile_numeric_layer(
    compiled: CompiledPlot,
    geom: str,
    x_col: list,
    y_col: list,
    color_col: list[str] | None,
    color_map: dict[str, str],
    theme: ThemeSpec,
    plot_area: Rect,
) -> None:
    """Compile a scatter or line layer with numeric axes."""
    x_vals = [float(v) for v in x_col]
    y_vals = [float(v) for v in y_col]

    if not x_vals or not y_vals:
        return

    # Compute scales from ticks for nice axis bounds
    x_ticks_vals = nice_ticks(min(x_vals), max(x_vals))
    y_ticks_vals = nice_ticks(min(y_vals), max(y_vals))

    x_scale = LinearScale(
        data_min=x_ticks_vals[0],
        data_max=x_ticks_vals[-1],
        pixel_min=plot_area.x,
        pixel_max=plot_area.right,
    )
    y_scale = LinearScale(
        data_min=y_ticks_vals[0],
        data_max=y_ticks_vals[-1],
        pixel_min=plot_area.bottom,  # SVG y is inverted
        pixel_max=plot_area.y,
    )

    # Set ticks if not already set
    if not compiled.x_ticks:
        compiled.x_ticks = [
            TickMark(value=v, label=format_tick(v), pixel_pos=x_scale.map(v))
            for v in x_ticks_vals
        ]
    if not compiled.y_ticks:
        compiled.y_ticks = [
            TickMark(value=v, label=format_tick(v), pixel_pos=y_scale.map(v))
            for v in y_ticks_vals
        ]

    default_color = theme.palette[0]

    if geom == "scatter":
        for i in range(min(len(x_vals), len(y_vals))):
            color = (
                color_map.get(color_col[i], default_color)
                if color_col
                else default_color
            )
            compiled.points.append(
                CompiledPoint(
                    px=x_scale.map(x_vals[i]),
                    py=y_scale.map(y_vals[i]),
                    color=color,
                    radius=theme.point_radius,
                    group=color_col[i] if color_col else None,
                )
            )

    elif geom == "line":
        if color_col:
            # Group by color
            groups: dict[str, list[tuple[float, float]]] = {}
            for i in range(min(len(x_vals), len(y_vals))):
                g = color_col[i]
                if g not in groups:
                    groups[g] = []
                groups[g].append(
                    (
                        x_scale.map(x_vals[i]),
                        y_scale.map(y_vals[i]),
                    )
                )
            for g, pts in groups.items():
                compiled.lines.append(
                    CompiledLine(
                        points=pts,
                        color=color_map.get(g, default_color),
                        width=theme.line_width,
                        group=g,
                    )
                )
        else:
            pts = [
                (x_scale.map(x_vals[i]), y_scale.map(y_vals[i]))
                for i in range(min(len(x_vals), len(y_vals)))
            ]
            compiled.lines.append(
                CompiledLine(
                    points=pts,
                    color=default_color,
                    width=theme.line_width,
                )
            )


def _compile_bar_layer(
    compiled: CompiledPlot,
    x_col: list,
    y_col: list,
    color_col: list[str] | None,
    color_map: dict[str, str],
    theme: ThemeSpec,
    plot_area: Rect,
) -> None:
    """Compile a bar layer with categorical x-axis."""
    categories = [str(v) for v in x_col]
    y_vals = [float(v) for v in y_col]

    if not categories or not y_vals:
        return

    # Unique categories in order
    unique_cats: list[str] = []
    seen: set[str] = set()
    for c in categories:
        if c not in seen:
            unique_cats.append(c)
            seen.add(c)

    cat_scale = CategoricalScale(
        categories=unique_cats,
        pixel_min=plot_area.x,
        pixel_max=plot_area.right,
    )

    y_max = max(y_vals) if y_vals else 1.0
    y_tick_vals = nice_ticks(0, y_max)
    y_scale = LinearScale(
        data_min=y_tick_vals[0],
        data_max=y_tick_vals[-1],
        pixel_min=plot_area.bottom,
        pixel_max=plot_area.y,
    )

    # Set ticks
    if not compiled.x_ticks:
        compiled.x_ticks = [
            TickMark(
                value=i,
                label=cat,
                pixel_pos=cat_scale.map(cat),
            )
            for i, cat in enumerate(unique_cats)
        ]
    if not compiled.y_ticks:
        compiled.y_ticks = [
            TickMark(value=v, label=format_tick(v), pixel_pos=y_scale.map(v))
            for v in y_tick_vals
        ]

    band = cat_scale.band_width
    bar_width = band * (1 - theme.bar_padding)
    default_color = theme.palette[0]

    for i in range(min(len(categories), len(y_vals))):
        cx = cat_scale.map(categories[i])
        y_px = y_scale.map(y_vals[i])
        baseline = y_scale.map(0)
        color = (
            color_map.get(color_col[i], default_color) if color_col else default_color
        )
        compiled.bars.append(
            CompiledBar(
                px=cx - bar_width / 2,
                py=min(y_px, baseline),
                bar_width=bar_width,
                bar_height=abs(baseline - y_px),
                color=color,
                group=color_col[i] if color_col else None,
            )
        )


def _avoid_tick_collisions(
    compiled: CompiledPlot,
    theme: ThemeSpec,
) -> None:
    """Apply collision avoidance to tick labels."""
    if len(compiled.x_ticks) > 1:
        labels = [
            TextLabel(
                text=t.label,
                x=t.pixel_pos,
                y=compiled.plot_area.bottom + 15,
                font_size=theme.tick_font_size,
                font_name=theme.font_name,
            )
            for t in compiled.x_ticks
        ]
        adjusted = avoid_collisions(labels)
        # Update positions (only y changes for x-axis labels)
        for tick, lbl in zip(compiled.x_ticks, adjusted):
            # TickMark is frozen, so create new ones
            pass  # x-tick collision is mainly horizontal — skip for MVP
