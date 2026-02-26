"""Translate matplotlib scripts to botplotlib.

Reads existing matplotlib scripts and extracts an equivalent PlotSpec
using AST analysis. No matplotlib installation required — your code
is parsed, never executed.

Uses AST parsing (never imports or runs your matplotlib code).

Supported patterns:
- plt.plot(), plt.scatter(), plt.bar(), plt.barh()
- ax.plot(), ax.scatter(), ax.bar(), ax.barh()
- plt.title(), plt.xlabel(), plt.ylabel()
- ax.set_title(), ax.set_xlabel(), ax.set_ylabel()
- plt.figure(figsize=...), plt.subplots(figsize=...)
- plt.legend() / ax.legend()
- plt.savefig() / fig.savefig()
- plt.grid() / ax.grid()
- label= keyword on plot calls (legend entries)
- color=/c= keyword on plot calls
- Format strings in plt.plot() (e.g., 'ro-', 'b--', 'g^')

Also provides to_botplotlib_code() for generating the equivalent
botplotlib one-liner from a matplotlib script.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    LegendSpec,
    PlotSpec,
    SizeSpec,
)

# Matplotlib format string regex: optional color, optional marker, optional linestyle
# Examples: 'ro', 'b--', 'g^-', 'k', '--', 'r-.'
_FMT_COLOR_MAP: dict[str, str] = {
    "b": "#1f77b4",  # blue
    "g": "#2ca02c",  # green
    "r": "#d62728",  # red
    "c": "#17becf",  # cyan
    "m": "#9467bd",  # magenta
    "y": "#bcbd22",  # yellow
    "k": "#000000",  # black
    "w": "#ffffff",  # white
}

_FMT_MARKER_CHARS = set(".,ov^<>1234sp*hH+xXDd|_")

_FMT_LINESTYLES = ["--", "-.", ":", "-"]  # ordered longest-first for matching


def _parse_format_string(fmt: str) -> dict[str, str | None]:
    """Parse a matplotlib format string like 'ro--' into components.

    Returns a dict with keys: color, marker, linestyle (any may be None).
    """
    result: dict[str, str | None] = {"color": None, "marker": None, "linestyle": None}
    remaining = fmt

    # Extract color (single char at start)
    if remaining and remaining[0] in _FMT_COLOR_MAP:
        result["color"] = _FMT_COLOR_MAP[remaining[0]]
        remaining = remaining[1:]

    # Extract marker (single char)
    if remaining and remaining[0] in _FMT_MARKER_CHARS:
        result["marker"] = remaining[0]
        remaining = remaining[1:]

    # Extract linestyle
    for ls in _FMT_LINESTYLES:
        if remaining.startswith(ls):
            result["linestyle"] = ls
            remaining = remaining[len(ls) :]
            break

    return result


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


def to_botplotlib_code(source: str | Path) -> str:
    """Convert a matplotlib script to equivalent botplotlib Python code.

    This produces a human-readable one-liner (or short snippet) that
    demonstrates the token-efficiency of botplotlib vs matplotlib.

    Parameters
    ----------
    source:
        Path to a .py file, or a string of Python code.

    Returns
    -------
    str
        Python code using botplotlib that produces the equivalent plot.
    """
    spec = from_matplotlib(source)
    lines = ["import botplotlib as bpl", ""]

    if not spec.layers:
        lines.append("# No plot calls detected in the matplotlib script")
        return "\n".join(lines)

    # Build data dict
    if spec.data.columns:
        col_strs = []
        for col_name, col_data in spec.data.columns.items():
            col_strs.append(f'    "{col_name}": {col_data!r}')
        lines.append("data = {")
        lines.append(",\n".join(col_strs))
        lines.append("}")
        lines.append("")

    # For single-layer plots, use the convenience API
    if len(spec.layers) == 1:
        layer = spec.layers[0]
        func = layer.geom  # scatter, line, bar
        parts = [f'bpl.{func}(data, x="{layer.x}", y="{layer.y}"']

        if spec.labels.title:
            parts.append(f', title="{spec.labels.title}"')
        if spec.labels.x:
            parts.append(f', x_label="{spec.labels.x}"')
        if spec.labels.y:
            parts.append(f', y_label="{spec.labels.y}"')
        if spec.theme != "default":
            parts.append(f', theme="{spec.theme}"')
        if spec.size.width != 800 or spec.size.height != 500:
            parts.append(f", width={spec.size.width}, height={spec.size.height}")

        parts.append(")")
        lines.append("".join(parts))
    else:
        # Multi-layer: use Figure directly
        lines.append("spec = bpl.PlotSpec(")
        lines.append("    data=bpl.spec.models.DataSpec(columns=data),")
        lines.append("    layers=[")
        for layer in spec.layers:
            lines.append(
                f'        bpl.spec.models.LayerSpec(geom="{layer.geom}", '
                f'x="{layer.x}", y="{layer.y}"),'
            )
        lines.append("    ],")
        if spec.labels.title or spec.labels.x or spec.labels.y:
            title_str = f'"{spec.labels.title}"' if spec.labels.title else "None"
            x_str = f'"{spec.labels.x}"' if spec.labels.x else "None"
            y_str = f'"{spec.labels.y}"' if spec.labels.y else "None"
            lines.append(
                f"    labels=bpl.spec.models.LabelsSpec("
                f"title={title_str}, x={x_str}, y={y_str}),"
            )
        lines.append(")")
        lines.append("fig = bpl.render(spec)")

    # Add save call if savefig was detected
    if hasattr(spec, "_refactor_metadata"):
        meta = spec._refactor_metadata  # type: ignore[attr-defined]
        if meta.get("savefig_path"):
            path = meta["savefig_path"]
            if path.endswith(".png"):
                lines.append(f'fig.save_png("{path}")')
            else:
                svg_path = re.sub(r"\.\w+$", ".svg", path)
                lines.append(f'fig.save_svg("{svg_path}")')

    return "\n".join(lines)


# -- Matplotlib color name mapping (common named colors) --------------------

_NAMED_COLOR_MAP: dict[str, str] = {
    "red": "#D62728",
    "blue": "#1F77B4",
    "green": "#2CA02C",
    "orange": "#FF7F0E",
    "purple": "#9467BD",
    "brown": "#8C564B",
    "pink": "#E377C2",
    "gray": "#7F7F7F",
    "grey": "#7F7F7F",
    "olive": "#BCBD22",
    "cyan": "#17BECF",
    "black": "#000000",
    "white": "#FFFFFF",
    "navy": "#000080",
    "teal": "#008080",
    "maroon": "#800000",
    "coral": "#FF7F50",
    "salmon": "#FA8072",
    "gold": "#FFD700",
    "indigo": "#4B0082",
    "violet": "#EE82EE",
    "tomato": "#FF6347",
    "steelblue": "#4682B4",
    "darkgreen": "#006400",
    "darkblue": "#00008B",
    "darkred": "#8B0000",
    "lightblue": "#ADD8E6",
    "lightgreen": "#90EE90",
    "skyblue": "#87CEEB",
}


def _normalize_color(color_val: Any) -> str | None:
    """Normalize a matplotlib color value to a hex string.

    Handles hex strings, named colors, and single-char color codes.
    """
    if not isinstance(color_val, str):
        return None

    # Already hex
    if color_val.startswith("#"):
        return color_val

    # Single-char matplotlib code
    if len(color_val) == 1 and color_val in _FMT_COLOR_MAP:
        return _FMT_COLOR_MAP[color_val]

    # Named color
    lower = color_val.lower()
    if lower in _NAMED_COLOR_MAP:
        return _NAMED_COLOR_MAP[lower]

    # CSS-style hex without #
    if re.match(r"^[0-9a-fA-F]{6}$", color_val):
        return f"#{color_val}"

    # Return as-is (might be a valid CSS color)
    return color_val


class _MatplotlibExtractor(ast.NodeVisitor):
    """Walk a matplotlib AST and extract plot spec information."""

    def __init__(self) -> None:
        self.layers: list[dict[str, Any]] = []
        self.title: str | None = None
        self.x_label: str | None = None
        self.y_label: str | None = None
        self.data_vars: dict[str, list] = {}

        # New: additional metadata
        self.figsize: tuple[float, float] | None = None
        self.has_legend: bool = False
        self.savefig_path: str | None = None
        self.grid: bool | None = None
        self.layer_labels: list[str] = []  # legend labels from label= kwarg

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._get_call_name(node)
        if func_name is None:
            self.generic_visit(node)
            return

        # Plot type detection
        if func_name in ("plt.scatter", "ax.scatter", "scatter"):
            self._extract_xy_layer(node, "scatter")
        elif func_name in ("plt.plot", "ax.plot", "plot"):
            self._extract_plot_layer(node)
        elif func_name in ("plt.bar", "ax.bar", "bar"):
            self._extract_xy_layer(node, "bar")
        elif func_name in ("plt.barh", "ax.barh", "barh"):
            self._extract_xy_layer(node, "bar")

        # Labels
        elif func_name in ("plt.title", "ax.set_title"):
            self.title = self._get_first_str_arg(node)
        elif func_name in ("plt.xlabel", "ax.set_xlabel"):
            self.x_label = self._get_first_str_arg(node)
        elif func_name in ("plt.ylabel", "ax.set_ylabel"):
            self.y_label = self._get_first_str_arg(node)

        # Figure configuration
        elif func_name in ("plt.figure",):
            self._extract_figsize(node)
        elif func_name in ("plt.subplots",):
            self._extract_figsize(node)

        # Legend
        elif func_name in ("plt.legend", "ax.legend"):
            self.has_legend = True

        # Savefig
        elif func_name in ("plt.savefig", "fig.savefig"):
            self.savefig_path = self._get_first_str_arg(node)

        # Grid
        elif func_name in ("plt.grid", "ax.grid"):
            self._extract_grid(node)

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Track simple variable assignments like `x = [1, 2, 3]`."""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            value = self._try_eval_literal(node.value)
            if isinstance(value, (list, tuple)):
                self.data_vars[name] = list(value)
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

        # Build size from figsize if detected
        size = SizeSpec()
        if self.figsize is not None:
            # matplotlib figsize is in inches at 100 dpi (convention for screen)
            size = SizeSpec(
                width=self.figsize[0] * 100,
                height=self.figsize[1] * 100,
            )

        # Build legend from detected labels or legend() calls
        legend = LegendSpec(
            show=self.has_legend or any(layer.get("label") for layer in self.layers)
        )

        return PlotSpec(
            data=DataSpec(columns=columns),
            layers=layers,
            labels=LabelsSpec(
                title=self.title,
                x=self.x_label,
                y=self.y_label,
            ),
            legend=legend,
            size=size,
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

    def _extract_plot_layer(self, node: ast.Call) -> None:
        """Extract a plt.plot() / ax.plot() layer, handling format strings."""
        # plt.plot() is special: it can have a format string as the 3rd positional arg
        # plt.plot(x, y, 'ro-', label='data')
        # plt.plot(y)  (single arg)
        # plt.plot(x, y)

        args = node.args
        fmt_info: dict[str, str | None] = {
            "color": None,
            "marker": None,
            "linestyle": None,
        }

        # Check if the 3rd positional arg is a format string
        if len(args) >= 3:
            fmt_val = self._try_eval_literal(args[2])
            if isinstance(fmt_val, str) and len(fmt_val) <= 4:
                fmt_info = _parse_format_string(fmt_val)

        # Extract color from keyword args (overrides format string)
        kw_color = self._get_keyword(node, "color") or self._get_keyword(node, "c")
        if kw_color is not None:
            normalized = _normalize_color(kw_color)
            if normalized:
                fmt_info["color"] = normalized

        # Extract label keyword
        label = self._get_keyword(node, "label")

        # Build the layer (reuse _extract_xy_layer for data)
        self._extract_xy_layer(node, "line")

        # Attach extra metadata to the last layer
        if self.layers:
            last = self.layers[-1]
            if fmt_info["color"]:
                last["color"] = fmt_info["color"]
            if label:
                last["label"] = label

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

            if isinstance(x_val, (list, tuple)):
                layer["x_data"] = list(x_val)
                if "x_name" not in layer:
                    layer["x_name"] = "x"
            if isinstance(y_val, (list, tuple)):
                layer["y_data"] = list(y_val)
                if "y_name" not in layer:
                    layer["y_name"] = "y"

        elif len(args) == 1:
            # Single arg is y data, x is implicit range
            y_val = self._try_eval_literal(args[0])
            if isinstance(args[0], ast.Name):
                layer["y_name"] = args[0].id

            if isinstance(y_val, (list, tuple)):
                y_list = list(y_val)
                layer["y_data"] = y_list
                layer["x_data"] = list(range(len(y_list)))
                layer["x_name"] = "x"
                if "y_name" not in layer:
                    layer["y_name"] = "y"

        # Extract common keyword args (for non-plot calls;
        # plot() handles its own via _extract_plot_layer)
        if geom != "line":  # line is handled by _extract_plot_layer
            kw_color = self._get_keyword(node, "color") or self._get_keyword(node, "c")
            if kw_color is not None:
                normalized = _normalize_color(kw_color)
                if normalized:
                    layer["color"] = normalized

            label = self._get_keyword(node, "label")
            if label:
                layer["label"] = label

        self.layers.append(layer)

    def _extract_figsize(self, node: ast.Call) -> None:
        """Extract figsize from plt.figure() or plt.subplots()."""
        figsize = self._get_keyword(node, "figsize")
        if isinstance(figsize, (list, tuple)) and len(figsize) == 2:
            try:
                self.figsize = (float(figsize[0]), float(figsize[1]))
            except (ValueError, TypeError):
                pass

    def _extract_grid(self, node: ast.Call) -> None:
        """Extract grid configuration from plt.grid() or ax.grid()."""
        # plt.grid(True), plt.grid(False), plt.grid()
        if node.args:
            val = self._try_eval_literal(node.args[0])
            if isinstance(val, bool):
                self.grid = val
            else:
                # plt.grid() with no args toggles it on
                self.grid = True
        else:
            self.grid = True

    def _get_first_str_arg(self, node: ast.Call) -> str | None:
        """Extract the first string argument from a function call."""
        if node.args:
            val = self._try_eval_literal(node.args[0])
            if isinstance(val, str):
                return val
        return None

    def _get_keyword(self, node: ast.Call, name: str) -> Any:
        """Extract a keyword argument value from a function call."""
        for kw in node.keywords:
            if kw.arg == name:
                return self._try_eval_literal(kw.value)
        return None

    def _try_eval_literal(self, node: ast.expr) -> Any:
        """Try to evaluate an AST node as a literal value."""
        try:
            return ast.literal_eval(node)
        except (ValueError, TypeError):
            return None
