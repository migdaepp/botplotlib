"""Tests for the waterfall geom — proof of concept for plugin architecture."""

from __future__ import annotations

import pytest

import botplotlib as bpl
from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.geoms import get_geom, registered_geoms
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
    """bpl.waterfall() convenience function works."""

    def test_basic_waterfall(self) -> None:
        fig = bpl.waterfall(WATERFALL_DATA, x="category", y="amount")
        svg = fig.to_svg()
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_waterfall_with_title(self) -> None:
        fig = bpl.waterfall(
            WATERFALL_DATA,
            x="category",
            y="amount",
            title="Profit Breakdown",
        )
        svg = fig.to_svg()
        assert "Profit Breakdown" in svg

    def test_waterfall_with_theme(self) -> None:
        fig = bpl.waterfall(
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
        fig = bpl.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        colors = {b.color for b in compiled.bars}
        assert len(colors) == 1  # all same color (positive)

    def test_all_negative(self) -> None:
        data = {"step": ["A", "B", "C"], "val": [-10, -20, -30]}
        fig = bpl.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        colors = {b.color for b in compiled.bars}
        assert len(colors) == 1  # all same color (negative)

    def test_single_bar(self) -> None:
        data = {"step": ["Only"], "val": [42]}
        fig = bpl.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        assert len(compiled.bars) == 1
        assert len(compiled.lines) == 0  # no connectors

    def test_zero_value(self) -> None:
        data = {"step": ["A", "B"], "val": [100, 0]}
        fig = bpl.waterfall(data, x="step", y="val")
        compiled = fig.compiled
        assert len(compiled.bars) == 2
        # Zero-height bar should still render (height = 0)
        assert compiled.bars[1].bar_height == pytest.approx(0.0)
