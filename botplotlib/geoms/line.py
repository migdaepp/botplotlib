"""Line geom — positioned polylines."""

from __future__ import annotations

from botplotlib._types import Rect
from botplotlib.geoms import Geom, ResolvedScales, ScaleHint
from botplotlib.geoms.primitives import CompiledLine, Primitive
from botplotlib.spec.models import LayerSpec
from botplotlib.spec.theme import ThemeSpec


class LineGeom(Geom):
    """Line plot: connected polylines, optionally grouped by color."""

    name = "line"

    def validate(self, layer: LayerSpec, data: dict[str, list]) -> None:
        for col_name, role in [(layer.x, "x"), (layer.y, "y")]:
            if col_name not in data:
                raise ValueError(
                    f"Line geom requires column '{col_name}' for {role} axis, "
                    f"but data has columns: {sorted(data.keys())}."
                )

    def scale_hint(self, layer: LayerSpec, data: dict[str, list]) -> ScaleHint:
        x_numeric: list[float] = []
        y_numeric: list[float] = []
        for v in data.get(layer.x, []):
            try:
                x_numeric.append(float(v))
            except (ValueError, TypeError):
                pass
        for v in data.get(layer.y, []):
            try:
                y_numeric.append(float(v))
            except (ValueError, TypeError):
                pass
        return ScaleHint(
            x_type="numeric",
            y_type="numeric",
            x_numeric=x_numeric,
            y_numeric=y_numeric,
        )

    def compile(
        self,
        layer: LayerSpec,
        data: dict[str, list],
        scales: ResolvedScales,
        theme: ThemeSpec,
        plot_area: Rect,
    ) -> list[Primitive]:
        x_vals = [float(v) for v in data[layer.x]]
        y_vals = [float(v) for v in data[layer.y]]
        color_col = (
            [str(v) for v in data[layer.color]]
            if layer.color and layer.color in data
            else None
        )

        primitives: list[Primitive] = []

        if color_col:
            # Group by color
            groups: dict[str, list[tuple[float, float]]] = {}
            for i in range(min(len(x_vals), len(y_vals))):
                g = color_col[i]
                if g not in groups:
                    groups[g] = []
                groups[g].append((scales.x.map(x_vals[i]), scales.y.map(y_vals[i])))
            for g, pts in groups.items():
                primitives.append(
                    CompiledLine(
                        points=pts,
                        color=scales.color_map.get(g, scales.default_color),
                        width=theme.line_width,
                        group=g,
                    )
                )
        else:
            pts = [
                (scales.x.map(x_vals[i]), scales.y.map(y_vals[i]))
                for i in range(min(len(x_vals), len(y_vals)))
            ]
            primitives.append(
                CompiledLine(
                    points=pts,
                    color=scales.default_color,
                    width=theme.line_width,
                )
            )

        return primitives
