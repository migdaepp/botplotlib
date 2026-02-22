"""botplotlib — Beautiful plots, simple API, no matplotlib."""

from botplotlib._api import bar, line, plot, render, scatter
from botplotlib.figure import Figure
from botplotlib.spec.models import PlotSpec

__all__ = [
    "bar",
    "line",
    "plot",
    "render",
    "scatter",
    "Figure",
    "PlotSpec",
]
