"""Tests for botplotlib.refactor.from_matplotlib."""

from __future__ import annotations

import tempfile
from pathlib import Path

from botplotlib.refactor.from_matplotlib import from_matplotlib


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
