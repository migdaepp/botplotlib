"""Tests for custom color_map parameter."""

from __future__ import annotations

import pytest

import botplotlib as blt
from botplotlib.compiler.accessibility import ContrastError
from botplotlib.compiler.compiler import compile_spec
from botplotlib.spec.models import DataSpec, LayerSpec, PlotSpec

BAR_DATA = {
    "category": ["A", "B", "C"],
    "value": [10, 20, 30],
}

BLT_DATA = {
    "layer": ["bottom bun", "lettuce", "bot", "tomato", "top bun"],
    "size": [1, 1, 1, 1, 1],
}


class TestColorMapBar:
    """color_map produces correct fill colors on bar charts."""

    def test_custom_colors_in_svg(self) -> None:
        fig = blt.bar(
            BAR_DATA,
            x="category",
            y="value",
            color="category",
            color_map={"A": "#CC0000", "B": "#006600", "C": "#0000CC"},
        )
        svg = fig.to_svg()
        assert "#CC0000" in svg
        assert "#006600" in svg
        assert "#0000CC" in svg

    def test_partial_color_map_falls_back(self) -> None:
        """Only override some categories; the rest get palette colors."""
        fig = blt.bar(
            BAR_DATA,
            x="category",
            y="value",
            color="category",
            color_map={"A": "#FF0000"},
        )
        svg = fig.to_svg()
        assert "#FF0000" in svg
        # B and C should still render (palette colors)
        assert "<svg" in svg and "</svg>" in svg

    def test_color_map_without_color_param_ignored(self) -> None:
        """color_map without color= grouping doesn't crash."""
        fig = blt.bar(
            BAR_DATA,
            x="category",
            y="value",
            color_map={"A": "#FF0000"},
        )
        svg = fig.to_svg()
        # Should render normally — no crash, no custom color applied
        assert "<svg" in svg and "</svg>" in svg

    def test_blt_food_colors(self) -> None:
        """The BLT bar chart with food-appropriate colors."""
        fig = blt.bar(
            BLT_DATA,
            x="layer",
            y="size",
            color="layer",
            color_map={
                "bottom bun": "#B07830",
                "lettuce": "#388E3C",
                "bot": "#4E79A7",
                "tomato": "#E53935",
                "top bun": "#B07830",
            },
        )
        svg = fig.to_svg()
        assert "#B07830" in svg
        assert "#388E3C" in svg
        assert "#4E79A7" in svg
        assert "#E53935" in svg


class TestColorMapScatter:
    """color_map works with scatter plots."""

    def test_scatter_custom_colors(self) -> None:
        data = {"x": [1, 2, 3], "y": [4, 5, 6], "grp": ["a", "b", "a"]}
        fig = blt.scatter(
            data,
            x="x",
            y="y",
            color="grp",
            color_map={"a": "#AA0000", "b": "#006600"},
        )
        svg = fig.to_svg()
        assert "#AA0000" in svg
        assert "#006600" in svg


class TestColorMapLine:
    """color_map works with line plots."""

    def test_line_custom_colors(self) -> None:
        data = {
            "x": [1, 2, 3, 1, 2, 3],
            "y": [1, 2, 3, 3, 2, 1],
            "g": ["a", "a", "a", "b", "b", "b"],
        }
        fig = blt.line(
            data,
            x="x",
            y="y",
            color="g",
            color_map={"a": "#112233", "b": "#445566"},
        )
        svg = fig.to_svg()
        assert "#112233" in svg
        assert "#445566" in svg


class TestColorMapRoundTrip:
    """PlotSpec with color_map serializes to JSON and back."""

    def test_json_round_trip(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns=BAR_DATA),
            layers=[
                LayerSpec(
                    geom="bar",
                    x="category",
                    y="value",
                    color="category",
                    color_map={"A": "#FF0000", "B": "#00FF00"},
                )
            ],
        )
        json_str = spec.model_dump_json()
        restored = PlotSpec.model_validate_json(json_str)
        assert restored.layers[0].color_map == {"A": "#FF0000", "B": "#00FF00"}

    def test_compile_with_color_map_on_layer(self) -> None:
        """Compiler reads color_map from LayerSpec."""
        spec = PlotSpec(
            data=DataSpec(columns=BAR_DATA),
            layers=[
                LayerSpec(
                    geom="bar",
                    x="category",
                    y="value",
                    color="category",
                    color_map={"A": "#FF0000"},
                )
            ],
        )
        compiled = compile_spec(spec)
        # A should have the custom color in the legend
        legend_colors = {e.label: e.color for e in compiled.legend_entries}
        assert legend_colors["A"] == "#FF0000"


class TestColorMapWCAG:
    """color_map colors are validated for WCAG contrast."""

    def test_low_contrast_color_raises(self) -> None:
        """A near-white color on white background should fail."""
        spec = PlotSpec(
            data=DataSpec(columns=BAR_DATA),
            layers=[
                LayerSpec(
                    geom="bar",
                    x="category",
                    y="value",
                    color="category",
                    color_map={"A": "#EEEEEE"},
                )
            ],
        )
        with pytest.raises(ContrastError):
            compile_spec(spec)
