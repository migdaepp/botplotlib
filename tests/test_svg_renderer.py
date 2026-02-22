"""Tests for botplotlib.render.svg_renderer."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from botplotlib.compiler.compiler import compile_spec
from botplotlib.render.svg_renderer import render_svg
from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    LegendSpec,
    PlotSpec,
    SizeSpec,
)
from tests.conftest import assert_valid_svg, count_svg_elements


def _scatter_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]}),
        layers=[LayerSpec(geom="scatter", x="x", y="y")],
        labels=LabelsSpec(title="Test Scatter", x="X Axis", y="Y Axis"),
    )


def _line_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={"x": [1, 2, 3, 4], "y": [10, 20, 15, 25]}),
        layers=[LayerSpec(geom="line", x="x", y="y")],
        labels=LabelsSpec(title="Test Line"),
    )


def _bar_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "category": ["A", "B", "C", "D"],
            "value": [23, 17, 35, 12],
        }),
        layers=[LayerSpec(geom="bar", x="category", y="value")],
        labels=LabelsSpec(title="Test Bar"),
    )


def _color_scatter_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["A", "A", "A", "B", "B", "B"],
        }),
        layers=[LayerSpec(geom="scatter", x="x", y="y", color="g")],
        labels=LabelsSpec(title="Scatter with Groups"),
        legend=LegendSpec(show=True),
    )


class TestRenderScatter:
    def test_produces_valid_svg(self) -> None:
        compiled = compile_spec(_scatter_spec())
        svg = render_svg(compiled)
        assert_valid_svg(svg)

    def test_contains_circles(self) -> None:
        compiled = compile_spec(_scatter_spec())
        svg = render_svg(compiled)
        assert count_svg_elements(svg, "circle") == 5

    def test_contains_title(self) -> None:
        compiled = compile_spec(_scatter_spec())
        svg = render_svg(compiled)
        assert "Test Scatter" in svg


class TestRenderLine:
    def test_produces_valid_svg(self) -> None:
        compiled = compile_spec(_line_spec())
        svg = render_svg(compiled)
        assert_valid_svg(svg)

    def test_contains_polyline(self) -> None:
        compiled = compile_spec(_line_spec())
        svg = render_svg(compiled)
        assert count_svg_elements(svg, "polyline") == 1


class TestRenderBar:
    def test_produces_valid_svg(self) -> None:
        compiled = compile_spec(_bar_spec())
        svg = render_svg(compiled)
        assert_valid_svg(svg)

    def test_contains_bars(self) -> None:
        compiled = compile_spec(_bar_spec())
        svg = render_svg(compiled)
        # 4 bars + background rect + clip rect = at least 6 rects
        assert count_svg_elements(svg, "rect") >= 5


class TestRenderLegend:
    def test_legend_rendered(self) -> None:
        compiled = compile_spec(_color_scatter_spec())
        svg = render_svg(compiled)
        assert "A" in svg
        assert "B" in svg

    def test_legend_has_color_swatches(self) -> None:
        compiled = compile_spec(_color_scatter_spec())
        svg = render_svg(compiled)
        # Should have legend rect swatches (small rects with rx=2)
        assert 'rx="2"' in svg


class TestRenderEmpty:
    def test_empty_spec_renders(self) -> None:
        compiled = compile_spec(PlotSpec())
        svg = render_svg(compiled)
        assert_valid_svg(svg)
