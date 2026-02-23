"""Pydantic v2 spec models for the botplotlib spec-compile-render pipeline.

Every model is JSON-serializable and round-trips through
``.model_dump_json()`` / ``.model_validate_json()``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SizeSpec(BaseModel):
    """Canvas size in pixels."""

    width: float = 800
    height: float = 500


class LabelsSpec(BaseModel):
    """Plot labels."""

    title: str | None = None
    x: str | None = None
    y: str | None = None


class LegendSpec(BaseModel):
    """Legend configuration."""

    show: bool = True
    position: Literal["top", "bottom", "left", "right"] = "right"


class LayerSpec(BaseModel):
    """A single plot layer (scatter, line, or bar)."""

    geom: str  # validated against geom registry at compile time
    x: str  # column name for x axis
    y: str  # column name for y axis
    color: str | None = None  # column name for color grouping


class DataSpec(BaseModel):
    """Columnar data attached to a plot spec."""

    columns: dict[str, list] = Field(default_factory=dict)


class PlotSpec(BaseModel):
    """Complete specification for a plot.

    JSON-serializable, round-trips through
    ``.model_dump_json()`` / ``.model_validate_json()``.
    """

    data: DataSpec = Field(default_factory=DataSpec)
    layers: list[LayerSpec] = Field(default_factory=list)
    labels: LabelsSpec = Field(default_factory=LabelsSpec)
    legend: LegendSpec = Field(default_factory=LegendSpec)
    size: SizeSpec = Field(default_factory=SizeSpec)
    theme: str = "default"  # theme name (resolved at compile time)
