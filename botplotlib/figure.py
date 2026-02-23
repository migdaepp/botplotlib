"""Figure class — the main user-facing object for a rendered plot.

Wraps a CompiledPlot and provides save/show/repr methods.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.render.svg_renderer import render_svg
from botplotlib.spec.models import LayerSpec, PlotSpec


class Figure:
    """A rendered plot that can be saved, displayed, or inspected.

    Typically created via the convenience functions in ``botplotlib._api``
    (e.g., ``bpl.scatter()``, ``bpl.line()``, ``bpl.bar()``).

    Agent / JSON path:
        ``Figure.from_json(json_string)`` — parse a PlotSpec JSON string.
        ``Figure.from_dict(d)`` — construct from a plain dict (typical LLM
        function-call output format).
    """

    def __init__(self, spec: PlotSpec) -> None:
        self._spec = spec
        self._compiled: CompiledPlot | None = None
        self._svg: str | None = None

    # -- Agent / JSON path ---------------------------------------------------

    @classmethod
    def from_json(cls, json_string: str) -> "Figure":
        """Construct a Figure from a PlotSpec JSON string.

        Validates the JSON with Pydantic and raises ``ValidationError`` on
        invalid input.  This is the primary entry point for the agent / JSON
        path — LLMs can generate a PlotSpec JSON string directly and hand it
        off to this method.

        Parameters
        ----------
        json_string:
            A JSON string that conforms to the PlotSpec schema.

        Raises
        ------
        pydantic.ValidationError
            If the JSON does not match the PlotSpec schema.
        json.JSONDecodeError
            If ``json_string`` is not valid JSON.
        """
        spec = PlotSpec.model_validate_json(json_string)
        return cls(spec)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Figure":
        """Construct a Figure from a plain dict.

        Validates the dict with Pydantic and raises ``ValidationError`` on
        invalid input.  This is the typical entry point when an LLM returns a
        PlotSpec as structured output (e.g., a function-call response dict).

        Parameters
        ----------
        d:
            A dict that conforms to the PlotSpec schema.

        Raises
        ------
        pydantic.ValidationError
            If the dict does not match the PlotSpec schema.
        """
        spec = PlotSpec.model_validate(d)
        return cls(spec)

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

    @property
    def subtitle(self) -> str | None:
        return self._spec.labels.subtitle

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self._spec.labels.subtitle = value
        self._invalidate()

    @property
    def footnote(self) -> str | None:
        return self._spec.labels.footnote

    @footnote.setter
    def footnote(self, value: str | None) -> None:
        self._spec.labels.footnote = value
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

    def add_bar(
        self,
        x: str,
        y: str,
        color: str | None = None,
        labels: bool = False,
        label_format: str | None = None,
    ) -> Figure:
        """Add a bar layer."""
        self._spec.layers.append(
            LayerSpec(
                geom="bar",
                x=x,
                y=y,
                color=color,
                labels=labels,
                label_format=label_format,
            )
        )
        self._invalidate()
        return self
