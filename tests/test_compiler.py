"""Tests for botplotlib.compiler.compiler."""

from __future__ import annotations

import pytest

from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    LegendSpec,
    PlotSpec,
    SizeSpec,
)


def _make_scatter_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "x": [1, 2, 3, 4, 5],
            "y": [2, 4, 1, 5, 3],
        }),
        layers=[LayerSpec(geom="scatter", x="x", y="y")],
        labels=LabelsSpec(title="Test Scatter"),
    )


def _make_line_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "x": [1, 2, 3, 4],
            "y": [10, 20, 15, 25],
        }),
        layers=[LayerSpec(geom="line", x="x", y="y")],
        labels=LabelsSpec(title="Test Line"),
    )


def _make_bar_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "category": ["A", "B", "C", "D"],
            "value": [23, 17, 35, 12],
        }),
        layers=[LayerSpec(geom="bar", x="category", y="value")],
        labels=LabelsSpec(title="Test Bar"),
    )


def _make_color_scatter_spec() -> PlotSpec:
    return PlotSpec(
        data=DataSpec(columns={
            "x": [1, 2, 3, 4, 5, 6],
            "y": [2, 4, 1, 5, 3, 6],
            "g": ["A", "A", "A", "B", "B", "B"],
        }),
        layers=[LayerSpec(geom="scatter", x="x", y="y", color="g")],
        labels=LabelsSpec(title="Scatter with Color"),
        legend=LegendSpec(show=True),
    )


class TestCompileScatter:
    def test_produces_points(self) -> None:
        result = compile_spec(_make_scatter_spec())
        assert isinstance(result, CompiledPlot)
        assert len(result.points) == 5

    def test_has_ticks(self) -> None:
        result = compile_spec(_make_scatter_spec())
        assert len(result.x_ticks) > 0
        assert len(result.y_ticks) > 0

    def test_has_title(self) -> None:
        result = compile_spec(_make_scatter_spec())
        title_texts = [t for t in result.texts if t.text == "Test Scatter"]
        assert len(title_texts) == 1

    def test_points_within_plot_area(self) -> None:
        result = compile_spec(_make_scatter_spec())
        for pt in result.points:
            assert result.plot_area.x <= pt.px <= result.plot_area.right
            assert result.plot_area.y <= pt.py <= result.plot_area.bottom


class TestCompileLine:
    def test_produces_lines(self) -> None:
        result = compile_spec(_make_line_spec())
        assert len(result.lines) == 1

    def test_line_has_correct_point_count(self) -> None:
        result = compile_spec(_make_line_spec())
        assert len(result.lines[0].points) == 4


class TestCompileBar:
    def test_produces_bars(self) -> None:
        result = compile_spec(_make_bar_spec())
        assert len(result.bars) == 4

    def test_bars_have_positive_dimensions(self) -> None:
        result = compile_spec(_make_bar_spec())
        for bar in result.bars:
            assert bar.bar_width > 0
            assert bar.bar_height > 0

    def test_categorical_x_ticks(self) -> None:
        result = compile_spec(_make_bar_spec())
        labels = [t.label for t in result.x_ticks]
        assert labels == ["A", "B", "C", "D"]


class TestCompileColorGrouping:
    def test_has_legend_entries(self) -> None:
        result = compile_spec(_make_color_scatter_spec())
        assert len(result.legend_entries) == 2

    def test_legend_entries_have_colors(self) -> None:
        result = compile_spec(_make_color_scatter_spec())
        for entry in result.legend_entries:
            assert entry.color.startswith("#")

    def test_points_have_group_colors(self) -> None:
        result = compile_spec(_make_color_scatter_spec())
        colors = {pt.color for pt in result.points}
        assert len(colors) == 2


class TestCompileEmptySpec:
    def test_empty_spec_compiles(self) -> None:
        spec = PlotSpec()
        result = compile_spec(spec)
        assert isinstance(result, CompiledPlot)
        assert len(result.points) == 0
        assert len(result.lines) == 0
        assert len(result.bars) == 0
