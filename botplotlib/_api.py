"""Flat convenience API for botplotlib.

Provides the top-level functions: scatter(), line(), bar(), plot(), render().
"""

from __future__ import annotations

from typing import Any

from botplotlib.compiler.data_prep import normalize_data
from botplotlib.figure import Figure
from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    LegendSpec,
    PlotSpec,
    SizeSpec,
)


def _build_figure(
    data: Any,
    x: str,
    y: str,
    geom: str,
    color: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    footnote: str | None = None,
    theme: str = "default",
    width: float = 800,
    height: float = 500,
    labels: bool = False,
    label_format: str | None = None,
) -> Figure:
    """Internal helper to build a Figure from common arguments."""
    columns = normalize_data(data)
    spec = PlotSpec(
        data=DataSpec(columns=columns),
        layers=[
            LayerSpec(
                geom=geom,
                x=x,
                y=y,
                color=color,
                labels=labels,
                label_format=label_format,
            )
        ],
        labels=LabelsSpec(
            title=title,
            subtitle=subtitle,
            x=x_label if x_label is not None else x,
            y=y_label if y_label is not None else y,
            footnote=footnote,
        ),
        legend=LegendSpec(show=color is not None),
        size=SizeSpec(width=width, height=height),
        theme=theme,
    )
    return Figure(spec)


def scatter(
    data: Any,
    x: str,
    y: str,
    *,
    color: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    footnote: str | None = None,
    theme: str = "default",
    width: float = 800,
    height: float = 500,
) -> Figure:
    """Create a scatter plot.

    Parameters
    ----------
    data:
        Input data (dict, list[dict], DataFrame, etc.).
    x:
        Column name for the x axis.
    y:
        Column name for the y axis.
    color:
        Column name for color grouping (optional).
    title:
        Plot title (optional).
    subtitle:
        Subtitle below the title (optional).
    footnote:
        Footer text below the plot (optional).
    theme:
        Theme name (default, bluesky, substack, print, magazine).
    """
    return _build_figure(
        data,
        x,
        y,
        "scatter",
        color=color,
        title=title,
        subtitle=subtitle,
        x_label=x_label,
        y_label=y_label,
        footnote=footnote,
        theme=theme,
        width=width,
        height=height,
    )


def line(
    data: Any,
    x: str,
    y: str,
    *,
    color: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    footnote: str | None = None,
    theme: str = "default",
    width: float = 800,
    height: float = 500,
) -> Figure:
    """Create a line plot.

    Parameters
    ----------
    data:
        Input data (dict, list[dict], DataFrame, etc.).
    x:
        Column name for the x axis.
    y:
        Column name for the y axis.
    color:
        Column name for color grouping (optional).
    title:
        Plot title (optional).
    subtitle:
        Subtitle below the title (optional).
    footnote:
        Footer text below the plot (optional).
    theme:
        Theme name (default, bluesky, substack, print, magazine).
    """
    return _build_figure(
        data,
        x,
        y,
        "line",
        color=color,
        title=title,
        subtitle=subtitle,
        x_label=x_label,
        y_label=y_label,
        footnote=footnote,
        theme=theme,
        width=width,
        height=height,
    )


def bar(
    data: Any,
    x: str,
    y: str,
    *,
    color: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    footnote: str | None = None,
    theme: str = "default",
    width: float = 800,
    height: float = 500,
    labels: bool = False,
    label_format: str | None = None,
) -> Figure:
    """Create a bar chart.

    Parameters
    ----------
    data:
        Input data (dict, list[dict], DataFrame, etc.).
    x:
        Column name for the x (category) axis.
    y:
        Column name for the y (value) axis.
    color:
        Column name for color grouping (optional).
    title:
        Plot title (optional).
    subtitle:
        Subtitle below the title (optional).
    footnote:
        Footer text below the plot (optional).
    theme:
        Theme name (default, bluesky, substack, print, magazine).
    labels:
        Show value labels on bars (default False).
    label_format:
        Python format string for labels, e.g. "${:,.0f}".
    """
    return _build_figure(
        data,
        x,
        y,
        "bar",
        color=color,
        title=title,
        subtitle=subtitle,
        x_label=x_label,
        y_label=y_label,
        footnote=footnote,
        theme=theme,
        width=width,
        height=height,
        labels=labels,
        label_format=label_format,
    )


def plot(data: Any, *, theme: str = "default", **kwargs: Any) -> Figure:
    """Create an empty figure for layered composition.

    Use ``fig.add_scatter()``, ``fig.add_line()``, ``fig.add_bar()``
    to add layers.

    Parameters
    ----------
    data:
        Input data (dict, list[dict], DataFrame, etc.).
    theme:
        Theme name.
    """
    columns = normalize_data(data)
    spec = PlotSpec(
        data=DataSpec(columns=columns),
        theme=theme,
    )
    return Figure(spec)


def waterfall(
    data: Any,
    x: str,
    y: str,
    *,
    title: str | None = None,
    subtitle: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
    footnote: str | None = None,
    theme: str = "default",
    width: float = 800,
    height: float = 500,
    labels: bool = False,
    label_format: str | None = None,
) -> Figure:
    """Create a waterfall chart.

    Parameters
    ----------
    data:
        Input data (dict, list[dict], DataFrame, etc.).
    x:
        Column name for category labels (e.g., "Revenue", "COGS").
    y:
        Column name for step values (positive = increase, negative = decrease).
    title:
        Plot title (optional).
    subtitle:
        Subtitle below the title (optional).
    footnote:
        Footer text below the plot (optional).
    theme:
        Theme name (default, bluesky, substack, print, magazine).
    labels:
        Show value labels on bars (default False).
    label_format:
        Python format string for labels, e.g. "${:,.0f}".
    """
    return _build_figure(
        data,
        x,
        y,
        "waterfall",
        title=title,
        subtitle=subtitle,
        x_label=x_label,
        y_label=y_label,
        footnote=footnote,
        theme=theme,
        width=width,
        height=height,
        labels=labels,
        label_format=label_format,
    )


def render(spec: PlotSpec) -> Figure:
    """Render a PlotSpec into a Figure.

    Parameters
    ----------
    spec:
        A PlotSpec object (e.g., from the matplotlib refactor tool).
    """
    return Figure(spec)
