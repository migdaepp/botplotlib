"""Figure class — the main user-facing object for a rendered plot.

Wraps a CompiledPlot and provides save/show/repr methods.
"""

from __future__ import annotations

from pathlib import Path

from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.render.svg_renderer import render_svg
from botplotlib.spec.models import LayerSpec, PlotSpec


class Figure:
    """A rendered plot that can be saved, displayed, or inspected.

    Typically created via the convenience functions in ``botplotlib._api``
    (e.g., ``bpl.scatter()``, ``bpl.line()``, ``bpl.bar()``).
    """

    def __init__(self, spec: PlotSpec) -> None:
        self._spec = spec
        self._compiled: CompiledPlot | None = None
        self._svg: str | None = None

    # -- Lazy compilation/rendering ------------------------------------------

    @property
    def compiled(self) -> CompiledPlot:
        if self._compiled is None:
            self._compiled = compile_spec(self._spec)
        return self._compiled

    def to_svg(self) -> str:
        """Return the plot as an SVG string."""
        if self._svg is None:
            self._svg = render_svg(self.compiled)
        return self._svg

    # -- Save methods --------------------------------------------------------

    def save_svg(self, path: str | Path) -> None:
        """Save the plot as an SVG file."""
        Path(path).write_text(self.to_svg())

    def save_png(self, path: str | Path) -> None:
        """Save the plot as a PNG file. Requires ``botplotlib[png]``."""
        from botplotlib.render.png import svg_to_png

        svg_to_png(self.to_svg(), str(path))

    # -- Jupyter integration -------------------------------------------------

    def _repr_svg_(self) -> str:
        """Jupyter inline display hook."""
        return self.to_svg()

    # -- Spec access ---------------------------------------------------------

    @property
    def spec(self) -> PlotSpec:
        """Return the underlying PlotSpec."""
        return self._spec

    # -- Mutation helpers for layered API ------------------------------------

    def _invalidate(self) -> None:
        """Clear cached compilation/rendering after spec mutation."""
        self._compiled = None
        self._svg = None

    @property
    def title(self) -> str | None:
        return self._spec.labels.title

    @title.setter
    def title(self, value: str | None) -> None:
        self._spec.labels.title = value
        self._invalidate()

    def add_scatter(self, x: str, y: str, color: str | None = None) -> Figure:
        """Add a scatter layer."""
        self._spec.layers.append(LayerSpec(geom="scatter", x=x, y=y, color=color))
        self._invalidate()
        return self

    def add_line(self, x: str, y: str, color: str | None = None) -> Figure:
        """Add a line layer."""
        self._spec.layers.append(LayerSpec(geom="line", x=x, y=y, color=color))
        self._invalidate()
        return self

    def add_bar(self, x: str, y: str, color: str | None = None) -> Figure:
        """Add a bar layer."""
        self._spec.layers.append(LayerSpec(geom="bar", x=x, y=y, color=color))
        self._invalidate()
        return self
