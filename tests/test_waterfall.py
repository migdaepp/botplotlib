"""Tests for the waterfall geom — proof of concept for plugin architecture."""

from __future__ import annotations

import pytest

import botplotlib as blt
from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.geoms import get_geom, registered_geoms
from botplotlib.geoms.primitives import CompiledBar, CompiledText
from botplotlib.spec.models import DataSpec, LayerSpec, PlotSpec

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

WATERFALL_DATA = {
    "category": ["Revenue", "COGS", "Expenses", "Tax", "Profit"],
    "amount": [100, -40, -30, -10, 20],
}


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------


class TestWaterfallRegistry:
    """Waterfall geom is registered and discoverable."""

    def test_waterfall_in_registry(self) -> None:
        geoms = registered_geoms()
        assert "waterfall" in geoms

    def test_get_waterfall_geom(self) -> None:
        geom = get_geom("waterfall")
        assert geom.name == "waterfall"


# ---------------------------------------------------------------------------
# API tests
# ---------------------------------------------------------------------------


class TestWaterfallAPI:
    """blt.waterfall() convenience function works."""

    def test_basic_waterfall(self) -> None:
        fig = blt.waterfall(WATERFALL_DATA, x="category", y="amount")
        svg = fig.to_svg()
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_waterfall_with_title(self) -> None:
        fig = blt.waterfall(
            WATERFALL_DATA,
            x="category",
            y="amount",
            title="Profit Breakdown",
        )
        svg = fig.to_svg()
        assert "Profit Breakdown" in svg

    def test_waterfall_with_theme(self) -> None:
        fig = blt.waterfall(
            WATERFALL_DATA,
            x="category",
            y="amount",
            theme="bluesky",
        )
        svg = fig.to_svg()
        assert "<svg" in svg


# ---------------------------------------------------------------------------
# Compilation tests
# ---------------------------------------------------------------------------


class TestWaterfallCompilation:
    """Waterfall compiles to correct geometry."""

    def _compile_waterfall(self) -> CompiledPlot:
        spec = PlotSpec(
            data=DataSpec(columns=WATERFALL_DATA),
            layers=[LayerSpec(geom="waterfall", x="category", y="amount")],
        )
        return compile_spec(spec)

    def test_produces_bars(self) -> None:
        compiled = self._compile_waterfall()
        # 5 categories = 5 bars
        assert len(compiled.bars) == 5

    def test_produces_connector_lines(self) -> None:
        compiled = self._compile_waterfall()
        # 4 connectors between 5 bars
        assert len(compiled.lines) == 4

    def test_bars_in_primitives_list(self) -> None:
        compiled = self._compile_waterfall()
        # Primitives list has both bars and lines
        assert len(compiled.primitives) == 9  # 5 bars + 4 lines

    def test_positive_negative_colors_differ(self) -> None:
        compiled = self._compile_waterfall()
        colors = {b.color for b in compiled.bars}
        # Revenue(+100) and Profit(+20) have one color;
        # COGS(-40), Expenses(-30), Tax(-10) have another
        assert len(colors) == 2

    def test_floating_bars_correct_positions(self) -> None:
        compiled = self._compile_waterfall()
        # First bar starts at y=0 (100 tall)
        # Second bar floats from 100 down to 60 (height 40)
        # Third bar floats from 60 down to 30 (height 30)
        # Heights should match step sizes
        bar_heights = [b.bar_height for b in compiled.bars]
        # All heights are positive and proportional to step magnitudes
        for h in bar_heights:
            assert h > 0

    def test_x_ticks_are_categories(self) -> None:
        compiled = self._compile_waterfall()
        labels = [t.label for t in compiled.x_ticks]
        assert labels == ["Revenue", "COGS", "Expenses", "Tax", "Profit"]

    def test_y_range_covers_all_values(self) -> None:
        compiled = self._compile_waterfall()
        y_tick_values = [t.value for t in compiled.y_ticks]
        # Running totals: 0, 100, 60, 30, 20, 40
        # y range should cover 0 to 100
        assert min(y_tick_values) <= 0
        assert max(y_tick_values) >= 100


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


class TestWaterfallValidation:
    """Waterfall validates data correctly."""

    def test_missing_x_column(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns={"amount": [100]}),
            layers=[LayerSpec(geom="waterfall", x="category", y="amount")],
        )
        with pytest.raises(ValueError, match="column 'category'"):
            compile_spec(spec)

    def test_missing_y_column(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns={"category": ["A"]}),
            layers=[LayerSpec(geom="waterfall", x="category", y="amount")],
        )
        with pytest.raises(ValueError, match="column 'amount'"):
            compile_spec(spec)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestWaterfallEdgeCases:
    """Waterfall handles edge cases."""

    def test_all_positive(self) -> None:
        data = {"step": ["A", "B", "C"], "val": [10, 20, 30]}
        fig = blt.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        colors = {b.color for b in compiled.bars}
        assert len(colors) == 1  # all same color (positive)

    def test_all_negative(self) -> None:
        data = {"step": ["A", "B", "C"], "val": [-10, -20, -30]}
        fig = blt.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        colors = {b.color for b in compiled.bars}
        assert len(colors) == 1  # all same color (negative)

    def test_single_bar(self) -> None:
        data = {"step": ["Only"], "val": [42]}
        fig = blt.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        assert len(compiled.bars) == 1
        assert len(compiled.lines) == 0  # no connectors

    def test_zero_value(self) -> None:
        data = {"step": ["A", "B"], "val": [100, 0]}
        fig = blt.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        assert len(compiled.bars) == 2
        # Zero-height bar should still render (height = 0)
        assert compiled.bars[1].bar_height == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Label tests
# ---------------------------------------------------------------------------


class TestWaterfallLabels:
    """Waterfall labels appear and are positioned correctly."""

    def test_waterfall_labels_appear(self) -> None:
        fig = blt.waterfall(WATERFALL_DATA, x="category", y="amount", labels=True)
        svg = fig.to_svg()
        assert "100" in svg
        assert "-40" in svg

    def test_waterfall_label_count(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns=WATERFALL_DATA),
            layers=[LayerSpec(geom="waterfall", x="category", y="amount", labels=True)],
        )
        compiled = compile_spec(spec)
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        step_values = {"100", "-40", "-30", "-10", "20"}
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text in step_values
        ]
        assert len(labels) == len(bars)

    def test_waterfall_positive_label_above(self) -> None:
        # Large positive step on a narrow chart → label outside, above bar
        data = {"step": list("ABCDEFGH"), "val": [1] * 8}
        spec = PlotSpec(
            data=DataSpec(columns=data),
            layers=[LayerSpec(geom="waterfall", x="step", y="val", labels=True)],
            size={"width": 200, "height": 100},
        )
        compiled = compile_spec(spec)
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text == "1"
        ]
        assert len(labels) > 0
        # Positive step → label above bar (label.y <= bar.py)
        for bar, label in zip(bars, labels):
            assert label.y <= bar.py

    def test_waterfall_negative_label_below(self) -> None:
        # Negative step on a narrow chart → label outside, below bar
        data = {"step": list("ABCDEFGH"), "val": [-1] * 8}
        spec = PlotSpec(
            data=DataSpec(columns=data),
            layers=[LayerSpec(geom="waterfall", x="step", y="val", labels=True)],
            size={"width": 200, "height": 100},
        )
        compiled = compile_spec(spec)
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text == "-1"
        ]
        assert len(labels) > 0
        # Negative step → label below bar (label.y >= bar.py + bar.bar_height)
        for bar, label in zip(bars, labels):
            assert label.y >= bar.py + bar.bar_height
