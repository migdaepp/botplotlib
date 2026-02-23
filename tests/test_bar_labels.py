"""Tests for value labels on bar charts."""

from __future__ import annotations

import botplotlib as bpl
from botplotlib.compiler.compiler import CompiledPlot, compile_spec
from botplotlib.geoms.primitives import CompiledBar, CompiledText
from botplotlib.spec.models import DataSpec, LayerSpec, PlotSpec

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

BAR_DATA = {
    "category": ["A", "B", "C", "D"],
    "value": [10, 50, 200, 5],
}


def _compile_bar(labels: bool = False, label_format: str | None = None) -> CompiledPlot:
    spec = PlotSpec(
        data=DataSpec(columns=BAR_DATA),
        layers=[
            LayerSpec(
                geom="bar",
                x="category",
                y="value",
                labels=labels,
                label_format=label_format,
            )
        ],
    )
    return compile_spec(spec)


def _label_texts(compiled: CompiledPlot) -> list[CompiledText]:
    """Extract CompiledText primitives that came from bar labels (not axis labels)."""
    return [p for p in compiled.primitives if isinstance(p, CompiledText)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestLabelsOffByDefault:
    def test_no_label_texts_when_off(self) -> None:
        compiled = _compile_bar(labels=False)
        # The only CompiledText items should be axis/title labels, not bar labels.
        bar_label_values = {"10", "50", "200", "5"}
        for t in compiled.primitives:
            if isinstance(t, CompiledText):
                assert t.text not in bar_label_values


class TestLabelsAppear:
    def test_labels_in_svg(self) -> None:
        fig = bpl.bar(BAR_DATA, x="category", y="value", labels=True)
        svg = fig.to_svg()
        for val in [10, 50, 200, 5]:
            assert str(val) in svg

    def test_labels_count_matches_bars(self) -> None:
        compiled = _compile_bar(labels=True)
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        # Filter label texts: they should be the formatted values
        label_values = {"10", "50", "200", "5"}
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text in label_values
        ]
        assert len(labels) == len(bars)


class TestLabelFormat:
    def test_default_format(self) -> None:
        compiled = _compile_bar(labels=True)
        label_values = {
            p.text
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text.isdigit()
        }
        # Integers should appear as clean integers
        assert "10" in label_values
        assert "200" in label_values

    def test_custom_format(self) -> None:
        compiled = _compile_bar(labels=True, label_format="${:,.0f}")
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text.startswith("$")
        ]
        assert len(labels) == 4
        label_texts = {lbl.text for lbl in labels}
        assert "$200" in label_texts
        assert "$50" in label_texts


class TestLabelPlacement:
    def test_label_inside_wide_bar(self) -> None:
        # Use a wide chart with a large value so the bar is tall
        data = {"cat": ["Big"], "val": [1000]}
        compiled = compile_spec(
            PlotSpec(
                data=DataSpec(columns=data),
                layers=[LayerSpec(geom="bar", x="cat", y="val", labels=True)],
                size={"width": 800, "height": 500},
            )
        )
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text == "1000"
        ]
        assert len(bars) == 1 and len(labels) == 1
        bar = bars[0]
        label = labels[0]
        # Label y should be inside the bar bounds
        assert bar.py <= label.y <= bar.py + bar.bar_height

    def test_label_outside_narrow_bar(self) -> None:
        # Use a narrow chart with a small value so the bar is short
        data = {"cat": ["A", "B", "C", "D", "E", "F", "G", "H"], "val": [1] * 8}
        compiled = compile_spec(
            PlotSpec(
                data=DataSpec(columns=data),
                layers=[LayerSpec(geom="bar", x="cat", y="val", labels=True)],
                size={"width": 200, "height": 100},
            )
        )
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text == "1"
        ]
        assert len(labels) > 0
        # At least some labels should be above the bar (label.y < bar.py)
        for bar, label in zip(bars, labels):
            assert label.y <= bar.py


class TestLabelColorAdapts:
    def test_dark_bar_white_label(self) -> None:
        # Default palette first color is dark (#4E79A7) → white label
        data = {"cat": ["X"], "val": [1000]}
        compiled = compile_spec(
            PlotSpec(
                data=DataSpec(columns=data),
                layers=[LayerSpec(geom="bar", x="cat", y="val", labels=True)],
                size={"width": 800, "height": 500},
            )
        )
        labels = [
            p
            for p in compiled.primitives
            if isinstance(p, CompiledText) and p.text == "1000"
        ]
        assert len(labels) == 1
        bars = [p for p in compiled.primitives if isinstance(p, CompiledBar)]
        bar = bars[0]
        label = labels[0]
        # If label is inside the bar, it should be white
        if bar.py <= label.y <= bar.py + bar.bar_height:
            assert label.color == "#FFFFFF"


class TestLabelsJsonRoundTrip:
    def test_round_trip(self) -> None:
        layer = LayerSpec(
            geom="bar",
            x="cat",
            y="val",
            labels=True,
            label_format="${:,.0f}",
        )
        json_str = layer.model_dump_json()
        restored = LayerSpec.model_validate_json(json_str)
        assert restored.labels is True
        assert restored.label_format == "${:,.0f}"


class TestApiConvenience:
    def test_bar_with_labels(self) -> None:
        fig = bpl.bar(BAR_DATA, x="category", y="value", labels=True)
        svg = fig.to_svg()
        assert "<svg" in svg
        assert "10" in svg
