"""Compiled geometry primitive types.

These are the atoms of botplotlib's rendering pipeline. Every geom
produces a list of these primitives; the renderer draws them.

New geom types never need new primitives -- they compose from these
existing types. See AGENTS.md for the geom recipe.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from botplotlib._types import Rect, TickMark
from botplotlib.spec.theme import ThemeSpec

# ---------------------------------------------------------------------------
# Primitive types
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
class CompiledPath:
    """An arbitrary SVG path.

    Used for area charts, Sankey curves, violin shapes, and any geom
    that needs freeform geometry beyond rects/circles/polylines.
    """

    d: str  # SVG path data string
    fill: str = "none"
    stroke: str = "none"
    stroke_width: float = 1.0
    opacity: float = 1.0
    group: str | None = None


@dataclass
class CompiledLegendEntry:
    """A legend entry."""

    label: str
    color: str


# Union of all renderable primitives
Primitive = Union[CompiledPoint, CompiledLine, CompiledBar, CompiledText, CompiledPath]


# ---------------------------------------------------------------------------
# CompiledPlot
# ---------------------------------------------------------------------------


@dataclass
class CompiledPlot:
    """Fully positioned geometry ready for rendering."""

    width: float
    height: float
    theme: ThemeSpec
    plot_area: Rect

    # Unified primitives list (new architecture)
    primitives: list[Primitive] = field(default_factory=list)

    # Legacy typed lists (backward compat with current renderer)
    points: list[CompiledPoint] = field(default_factory=list)
    lines: list[CompiledLine] = field(default_factory=list)
    bars: list[CompiledBar] = field(default_factory=list)

    x_ticks: list[TickMark] = field(default_factory=list)
    y_ticks: list[TickMark] = field(default_factory=list)
    texts: list[CompiledText] = field(default_factory=list)
    legend_entries: list[CompiledLegendEntry] = field(default_factory=list)
    legend_area: Rect | None = None
    clip_id: str = "plot-clip"

    def add_primitive(self, prim: Primitive) -> None:
        """Add a primitive to both the unified list and the legacy typed list."""
        self.primitives.append(prim)
        if isinstance(prim, CompiledPoint):
            self.points.append(prim)
        elif isinstance(prim, CompiledLine):
            self.lines.append(prim)
        elif isinstance(prim, CompiledBar):
            self.bars.append(prim)
        elif isinstance(prim, CompiledText):
            self.texts.append(prim)
        # CompiledPath goes only in primitives (renderer generalization handles it)
