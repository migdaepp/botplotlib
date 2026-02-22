"""Tests for the agent / JSON path: Figure.from_json() and Figure.from_dict().

These tests exercise the full pipeline from a JSON string or plain dict all
the way to a rendered SVG, validating that:

- Valid specs round-trip cleanly (PlotSpec → JSON → Figure → SVG).
- from_dict accepts realistic LLM function-call output.
- Missing required fields produce clear Pydantic ValidationErrors.
- Extra / unknown fields are silently ignored (Pydantic default).
- Malformed types produce clear Pydantic ValidationErrors.
- An empty spec (all defaults) renders without error.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from botplotlib.figure import Figure
from botplotlib.spec.models import DataSpec, LabelsSpec, LayerSpec, PlotSpec
from tests.conftest import assert_valid_svg

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scatter_spec() -> PlotSpec:
    """Return a minimal scatter PlotSpec with embedded data."""
    return PlotSpec(
        data=DataSpec(
            columns={
                "year": [2000, 2005, 2010, 2015, 2020],
                "temp": [14.2, 14.5, 14.8, 15.1, 15.4],
            }
        ),
        layers=[LayerSpec(geom="scatter", x="year", y="temp")],
        labels=LabelsSpec(title="Global Temperature", x="Year", y="Temp (°C)"),
        theme="default",
    )


def _llm_function_call_dict() -> dict:
    """Simulate a realistic dict an LLM would return as a function-call response.

    This mirrors the format produced by structured-output / tool-call APIs
    such as Anthropic's tool_use or OpenAI's function calling.
    """
    return {
        "data": {
            "columns": {
                "quarter": ["Q1", "Q2", "Q3", "Q4"],
                "revenue": [120_000, 145_000, 132_000, 168_000],
                "region": ["North", "South", "North", "South"],
            }
        },
        "layers": [{"geom": "bar", "x": "quarter", "y": "revenue", "color": "region"}],
        "labels": {
            "title": "Quarterly Revenue by Region",
            "x": "Quarter",
            "y": "Revenue ($)",
        },
        "legend": {"show": True, "position": "right"},
        "size": {"width": 800, "height": 500},
        "theme": "substack",
    }


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------


class TestRoundTripFromJson:
    """PlotSpec → JSON → Figure.from_json() → SVG round-trip.

    Note on SVG comparison: SizeSpec fields are typed as ``float``.  When
    constructing a spec directly in Python with integer literals the internal
    representation can differ from the JSON round-trip (where Pydantic always
    stores them as float).  This causes cosmetic differences in the SVG
    viewBox attribute (``800`` vs ``800.0``).  Round-trip tests therefore
    verify spec equality and SVG validity/content rather than byte-for-byte
    SVG identity.  The ``test_empty_spec_svg_matches_direct_figure`` test in
    ``TestEmptySpec`` confirms identity for the case where both figures are
    created via the JSON path.
    """

    def test_scatter_round_trip_spec_equals_original(self) -> None:
        """from_json restores a spec that is equal to the original."""
        original_spec = _scatter_spec()
        restored = Figure.from_json(original_spec.model_dump_json()).spec
        assert restored == original_spec

    def test_scatter_round_trip_svg_valid_and_titled(self) -> None:
        """from_json produces valid SVG containing the correct title."""
        fig = Figure.from_json(_scatter_spec().model_dump_json())
        svg = fig.to_svg()
        assert_valid_svg(svg)
        assert "Global Temperature" in svg

    def test_from_json_returns_figure(self) -> None:
        spec = _scatter_spec()
        fig = Figure.from_json(spec.model_dump_json())
        assert isinstance(fig, Figure)

    def test_from_json_spec_equals_original(self) -> None:
        original = _scatter_spec()
        restored = Figure.from_json(original.model_dump_json()).spec
        assert restored == original

    def test_from_json_svg_is_valid(self) -> None:
        fig = Figure.from_json(_scatter_spec().model_dump_json())
        assert_valid_svg(fig.to_svg())

    def test_from_json_title_appears_in_svg(self) -> None:
        fig = Figure.from_json(_scatter_spec().model_dump_json())
        assert "Global Temperature" in fig.to_svg()

    def test_from_json_double_round_trip_svg_matches(self) -> None:
        """Two JSON round-trips from the same base produce identical SVGs.

        Once the spec has been through JSON once, both sides are floats and
        the rendered SVG is byte-for-byte identical.
        """
        original_spec = _scatter_spec()
        json_str = original_spec.model_dump_json()
        # Round-trip once → then use that as the new baseline
        fig1 = Figure.from_json(json_str)
        fig2 = Figure.from_json(fig1.spec.model_dump_json())
        assert fig1.to_svg() == fig2.to_svg()

    def test_bar_round_trip_valid_svg(self) -> None:
        """Bar chart round-trip through JSON produces valid SVG."""
        spec = PlotSpec(
            data=DataSpec(
                columns={
                    "category": ["Alpha", "Beta", "Gamma"],
                    "value": [30, 50, 20],
                }
            ),
            layers=[LayerSpec(geom="bar", x="category", y="value")],
            labels=LabelsSpec(title="Bar Chart"),
        )
        fig = Figure.from_json(spec.model_dump_json())
        assert_valid_svg(fig.to_svg())
        assert "Bar Chart" in fig.to_svg()
        assert fig.spec == spec

    def test_line_round_trip_valid_svg(self) -> None:
        """Line chart round-trip through JSON produces valid SVG."""
        spec = PlotSpec(
            data=DataSpec(
                columns={
                    "t": [0, 1, 2, 3, 4],
                    "v": [0.0, 1.0, 0.5, 1.5, 1.0],
                }
            ),
            layers=[LayerSpec(geom="line", x="t", y="v")],
            labels=LabelsSpec(title="Line Chart"),
        )
        fig = Figure.from_json(spec.model_dump_json())
        assert_valid_svg(fig.to_svg())
        assert "Line Chart" in fig.to_svg()
        assert fig.spec == spec


# ---------------------------------------------------------------------------
# from_dict: realistic LLM function-call output
# ---------------------------------------------------------------------------


class TestFromDict:
    """Figure.from_dict() accepts and renders realistic LLM output."""

    def test_from_dict_returns_figure(self) -> None:
        fig = Figure.from_dict(_llm_function_call_dict())
        assert isinstance(fig, Figure)

    def test_from_dict_produces_valid_svg(self) -> None:
        fig = Figure.from_dict(_llm_function_call_dict())
        assert_valid_svg(fig.to_svg())

    def test_from_dict_title_in_svg(self) -> None:
        fig = Figure.from_dict(_llm_function_call_dict())
        assert "Quarterly Revenue by Region" in fig.to_svg()

    def test_from_dict_spec_fields_parsed_correctly(self) -> None:
        d = _llm_function_call_dict()
        fig = Figure.from_dict(d)
        spec = fig.spec
        assert spec.theme == "substack"
        assert spec.labels.title == "Quarterly Revenue by Region"
        assert spec.layers[0].geom == "bar"
        assert spec.layers[0].color == "region"
        assert spec.size.width == 800

    def test_from_dict_scatter_spec(self) -> None:
        d = {
            "data": {
                "columns": {
                    "x": [1, 2, 3, 4, 5],
                    "y": [2.1, 3.8, 2.9, 4.5, 3.2],
                }
            },
            "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
            "labels": {"title": "LLM Scatter"},
        }
        fig = Figure.from_dict(d)
        assert_valid_svg(fig.to_svg())
        assert "LLM Scatter" in fig.to_svg()

    def test_from_dict_minimal_keys_only(self) -> None:
        """from_dict works with only the mandatory layer fields; all else defaults."""
        d: dict = {
            "data": {"columns": {"a": [10, 20], "b": [30, 40]}},
            "layers": [{"geom": "line", "x": "a", "y": "b"}],
        }
        fig = Figure.from_dict(d)
        assert_valid_svg(fig.to_svg())

    def test_from_dict_matches_from_json(self) -> None:
        """from_dict and from_json with equivalent input produce identical SVG."""
        d = _llm_function_call_dict()
        fig_dict = Figure.from_dict(d)
        fig_json = Figure.from_json(json.dumps(d))
        assert fig_dict.to_svg() == fig_json.to_svg()


# ---------------------------------------------------------------------------
# Missing required fields → clear error
# ---------------------------------------------------------------------------


class TestMissingRequiredFields:
    """Missing required fields produce informative ValidationErrors."""

    def test_layer_missing_x_from_json(self) -> None:
        bad = json.dumps(
            {
                "layers": [{"geom": "scatter", "y": "y"}],
            }
        )
        with pytest.raises(ValidationError) as exc_info:
            Figure.from_json(bad)
        # Pydantic v2 error mentions the missing field
        assert "x" in str(exc_info.value).lower()

    def test_layer_missing_y_from_dict(self) -> None:
        bad: dict = {
            "layers": [{"geom": "scatter", "x": "x"}],
        }
        with pytest.raises(ValidationError) as exc_info:
            Figure.from_dict(bad)
        assert "y" in str(exc_info.value).lower()

    def test_layer_missing_geom_from_json(self) -> None:
        bad = json.dumps(
            {
                "layers": [{"x": "x", "y": "y"}],
            }
        )
        with pytest.raises(ValidationError):
            Figure.from_json(bad)

    def test_layer_missing_geom_from_dict(self) -> None:
        bad: dict = {"layers": [{"x": "x", "y": "y"}]}
        with pytest.raises(ValidationError):
            Figure.from_dict(bad)


# ---------------------------------------------------------------------------
# Extra / unknown fields → silently ignored (Pydantic default)
# ---------------------------------------------------------------------------


class TestExtraFieldsIgnored:
    """Extra / unknown fields are silently ignored by Pydantic."""

    def test_extra_top_level_field_from_json(self) -> None:
        spec_with_extra = _scatter_spec().model_dump()
        spec_with_extra["unknown_field"] = "this_should_be_ignored"
        fig = Figure.from_json(json.dumps(spec_with_extra))
        assert isinstance(fig, Figure)
        assert_valid_svg(fig.to_svg())

    def test_extra_top_level_field_from_dict(self) -> None:
        d = _llm_function_call_dict()
        d["agent_metadata"] = {"model": "claude-opus-4-6", "confidence": 0.95}
        fig = Figure.from_dict(d)
        assert isinstance(fig, Figure)
        assert_valid_svg(fig.to_svg())

    def test_extra_nested_field_from_dict(self) -> None:
        d: dict = {
            "data": {"columns": {"x": [1, 2], "y": [3, 4]}, "source_url": "ignored"},
            "layers": [{"geom": "scatter", "x": "x", "y": "y", "opacity": 0.8}],
            "labels": {"title": "Extra Fields", "subtitle": "ignored"},
        }
        # Should not raise even though 'subtitle', 'opacity', 'source_url' are unknown
        fig = Figure.from_dict(d)
        assert_valid_svg(fig.to_svg())


# ---------------------------------------------------------------------------
# Malformed types → clear error
# ---------------------------------------------------------------------------


class TestMalformedTypes:
    """Malformed types produce clear Pydantic ValidationErrors."""

    def test_invalid_geom_from_json(self) -> None:
        bad = json.dumps(
            {
                "data": {"columns": {"x": [1], "y": [2]}},
                "layers": [{"geom": "pie", "x": "x", "y": "y"}],
            }
        )
        with pytest.raises(ValidationError) as exc_info:
            Figure.from_json(bad)
        err_str = str(exc_info.value)
        # Pydantic should mention the invalid value or the valid options
        assert "pie" in err_str or "geom" in err_str.lower()

    def test_invalid_legend_position_from_dict(self) -> None:
        d: dict = {
            "data": {"columns": {"x": [1], "y": [2]}},
            "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
            "legend": {"show": True, "position": "outside"},
        }
        with pytest.raises(ValidationError) as exc_info:
            Figure.from_dict(d)
        err_str = str(exc_info.value)
        assert "outside" in err_str or "position" in err_str.lower()

    def test_size_width_wrong_type_from_json(self) -> None:
        bad = json.dumps(
            {
                "data": {"columns": {"x": [1], "y": [2]}},
                "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
                "size": {"width": "not-a-number", "height": 500},
            }
        )
        with pytest.raises(ValidationError):
            Figure.from_json(bad)

    def test_layers_not_a_list_from_dict(self) -> None:
        d: dict = {
            "data": {"columns": {"x": [1], "y": [2]}},
            "layers": "scatter",  # should be a list
        }
        with pytest.raises(ValidationError):
            Figure.from_dict(d)

    def test_malformed_json_string(self) -> None:
        """A syntactically invalid JSON string raises a decode error."""
        with pytest.raises(Exception):
            Figure.from_json("{not valid json}")


# ---------------------------------------------------------------------------
# Empty spec → renders without error
# ---------------------------------------------------------------------------


class TestEmptySpec:
    """An empty PlotSpec (all defaults) round-trips and renders without error."""

    def test_empty_spec_from_json(self) -> None:
        empty_spec = PlotSpec()
        fig = Figure.from_json(empty_spec.model_dump_json())
        assert isinstance(fig, Figure)
        assert_valid_svg(fig.to_svg())

    def test_empty_spec_from_dict(self) -> None:
        fig = Figure.from_dict({})
        assert isinstance(fig, Figure)
        assert_valid_svg(fig.to_svg())

    def test_empty_spec_from_json_literal(self) -> None:
        fig = Figure.from_json("{}")
        assert isinstance(fig, Figure)
        assert_valid_svg(fig.to_svg())

    def test_empty_spec_spec_has_defaults(self) -> None:
        fig = Figure.from_dict({})
        spec = fig.spec
        assert spec.theme == "default"
        assert spec.layers == []
        assert spec.data.columns == {}
        assert spec.size.width == 800
        assert spec.size.height == 500

    def test_empty_spec_svg_matches_direct_figure(self) -> None:
        """from_dict({}) and Figure(PlotSpec()) produce the same SVG."""
        direct_svg = Figure(PlotSpec()).to_svg()
        json_path_svg = Figure.from_dict({}).to_svg()
        assert direct_svg == json_path_svg
