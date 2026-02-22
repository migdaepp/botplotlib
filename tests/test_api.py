"""End-to-end tests for the botplotlib public API."""

from __future__ import annotations

import tempfile
from pathlib import Path

import botplotlib as bpl
from botplotlib.figure import Figure
from botplotlib.spec.models import PlotSpec
from tests.conftest import assert_valid_svg


class TestScatter:
    def test_basic_scatter(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6]},
            x="x",
            y="y",
        )
        assert isinstance(fig, Figure)
        svg = fig.to_svg()
        assert_valid_svg(svg)

    def test_scatter_with_title(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6]},
            x="x",
            y="y",
            title="My Scatter",
        )
        assert "My Scatter" in fig.to_svg()

    def test_scatter_with_color(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6], "g": ["A", "A", "B"]},
            x="x",
            y="y",
            color="g",
        )
        svg = fig.to_svg()
        assert_valid_svg(svg)

    def test_scatter_with_theme(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6]},
            x="x",
            y="y",
            theme="bluesky",
        )
        assert_valid_svg(fig.to_svg())

    def test_scatter_with_list_of_dicts(self) -> None:
        data = [{"x": 1, "y": 4}, {"x": 2, "y": 5}, {"x": 3, "y": 6}]
        fig = bpl.scatter(data, x="x", y="y")
        assert_valid_svg(fig.to_svg())


class TestLine:
    def test_basic_line(self) -> None:
        fig = bpl.line(
            {"x": [1, 2, 3, 4], "y": [10, 20, 15, 25]},
            x="x",
            y="y",
        )
        assert_valid_svg(fig.to_svg())

    def test_line_with_groups(self) -> None:
        fig = bpl.line(
            {
                "x": [1, 2, 3, 4, 1, 2, 3, 4],
                "y": [10, 20, 15, 25, 8, 18, 12, 22],
                "g": ["A", "A", "A", "A", "B", "B", "B", "B"],
            },
            x="x",
            y="y",
            color="g",
        )
        assert_valid_svg(fig.to_svg())


class TestBar:
    def test_basic_bar(self) -> None:
        fig = bpl.bar(
            {"category": ["A", "B", "C"], "value": [10, 20, 15]},
            x="category",
            y="value",
        )
        assert_valid_svg(fig.to_svg())

    def test_bar_with_title(self) -> None:
        fig = bpl.bar(
            {"category": ["A", "B", "C"], "value": [10, 20, 15]},
            x="category",
            y="value",
            title="My Bar Chart",
        )
        assert "My Bar Chart" in fig.to_svg()


class TestPlot:
    def test_layered_plot(self) -> None:
        data = {"x": [1, 2, 3, 4], "y": [10, 20, 15, 25]}
        fig = bpl.plot(data)
        fig.add_line(x="x", y="y")
        fig.add_scatter(x="x", y="y")
        fig.title = "Layered Plot"
        assert_valid_svg(fig.to_svg())


class TestRender:
    def test_render_from_spec(self) -> None:
        from botplotlib.spec.models import DataSpec, LabelsSpec, LayerSpec

        spec = PlotSpec(
            data=DataSpec(columns={"x": [1, 2, 3], "y": [4, 5, 6]}),
            layers=[LayerSpec(geom="scatter", x="x", y="y")],
            labels=LabelsSpec(title="From Spec"),
        )
        fig = bpl.render(spec)
        assert "From Spec" in fig.to_svg()


class TestSaveSvg:
    def test_save_svg_creates_file(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6]},
            x="x",
            y="y",
        )
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
            fig.save_svg(f.name)
            saved = Path(f.name).read_text()
            assert_valid_svg(saved)
            Path(f.name).unlink()


class TestReprSvg:
    def test_repr_svg(self) -> None:
        fig = bpl.scatter(
            {"x": [1, 2, 3], "y": [4, 5, 6]},
            x="x",
            y="y",
        )
        repr_svg = fig._repr_svg_()
        assert repr_svg == fig.to_svg()
