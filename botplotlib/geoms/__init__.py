"""Geom plugin architecture for botplotlib.

Every plot type (scatter, line, bar, waterfall, ...) is a Geom: a pure,
deterministic function that maps data + intent into geometric primitives.
The compiler dispatches to the geom registry; the renderer draws primitives.

To add a new geom, see the recipe in AGENTS.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from botplotlib.geoms.primitives import Primitive

if TYPE_CHECKING:
    from botplotlib._types import Rect
    from botplotlib.spec.models import LayerSpec
    from botplotlib.spec.scales import CategoricalScale, LinearScale
    from botplotlib.spec.theme import ThemeSpec


# ---------------------------------------------------------------------------
# Scale interface
# ---------------------------------------------------------------------------


@dataclass
class ScaleHint:
    """What a geom layer contributes to scale computation.

    The compiler collects ScaleHints from all layers, merges numeric
    ranges, and computes unified scales before calling geom.compile().
    """

    x_type: str = "numeric"  # "numeric" or "categorical"
    y_type: str = "numeric"
    x_numeric: list[float] = field(default_factory=list)
    y_numeric: list[float] = field(default_factory=list)
    x_categories: list[str] = field(default_factory=list)


@dataclass
class ResolvedScales:
    """Scales computed by the compiler, passed to geom.compile()."""

    x: LinearScale | CategoricalScale
    y: LinearScale
    color_map: dict[str, str] = field(default_factory=dict)
    default_color: str = "#1f77b4"


# ---------------------------------------------------------------------------
# Geom base class
# ---------------------------------------------------------------------------


class Geom(ABC):
    """Base class for plot geometries.

    Subclass this and implement validate(), scale_hint(), and compile()
    to create a new plot type. See AGENTS.md for the step-by-step recipe.
    """

    name: str  # e.g., "scatter", "waterfall"

    @abstractmethod
    def validate(self, layer: LayerSpec, data: dict[str, list]) -> None:
        """Validate that data has the columns this geom requires.

        Raise ValueError with a clear, actionable message if validation fails.
        """

    @abstractmethod
    def scale_hint(self, layer: LayerSpec, data: dict[str, list]) -> ScaleHint:
        """Declare what scales this geom needs and contribute data ranges.

        The compiler calls this on every layer before computing scales.
        Numeric geoms return their x/y values; categorical geoms return
        their categories.
        """

    @abstractmethod
    def compile(
        self,
        layer: LayerSpec,
        data: dict[str, list],
        scales: ResolvedScales,
        theme: ThemeSpec,
        plot_area: Rect,
    ) -> list[Primitive]:
        """Transform data into positioned geometric primitives.

        Returns a list of Primitive objects (CompiledPoint, CompiledLine,
        CompiledBar, CompiledText, CompiledPath). The renderer draws them.
        """


# ---------------------------------------------------------------------------
# Geom registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, Geom] = {}


def register_geom(geom: Geom) -> None:
    """Register a geom instance by name."""
    _REGISTRY[geom.name] = geom


def get_geom(name: str) -> Geom:
    """Look up a registered geom by name.

    Raises ValueError with available geoms listed if not found.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(
            f"Unknown geom '{name}'. Available geoms: {available}. "
            "See AGENTS.md for how to add new geoms."
        )
    return _REGISTRY[name]


def registered_geoms() -> dict[str, Geom]:
    """Return a copy of the geom registry."""
    return dict(_REGISTRY)


# ---------------------------------------------------------------------------
# Register built-in geoms
# ---------------------------------------------------------------------------


def _register_builtins() -> None:
    """Register the built-in geoms (scatter, line, bar, waterfall)."""
    from botplotlib.geoms.bar import BarGeom
    from botplotlib.geoms.line import LineGeom
    from botplotlib.geoms.scatter import ScatterGeom
    from botplotlib.geoms.waterfall import WaterfallGeom

    register_geom(ScatterGeom())
    register_geom(LineGeom())
    register_geom(BarGeom())
    register_geom(WaterfallGeom())


_register_builtins()
