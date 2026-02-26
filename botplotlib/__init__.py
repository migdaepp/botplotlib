"""botplotlib — Beautiful plots, simple API, no matplotlib."""

from botplotlib._api import bar, line, plot, render, scatter, waterfall
from botplotlib.figure import Figure
from botplotlib.spec.models import PlotSpec

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "bar",
    "line",
    "plot",
    "render",
    "scatter",
    "waterfall",
    "Figure",
    "PlotSpec",
]
