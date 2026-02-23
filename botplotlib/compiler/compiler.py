"""Compiler: PlotSpec → CompiledPlot.

Orchestrates the full compilation pipeline:
1. Resolve theme
2. Normalize data
3. Compute scales and ticks
4. Run WCAG accessibility checks (structural gate)
5. Compute layout
6. Position all geometry

Geom dispatch uses the plugin registry (botplotlib.geoms).
"""

from __future__ import annotations

from botplotlib._colors.palettes import assign_colors
from botplotlib._types import TickMark
from botplotlib.compiler.accessibility import validate_theme_accessibility
from botplotlib.compiler.layout import TextLabel, avoid_collisions, compute_layout
from botplotlib.compiler.ticks import format_tick, nice_ticks
from botplotlib.geoms import ResolvedScales, get_geom

# Re-export compiled types for backward compatibility.
# External code (renderer, tests) imports from botplotlib.compiler.compiler.
from botplotlib.geoms.primitives import (  # noqa: F401
    CompiledBar,
    CompiledLegendEntry,
    CompiledLine,
    CompiledPath,
    CompiledPlot,
    CompiledPoint,
    CompiledText,
    Primitive,
)
from botplotlib.spec.models import PlotSpec
from botplotlib.spec.scales import CategoricalScale, LinearScale
from botplotlib.spec.theme import ThemeSpec, resolve_theme

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Fraction of tick range to pad on each side of a numeric axis.
# Prevents extremal data points (circles, line endpoints) from being
# clipped at the plot-area boundary.  Analogous to ggplot2's `expand`.
_SCALE_PAD = 0.03

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

    # --- Geom-driven scale computation ---
    # Collect ScaleHints from all layers via the geom registry.
    layer_geoms = []
    for layer in spec.layers:
        if not data:
            continue
        geom = get_geom(layer.geom)
        geom.validate(layer, data)
        hint = geom.scale_hint(layer, data)
        layer_geoms.append((layer, geom, hint))

    # Merge hints into unified scales
    all_x_numeric: list[float] = []
    all_y_numeric: list[float] = []
    x_is_categorical = False
    all_categories: list[str] = []

    for _layer, _geom, hint in layer_geoms:
        if hint.x_type == "categorical":
            x_is_categorical = True
            all_categories.extend(hint.x_categories)
        else:
            all_x_numeric.extend(hint.x_numeric)
        all_y_numeric.extend(hint.y_numeric)

    # Compute scales and ticks
    if x_is_categorical:
        # Deduplicate categories preserving order
        unique_cats: list[str] = list(dict.fromkeys(all_categories))
        x_scale: LinearScale | CategoricalScale = CategoricalScale(
            categories=unique_cats,
            pixel_min=plot_area.x,
            pixel_max=plot_area.right,
        )
        compiled.x_ticks = [
            TickMark(value=i, label=cat, pixel_pos=x_scale.map(cat))
            for i, cat in enumerate(unique_cats)
        ]
    elif all_x_numeric:
        x_tick_vals = nice_ticks(min(all_x_numeric), max(all_x_numeric))
        x_pad = (x_tick_vals[-1] - x_tick_vals[0]) * _SCALE_PAD
        x_scale = LinearScale(
            data_min=x_tick_vals[0] - x_pad,
            data_max=x_tick_vals[-1] + x_pad,
            pixel_min=plot_area.x,
            pixel_max=plot_area.right,
        )
        compiled.x_ticks = [
            TickMark(value=v, label=format_tick(v), pixel_pos=x_scale.map(v))
            for v in x_tick_vals
        ]
    else:
        # No data — use a dummy scale
        x_scale = LinearScale(0, 1, plot_area.x, plot_area.right)

    if all_y_numeric:
        y_tick_vals = nice_ticks(min(all_y_numeric), max(all_y_numeric))
    else:
        y_tick_vals = nice_ticks(0, 1)

    y_pad = (y_tick_vals[-1] - y_tick_vals[0]) * _SCALE_PAD
    y_scale = LinearScale(
        data_min=y_tick_vals[0] - y_pad,
        data_max=y_tick_vals[-1] + y_pad,
        pixel_min=plot_area.bottom,  # SVG y is inverted
        pixel_max=plot_area.y,
    )
    compiled.y_ticks = [
        TickMark(value=v, label=format_tick(v), pixel_pos=y_scale.map(v))
        for v in y_tick_vals
    ]

    # Build resolved scales and dispatch to each geom
    default_color = theme.palette[0]
    resolved = ResolvedScales(
        x=x_scale,
        y=y_scale,
        color_map=color_map,
        default_color=default_color,
    )

    for layer, geom, _hint in layer_geoms:
        primitives = geom.compile(layer, data, resolved, theme, plot_area)
        for prim in primitives:
            compiled.add_primitive(prim)

    # Add legend entries
    if has_legend and color_map:
        for label, color in color_map.items():
            compiled.legend_entries.append(
                CompiledLegendEntry(label=label, color=color)
            )

    # Collision avoidance for tick labels
    _avoid_tick_collisions(compiled, theme)

    return compiled


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
