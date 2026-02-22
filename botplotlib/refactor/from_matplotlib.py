"""Auto-refactor: convert matplotlib scripts to botplotlib PlotSpec.

Reads a simple matplotlib script via AST parsing, identifies plot type,
data, and styling, and outputs an equivalent PlotSpec.

Supported patterns:
- plt.plot(), plt.scatter(), plt.bar()
- ax.plot(), ax.scatter(), ax.bar()
- plt.title(), plt.xlabel(), plt.ylabel()
- ax.set_title(), ax.set_xlabel(), ax.set_ylabel()
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    PlotSpec,
)


def from_matplotlib(source: str | Path) -> PlotSpec:
    """Convert a matplotlib script to a botplotlib PlotSpec.

    Parameters
    ----------
    source:
        Path to a .py file, or a string of Python code.

    Returns
    -------
    PlotSpec
        An equivalent plot specification.
    """
    if isinstance(source, Path) or (
        isinstance(source, str) and source.endswith(".py") and "\n" not in source
    ):
        code = Path(source).read_text()
    else:
        code = source

    tree = ast.parse(code)
    extractor = _MatplotlibExtractor()
    extractor.visit(tree)
    return extractor.to_spec()


class _MatplotlibExtractor(ast.NodeVisitor):
    """Walk a matplotlib AST and extract plot spec information."""

    def __init__(self) -> None:
        self.layers: list[dict[str, Any]] = []
        self.title: str | None = None
        self.x_label: str | None = None
        self.y_label: str | None = None
        self.data_vars: dict[str, list] = {}

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_call_name(node)
        if func_name is None:
            self.generic_visit(node)
            return

        # Plot type detection
        if func_name in ("plt.scatter", "ax.scatter", "scatter"):
            self._extract_xy_layer(node, "scatter")
        elif func_name in ("plt.plot", "ax.plot", "plot"):
            self._extract_xy_layer(node, "line")
        elif func_name in ("plt.bar", "ax.bar", "bar"):
            self._extract_xy_layer(node, "bar")

        # Labels
        elif func_name in ("plt.title", "ax.set_title"):
            self.title = self._get_first_str_arg(node)
        elif func_name in ("plt.xlabel", "ax.set_xlabel"):
            self.x_label = self._get_first_str_arg(node)
        elif func_name in ("plt.ylabel", "ax.set_ylabel"):
            self.y_label = self._get_first_str_arg(node)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track simple variable assignments like `x = [1, 2, 3]`."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            value = self._try_eval_literal(node.value)
            if isinstance(value, list):
                self.data_vars[name] = value
        self.generic_visit(node)

    def to_spec(self) -> PlotSpec:
        """Build a PlotSpec from the extracted information."""
        columns: dict[str, list] = {}
        layers: list[LayerSpec] = []

        for i, layer in enumerate(self.layers):
            geom = layer["geom"]
            x_name = layer.get("x_name", f"x_{i}")
            y_name = layer.get("y_name", f"y_{i}")

            # Resolve data
            x_data = layer.get("x_data")
            y_data = layer.get("y_data")

            if x_data is None and x_name in self.data_vars:
                x_data = self.data_vars[x_name]
            if y_data is None and y_name in self.data_vars:
                y_data = self.data_vars[y_name]

            if x_data is not None:
                columns[x_name] = x_data
            if y_data is not None:
                columns[y_name] = y_data

            layers.append(LayerSpec(geom=geom, x=x_name, y=y_name))

        return PlotSpec(
            data=DataSpec(columns=columns),
            layers=layers,
            labels=LabelsSpec(
                title=self.title,
                x=self.x_label,
                y=self.y_label,
            ),
        )

    # -- Helpers -------------------------------------------------------------

    def _get_call_name(self, node: ast.Call) -> str | None:
        """Extract the dotted function name from a Call node."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return None

    def _extract_xy_layer(self, node: ast.Call, geom: str) -> None:
        """Extract x, y data from a plot call."""
        layer: dict[str, Any] = {"geom": geom}

        args = node.args
        if len(args) >= 2:
            # First two positional args are x, y
            x_val = self._try_eval_literal(args[0])
            y_val = self._try_eval_literal(args[1])

            if isinstance(args[0], ast.Name):
                layer["x_name"] = args[0].id
            if isinstance(args[1], ast.Name):
                layer["y_name"] = args[1].id

            if isinstance(x_val, list):
                layer["x_data"] = x_val
                if "x_name" not in layer:
                    layer["x_name"] = "x"
            if isinstance(y_val, list):
                layer["y_data"] = y_val
                if "y_name" not in layer:
                    layer["y_name"] = "y"

        elif len(args) == 1:
            # Single arg is y data, x is implicit range
            y_val = self._try_eval_literal(args[0])
            if isinstance(args[0], ast.Name):
                layer["y_name"] = args[0].id

            if isinstance(y_val, list):
                layer["y_data"] = y_val
                layer["x_data"] = list(range(len(y_val)))
                layer["x_name"] = "x"
                if "y_name" not in layer:
                    layer["y_name"] = "y"

        self.layers.append(layer)

    def _get_first_str_arg(self, node: ast.Call) -> str | None:
        """Extract the first string argument from a function call."""
        if node.args:
            val = self._try_eval_literal(node.args[0])
            if isinstance(val, str):
                return val
        return None

    def _try_eval_literal(self, node: ast.expr) -> Any:
        """Try to evaluate an AST node as a literal value."""
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError):
            return None
