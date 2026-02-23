"""Waterfall geom — floating bars showing cumulative contribution.

A waterfall chart shows how an initial value is increased or decreased
by a series of intermediate values, arriving at a final total. Each bar
floats from the running total before the step to the running total after.

Data format:
    x: category labels (e.g., "Revenue", "COGS", "Profit")
    y: step values (positive = increase, negative = decrease)

The first bar starts at 0. Each subsequent bar floats from the previous
running total. Connector lines link the top of each bar to the base of
the next.
"""

from __future__ import annotations

from botplotlib._colors.palettes import relative_luminance
from botplotlib._types import Rect
from botplotlib.geoms import Geom, ResolvedScales, ScaleHint
from botplotlib.geoms.labels import format_label, label_fits_inside
from botplotlib.geoms.primitives import (
    CompiledBar,
    CompiledLine,
    CompiledText,
    Primitive,
)
from botplotlib.spec.models import LayerSpec
from botplotlib.spec.scales import CategoricalScale
from botplotlib.spec.theme import ThemeSpec


class WaterfallGeom(Geom):
    """Waterfall chart: floating bars showing cumulative contribution."""

    name = "waterfall"

    def validate(self, layer: LayerSpec, data: dict[str, list]) -> None:
        for col_name, role in [(layer.x, "x"), (layer.y, "y")]:
            if col_name not in data:
                raise ValueError(
                    f"Waterfall geom requires column '{col_name}' for {role} axis, "
                    f"but data has columns: {sorted(data.keys())}."
                )

    def scale_hint(self, layer: LayerSpec, data: dict[str, list]) -> ScaleHint:
        categories = [str(v) for v in data.get(layer.x, [])]
        y_vals: list[float] = []
        for v in data.get(layer.y, []):
            try:
                y_vals.append(float(v))
            except (ValueError, TypeError):
                pass

        # Compute running totals to determine y range
        running = 0.0
        all_endpoints = [0.0]
        for v in y_vals:
            running += v
            all_endpoints.append(running)

        return ScaleHint(
            x_type="categorical",
            y_type="numeric",
            x_categories=categories,
            y_numeric=all_endpoints,
        )

    def compile(
        self,
        layer: LayerSpec,
        data: dict[str, list],
        scales: ResolvedScales,
        theme: ThemeSpec,
        plot_area: Rect,
    ) -> list[Primitive]:
        categories = [str(v) for v in data[layer.x]]
        y_vals = [float(v) for v in data[layer.y]]

        if not isinstance(scales.x, CategoricalScale):
            raise TypeError(
                f"Waterfall geom requires a CategoricalScale for x-axis, "
                f"got {type(scales.x).__name__}."
            )

        band = scales.x.band_width
        bar_width = band * (1 - theme.bar_padding)

        # Colors: positive = first palette color, negative = second
        color_positive = theme.palette[0] if len(theme.palette) > 0 else "#2196F3"
        color_negative = theme.palette[1] if len(theme.palette) > 1 else "#F44336"

        primitives: list[Primitive] = []
        running = 0.0

        for i in range(min(len(categories), len(y_vals))):
            step = y_vals[i]
            base = running
            top = running + step
            running = top

            # Bar from base to top (floating)
            y_base_px = scales.y.map(base)
            y_top_px = scales.y.map(top)
            cx = scales.x.map(categories[i])

            bar_y = min(y_base_px, y_top_px)
            bar_h = abs(y_base_px - y_top_px)

            color = color_positive if step >= 0 else color_negative

            primitives.append(
                CompiledBar(
                    px=cx - bar_width / 2,
                    py=bar_y,
                    bar_width=bar_width,
                    bar_height=bar_h,
                    color=color,
                    group="positive" if step >= 0 else "negative",
                )
            )

            if layer.labels:
                label_text = format_label(step, layer.label_format)
                font_size = theme.tick_font_size
                inside = label_fits_inside(
                    label_text,
                    font_size,
                    bar_width,
                    bar_h,
                    font_name=theme.font_name,
                )
                if inside:
                    label_x = cx
                    label_y = bar_y + bar_h / 2 + font_size / 3
                    lum = relative_luminance(color)
                    label_color = "#FFFFFF" if lum < 0.4 else theme.text_color
                elif step >= 0:
                    label_x = cx
                    label_y = bar_y - 5
                    label_color = theme.text_color
                else:
                    label_x = cx
                    label_y = bar_y + bar_h + font_size + 2
                    label_color = theme.text_color

                primitives.append(
                    CompiledText(
                        text=label_text,
                        x=label_x,
                        y=label_y,
                        font_size=font_size,
                        color=label_color,
                        anchor="middle",
                    )
                )

            # Connector line from this bar's top to the next bar's base
            if i < min(len(categories), len(y_vals)) - 1:
                next_cx = scales.x.map(categories[i + 1])
                connector_y = scales.y.map(running)
                primitives.append(
                    CompiledLine(
                        points=[
                            (cx + bar_width / 2, connector_y),
                            (next_cx - bar_width / 2, connector_y),
                        ],
                        color=theme.grid_color,
                        width=1.0,
                    )
                )

        return primitives
