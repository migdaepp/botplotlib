"""Bar geom — positioned rectangles on a categorical x-axis."""

from __future__ import annotations

from botplotlib._types import Rect
from botplotlib.geoms import Geom, ResolvedScales, ScaleHint
from botplotlib.geoms.primitives import CompiledBar, Primitive
from botplotlib.spec.models import LayerSpec
from botplotlib.spec.scales import CategoricalScale
from botplotlib.spec.theme import ThemeSpec


class BarGeom(Geom):
    """Bar chart: vertical bars on categorical x-axis."""

    name = "bar"

    def validate(self, layer: LayerSpec, data: dict[str, list]) -> None:
        for col_name, role in [(layer.x, "x"), (layer.y, "y")]:
            if col_name not in data:
                raise ValueError(
                    f"Bar geom requires column '{col_name}' for {role} axis, "
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
        # Include 0 baseline — bar charts always start from zero
        return ScaleHint(
            x_type="categorical",
            y_type="numeric",
            x_categories=categories,
            y_numeric=[0.0] + y_vals,
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
        color_col = (
            [str(v) for v in data[layer.color]]
            if layer.color and layer.color in data
            else None
        )

        if not isinstance(scales.x, CategoricalScale):
            raise TypeError(
                f"Bar geom requires a CategoricalScale for x-axis, "
                f"got {type(scales.x).__name__}."
            )

        band = scales.x.band_width
        bar_width = band * (1 - theme.bar_padding)
        baseline = scales.y.map(0)

        primitives: list[Primitive] = []
        for i in range(min(len(categories), len(y_vals))):
            cx = scales.x.map(categories[i])
            y_px = scales.y.map(y_vals[i])
            color = (
                scales.color_map.get(color_col[i], scales.default_color)
                if color_col
                else scales.default_color
            )
            primitives.append(
                CompiledBar(
                    px=cx - bar_width / 2,
                    py=min(y_px, baseline),
                    bar_width=bar_width,
                    bar_height=abs(baseline - y_px),
                    color=color,
                    group=color_col[i] if color_col else None,
                )
            )
        return primitives
