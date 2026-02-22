"""Tests for Pydantic spec model serialization and validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from botplotlib.spec.models import (
    DataSpec,
    LabelsSpec,
    LayerSpec,
    LegendSpec,
    PlotSpec,
    SizeSpec,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _full_plot_spec() -> PlotSpec:
    """Return a PlotSpec with every field explicitly set."""
    return PlotSpec(
        data=DataSpec(
            columns={
                "x": [1, 2, 3],
                "y": [10.5, 20.0, 30.1],
                "category": ["a", "b", "c"],
            }
        ),
        layers=[
            LayerSpec(geom="scatter", x="x", y="y", color="category"),
            LayerSpec(geom="line", x="x", y="y"),
            LayerSpec(geom="bar", x="category", y="y"),
        ],
        labels=LabelsSpec(title="My Plot", x="X Axis", y="Y Axis"),
        legend=LegendSpec(show=False, position="bottom"),
        size=SizeSpec(width=1024, height=768),
        theme="dark",
    )


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """PlotSpec survives JSON round-trip via model_dump_json / model_validate_json."""

    def test_full_spec_round_trip(self) -> None:
        original = _full_plot_spec()
        json_str = original.model_dump_json()
        restored = PlotSpec.model_validate_json(json_str)
        assert restored == original

    def test_empty_spec_round_trip(self) -> None:
        original = PlotSpec()
        json_str = original.model_dump_json()
        restored = PlotSpec.model_validate_json(json_str)
        assert restored == original

    def test_nested_data_round_trip(self) -> None:
        """PlotSpec with nested data columns round-trips correctly."""
        spec = PlotSpec(
            data=DataSpec(
                columns={
                    "values": [1, 2.5, "three", None],
                    "flags": [True, False, True, False],
                }
            ),
            layers=[LayerSpec(geom="scatter", x="values", y="values")],
        )
        json_str = spec.model_dump_json()
        restored = PlotSpec.model_validate_json(json_str)
        assert restored == spec
        assert restored.data.columns["values"] == [1, 2.5, "three", None]
        assert restored.data.columns["flags"] == [True, False, True, False]


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------

class TestDefaults:
    """Empty PlotSpec has correct defaults."""

    def test_default_data(self) -> None:
        spec = PlotSpec()
        assert spec.data.columns == {}

    def test_default_layers(self) -> None:
        spec = PlotSpec()
        assert spec.layers == []

    def test_default_labels(self) -> None:
        spec = PlotSpec()
        assert spec.labels.title is None
        assert spec.labels.x is None
        assert spec.labels.y is None

    def test_default_legend(self) -> None:
        spec = PlotSpec()
        assert spec.legend.show is True
        assert spec.legend.position == "right"

    def test_default_size(self) -> None:
        spec = PlotSpec()
        assert spec.size.width == 800
        assert spec.size.height == 500

    def test_default_theme(self) -> None:
        spec = PlotSpec()
        assert spec.theme == "default"


# ---------------------------------------------------------------------------
# Literal validation: LayerSpec.geom
# ---------------------------------------------------------------------------

class TestLayerSpecValidation:
    """LayerSpec validates geom is one of scatter/line/bar."""

    @pytest.mark.parametrize("geom", ["scatter", "line", "bar"])
    def test_valid_geom(self, geom: str) -> None:
        layer = LayerSpec(geom=geom, x="x", y="y")
        assert layer.geom == geom

    @pytest.mark.parametrize("bad_geom", ["pie", "histogram", "heatmap", ""])
    def test_invalid_geom_raises(self, bad_geom: str) -> None:
        with pytest.raises(ValidationError):
            LayerSpec(geom=bad_geom, x="x", y="y")


# ---------------------------------------------------------------------------
# Literal validation: LegendSpec.position
# ---------------------------------------------------------------------------

class TestLegendSpecValidation:
    """LegendSpec validates position is one of top/bottom/left/right."""

    @pytest.mark.parametrize("pos", ["top", "bottom", "left", "right"])
    def test_valid_position(self, pos: str) -> None:
        legend = LegendSpec(position=pos)
        assert legend.position == pos

    @pytest.mark.parametrize("bad_pos", ["center", "inside", "none", ""])
    def test_invalid_position_raises(self, bad_pos: str) -> None:
        with pytest.raises(ValidationError):
            LegendSpec(position=bad_pos)


# ---------------------------------------------------------------------------
# DataSpec: mixed types in columns
# ---------------------------------------------------------------------------

class TestDataSpecMixedTypes:
    """DataSpec columns can hold mixed types (str, int, float)."""

    def test_mixed_str_int_float(self) -> None:
        data = DataSpec(columns={"mixed": ["hello", 42, 3.14]})
        assert data.columns["mixed"] == ["hello", 42, 3.14]

    def test_mixed_with_none(self) -> None:
        data = DataSpec(columns={"col": [None, 1, "two", 3.0]})
        assert data.columns["col"] == [None, 1, "two", 3.0]

    def test_empty_columns(self) -> None:
        data = DataSpec(columns={"empty": []})
        assert data.columns["empty"] == []

    def test_multiple_mixed_columns(self) -> None:
        data = DataSpec(
            columns={
                "ints": [1, 2, 3],
                "floats": [1.1, 2.2, 3.3],
                "strings": ["a", "b", "c"],
                "mixed": [1, "two", 3.0],
            }
        )
        assert len(data.columns) == 4
        assert data.columns["mixed"] == [1, "two", 3.0]


# ---------------------------------------------------------------------------
# Spec diff: comparing two PlotSpecs via model_dump()
# ---------------------------------------------------------------------------

class TestSpecDiff:
    """Two PlotSpecs can be compared by their model_dump() dicts."""

    def test_identical_specs_equal(self) -> None:
        spec_a = _full_plot_spec()
        spec_b = _full_plot_spec()
        assert spec_a.model_dump() == spec_b.model_dump()

    def test_different_theme_detected(self) -> None:
        spec_a = _full_plot_spec()
        spec_b = _full_plot_spec()
        spec_b.theme = "light"
        dump_a = spec_a.model_dump()
        dump_b = spec_b.model_dump()
        assert dump_a != dump_b
        assert dump_a["theme"] != dump_b["theme"]

    def test_different_layer_detected(self) -> None:
        spec_a = PlotSpec(layers=[LayerSpec(geom="scatter", x="x", y="y")])
        spec_b = PlotSpec(layers=[LayerSpec(geom="line", x="x", y="y")])
        assert spec_a.model_dump() != spec_b.model_dump()

    def test_different_size_detected(self) -> None:
        spec_a = PlotSpec(size=SizeSpec(width=800, height=500))
        spec_b = PlotSpec(size=SizeSpec(width=1024, height=768))
        assert spec_a.model_dump() != spec_b.model_dump()

    def test_added_data_detected(self) -> None:
        spec_a = PlotSpec()
        spec_b = PlotSpec(data=DataSpec(columns={"x": [1, 2, 3]}))
        assert spec_a.model_dump() != spec_b.model_dump()

    def test_default_specs_equal(self) -> None:
        """Two default PlotSpecs produce identical dicts."""
        assert PlotSpec().model_dump() == PlotSpec().model_dump()
