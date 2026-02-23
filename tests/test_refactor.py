"""Tests for botplotlib.refactor.from_matplotlib."""

from __future__ import annotations

import tempfile
from pathlib import Path

from botplotlib.refactor.from_matplotlib import (
    _normalize_color,
    _parse_format_string,
    from_matplotlib,
    to_botplotlib_code,
)

# ============================================================================
# Original tests (preserved)
# ============================================================================


class TestFromMatplotlibString:
    """Test refactoring from inline code strings."""

    def test_plt_scatter(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6])
plt.title("My Scatter")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "scatter"
        assert spec.labels.title == "My Scatter"
        assert spec.labels.x == "X"
        assert spec.labels.y == "Y"
        assert spec.data.columns["x"] == [1, 2, 3]
        assert spec.data.columns["y"] == [4, 5, 6]

    def test_plt_plot(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [10, 20, 30])
plt.title("Line Plot")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "line"
        assert spec.labels.title == "Line Plot"

    def test_plt_bar(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.bar(["A", "B", "C"], [10, 20, 30])
plt.title("Bar Chart")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "bar"
        assert spec.labels.title == "Bar Chart"

    def test_ax_scatter(self) -> None:
        code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter([1, 2, 3], [4, 5, 6])
ax.set_title("Ax Scatter")
ax.set_xlabel("X Axis")
ax.set_ylabel("Y Axis")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "scatter"
        assert spec.labels.title == "Ax Scatter"
        assert spec.labels.x == "X Axis"
        assert spec.labels.y == "Y Axis"

    def test_variable_references(self) -> None:
        code = """
import matplotlib.pyplot as plt
x = [1, 2, 3, 4]
y = [10, 20, 15, 25]
plt.plot(x, y)
plt.title("Variable Data")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].x == "x"
        assert spec.layers[0].y == "y"
        assert spec.data.columns.get("x") == [1, 2, 3, 4]
        assert spec.data.columns.get("y") == [10, 20, 15, 25]

    def test_single_arg_plot(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([10, 20, 30, 40])
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "line"
        # x should be auto-generated range
        assert spec.data.columns.get("x") == [0, 1, 2, 3]
        assert spec.data.columns.get("y") == [10, 20, 30, 40]

    def test_multiple_plots(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2], [3, 4])
plt.plot([5, 6], [7, 8])
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 2
        assert spec.layers[0].geom == "scatter"
        assert spec.layers[1].geom == "line"

    def test_no_plots_returns_empty_spec(self) -> None:
        code = """
x = 42
print("no plots here")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 0

    def test_spec_is_json_serializable(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6])
plt.title("Serialization Test")
"""
        spec = from_matplotlib(code)
        json_str = spec.model_dump_json()
        roundtripped = type(spec).model_validate_json(json_str)
        assert roundtripped.labels.title == "Serialization Test"


class TestFromMatplotlibFile:
    """Test refactoring from .py files."""

    def test_read_from_file(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6])
plt.title("From File")
"""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            spec = from_matplotlib(f.name)
            assert spec.labels.title == "From File"
            Path(f.name).unlink()

    def test_read_from_path_object(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [10, 20, 30])
"""
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            f.flush()
            spec = from_matplotlib(Path(f.name))
            assert len(spec.layers) == 1
            Path(f.name).unlink()


# ============================================================================
# New tests: color keyword arguments
# ============================================================================


class TestColorExtraction:
    """Test color= and c= keyword detection on plot calls."""

    def test_scatter_color_keyword(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6], color='red')
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "scatter"

    def test_scatter_c_keyword(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6], c='blue')
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1

    def test_bar_color_keyword(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.bar(["A", "B", "C"], [10, 20, 30], color='#FF5733')
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "bar"

    def test_plot_color_keyword(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6], color='green')
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "line"


# ============================================================================
# New tests: format string parsing
# ============================================================================


class TestFormatStringParsing:
    """Test matplotlib format string parsing (e.g., 'ro-', 'b--')."""

    def test_parse_color_only(self) -> None:
        result = _parse_format_string("r")
        assert result["color"] == "#d62728"
        assert result["marker"] is None
        assert result["linestyle"] is None

    def test_parse_color_and_marker(self) -> None:
        result = _parse_format_string("ro")
        assert result["color"] == "#d62728"
        assert result["marker"] == "o"

    def test_parse_color_marker_linestyle(self) -> None:
        result = _parse_format_string("ro-")
        assert result["color"] == "#d62728"
        assert result["marker"] == "o"
        assert result["linestyle"] == "-"

    def test_parse_dashed_line(self) -> None:
        result = _parse_format_string("b--")
        assert result["color"] == "#1f77b4"
        assert result["linestyle"] == "--"

    def test_parse_marker_only(self) -> None:
        result = _parse_format_string("^")
        assert result["color"] is None
        assert result["marker"] == "^"

    def test_plot_with_format_string(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6], 'ro-')
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "line"

    def test_plot_format_string_does_not_break_data(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6], 'b--')
plt.title("Dashed Line")
"""
        spec = from_matplotlib(code)
        assert spec.data.columns.get("x") == [1, 2, 3]
        assert spec.data.columns.get("y") == [4, 5, 6]
        assert spec.labels.title == "Dashed Line"


# ============================================================================
# New tests: normalize_color helper
# ============================================================================


class TestNormalizeColor:
    """Test the _normalize_color helper function."""

    def test_hex_passthrough(self) -> None:
        assert _normalize_color("#FF5733") == "#FF5733"

    def test_named_color(self) -> None:
        assert _normalize_color("red") == "#D62728"

    def test_named_color_case_insensitive(self) -> None:
        assert _normalize_color("Blue") == "#1F77B4"

    def test_single_char_code(self) -> None:
        assert _normalize_color("r") == "#d62728"

    def test_non_string_returns_none(self) -> None:
        assert _normalize_color(42) is None
        assert _normalize_color(None) is None


# ============================================================================
# New tests: figsize extraction
# ============================================================================


class TestFigsize:
    """Test figsize detection from plt.figure() and plt.subplots()."""

    def test_plt_figure_figsize(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 8))
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("Wide Figure")
"""
        spec = from_matplotlib(code)
        assert spec.size.width == 1200
        assert spec.size.height == 800

    def test_plt_subplots_figsize(self) -> None:
        code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter([1, 2, 3], [4, 5, 6])
"""
        spec = from_matplotlib(code)
        assert spec.size.width == 1000
        assert spec.size.height == 600

    def test_no_figsize_uses_defaults(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
"""
        spec = from_matplotlib(code)
        assert spec.size.width == 800
        assert spec.size.height == 500


# ============================================================================
# New tests: legend detection
# ============================================================================


class TestLegendDetection:
    """Test plt.legend() and label= keyword detection."""

    def test_plt_legend_call(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6], label='Series A')
plt.legend()
"""
        spec = from_matplotlib(code)
        assert spec.legend.show is True

    def test_ax_legend_call(self) -> None:
        code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6], label='Series A')
ax.legend()
"""
        spec = from_matplotlib(code)
        assert spec.legend.show is True

    def test_label_keyword_without_legend_call(self) -> None:
        """label= keyword alone should enable legend display."""
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6], label='Data')
"""
        spec = from_matplotlib(code)
        assert spec.legend.show is True

    def test_no_legend(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
"""
        spec = from_matplotlib(code)
        assert spec.legend.show is False


# ============================================================================
# New tests: savefig detection
# ============================================================================


class TestSavefig:
    """Test plt.savefig() detection."""

    def test_plt_savefig(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("output.png")
"""
        # savefig detection is internal to the extractor; just verify
        # the spec is still valid and the plot is extracted
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1

    def test_fig_savefig(self) -> None:
        code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter([1, 2, 3], [4, 5, 6])
fig.savefig("scatter_output.pdf")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1


# ============================================================================
# New tests: grid detection
# ============================================================================


class TestGridDetection:
    """Test plt.grid() and ax.grid() detection."""

    def test_plt_grid_true(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.grid(True)
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1

    def test_ax_grid(self) -> None:
        code = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
ax.grid()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1


# ============================================================================
# New tests: barh (horizontal bar)
# ============================================================================


class TestBarh:
    """Test plt.barh() detection."""

    def test_plt_barh(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.barh(["A", "B", "C"], [10, 20, 30])
plt.title("Horizontal Bar")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "bar"
        assert spec.labels.title == "Horizontal Bar"


# ============================================================================
# New tests: tuple data (should be converted to lists)
# ============================================================================


class TestTupleData:
    """Test that tuple data is handled correctly."""

    def test_tuple_positional_data(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter((1, 2, 3), (4, 5, 6))
"""
        spec = from_matplotlib(code)
        assert spec.data.columns["x"] == [1, 2, 3]
        assert spec.data.columns["y"] == [4, 5, 6]

    def test_tuple_variable_data(self) -> None:
        code = """
import matplotlib.pyplot as plt
x = (1, 2, 3)
y = (4, 5, 6)
plt.plot(x, y)
"""
        spec = from_matplotlib(code)
        assert spec.data.columns["x"] == [1, 2, 3]
        assert spec.data.columns["y"] == [4, 5, 6]


# ============================================================================
# New tests: realistic matplotlib scripts (integration tests)
# ============================================================================


class TestRealisticScripts:
    """Integration tests against realistic matplotlib patterns."""

    def test_scatter_with_styling(self) -> None:
        """Pattern 1: scatter with full styling configuration."""
        code = """
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2.3, 4.1, 3.5, 6.2, 5.8]

plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='steelblue', label='measurements')
plt.title("Experiment Results")
plt.xlabel("Trial Number")
plt.ylabel("Measurement (cm)")
plt.legend()
plt.grid(True)
plt.savefig("experiment.png")
plt.show()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "scatter"
        assert spec.labels.title == "Experiment Results"
        assert spec.labels.x == "Trial Number"
        assert spec.labels.y == "Measurement (cm)"
        assert spec.legend.show is True
        assert spec.size.width == 1000
        assert spec.size.height == 600
        assert spec.data.columns["x"] == [1, 2, 3, 4, 5]
        assert spec.data.columns["y"] == [2.3, 4.1, 3.5, 6.2, 5.8]

    def test_line_with_format_string(self) -> None:
        """Pattern 2: line plot with format string and multiple styling."""
        code = """
import matplotlib.pyplot as plt

years = [2020, 2021, 2022, 2023, 2024]
revenue = [100, 120, 115, 140, 160]

plt.plot(years, revenue, 'b-')
plt.title("Annual Revenue")
plt.xlabel("Year")
plt.ylabel("Revenue ($M)")
plt.grid(True)
plt.show()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "line"
        assert spec.labels.title == "Annual Revenue"
        assert spec.data.columns["years"] == [2020, 2021, 2022, 2023, 2024]
        assert spec.data.columns["revenue"] == [100, 120, 115, 140, 160]

    def test_bar_chart_with_labels(self) -> None:
        """Pattern 3: bar chart with category labels and colors."""
        code = """
import matplotlib.pyplot as plt

categories = ["Python", "JavaScript", "Rust", "Go"]
popularity = [92, 88, 45, 62]

plt.figure(figsize=(8, 5))
plt.bar(categories, popularity, color='#2196F3')
plt.title("Programming Language Popularity")
plt.xlabel("Language")
plt.ylabel("Popularity Score")
plt.savefig("languages.png", dpi=300)
plt.show()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "bar"
        assert spec.labels.title == "Programming Language Popularity"
        assert spec.labels.x == "Language"
        assert spec.labels.y == "Popularity Score"
        assert spec.data.columns["categories"] == [
            "Python",
            "JavaScript",
            "Rust",
            "Go",
        ]
        assert spec.data.columns["popularity"] == [92, 88, 45, 62]

    def test_ax_based_scatter_with_subplots(self) -> None:
        """Pattern 4: object-oriented API with subplots."""
        code = """
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 8))
ax.scatter([10, 20, 30, 40], [1, 4, 9, 16], c='red', label='quadratic')
ax.set_title("Growth Curve")
ax.set_xlabel("Input")
ax.set_ylabel("Output")
ax.legend()
ax.grid(True)
fig.savefig("growth.svg")
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 1
        assert spec.layers[0].geom == "scatter"
        assert spec.labels.title == "Growth Curve"
        assert spec.labels.x == "Input"
        assert spec.labels.y == "Output"
        assert spec.legend.show is True
        assert spec.size.width == 1200
        assert spec.size.height == 800

    def test_multi_series_line_plot(self) -> None:
        """Pattern 5: multiple plot calls with labels for legend."""
        code = """
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y1 = [1, 4, 9, 16, 25]
y2 = [1, 2, 3, 4, 5]

plt.figure(figsize=(10, 6))
plt.plot(x, y1, 'r-', label='Quadratic')
plt.plot(x, y2, 'b--', label='Linear')
plt.title("Growth Comparison")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()
"""
        spec = from_matplotlib(code)
        assert len(spec.layers) == 2
        assert spec.layers[0].geom == "line"
        assert spec.layers[1].geom == "line"
        assert spec.labels.title == "Growth Comparison"
        assert spec.legend.show is True
        # Both layers should share the same x column
        assert spec.layers[0].x == "x"
        assert spec.layers[1].x == "x"


# ============================================================================
# New tests: to_botplotlib_code()
# ============================================================================


class TestToBotplotlibCode:
    """Test the code generation helper."""

    def test_simple_scatter(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2, 3], [4, 5, 6])
plt.title("Test")
"""
        result = to_botplotlib_code(code)
        assert "import botplotlib as bpl" in result
        assert "bpl.scatter(" in result
        assert 'title="Test"' in result

    def test_line_with_labels(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("My Line")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")
"""
        result = to_botplotlib_code(code)
        assert "bpl.line(" in result
        assert 'title="My Line"' in result
        assert 'x_label="X Axis"' in result
        assert 'y_label="Y Axis"' in result

    def test_bar_code(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.bar(["A", "B"], [10, 20])
"""
        result = to_botplotlib_code(code)
        assert "bpl.bar(" in result

    def test_no_plots_returns_comment(self) -> None:
        code = """
x = 42
"""
        result = to_botplotlib_code(code)
        assert "No plot calls detected" in result

    def test_multi_layer_uses_spec(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.scatter([1, 2], [3, 4])
plt.plot([5, 6], [7, 8])
"""
        result = to_botplotlib_code(code)
        assert "PlotSpec" in result
        assert "bpl.render(spec)" in result

    def test_custom_figsize_in_code(self) -> None:
        code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 8))
plt.scatter([1, 2, 3], [4, 5, 6])
"""
        result = to_botplotlib_code(code)
        assert "width=1200" in result
        assert "height=800" in result
