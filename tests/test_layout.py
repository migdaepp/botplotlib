"""Tests for botplotlib.compiler.layout."""

from __future__ import annotations

from botplotlib.compiler.layout import (
    TextLabel,
    avoid_collisions,
    compute_layout,
)


class TestComputeLayout:
    """Tests for the box-model layout engine."""

    def test_basic_layout(self) -> None:
        result = compute_layout(800, 500, 40, 20, 50, 60)
        assert result.canvas_width == 800
        assert result.canvas_height == 500
        assert result.plot_area.x == 60
        assert result.plot_area.y == 40
        assert result.plot_area.width == 800 - 60 - 20
        assert result.plot_area.height == 500 - 40 - 50

    def test_title_adds_top_margin(self) -> None:
        without = compute_layout(800, 500, 40, 20, 50, 60, has_title=False)
        with_title = compute_layout(800, 500, 40, 20, 50, 60, has_title=True)
        assert with_title.plot_area.y > without.plot_area.y
        assert with_title.title_pos is not None

    def test_x_label_adds_bottom_margin(self) -> None:
        without = compute_layout(800, 500, 40, 20, 50, 60, has_x_label=False)
        with_label = compute_layout(800, 500, 40, 20, 50, 60, has_x_label=True)
        assert with_label.plot_area.height < without.plot_area.height
        assert with_label.x_label_pos is not None

    def test_y_label_adds_left_margin(self) -> None:
        without = compute_layout(800, 500, 40, 20, 50, 60, has_y_label=False)
        with_label = compute_layout(800, 500, 40, 20, 50, 60, has_y_label=True)
        assert with_label.plot_area.x > without.plot_area.x
        assert with_label.y_label_pos is not None

    def test_legend_right_reduces_plot_width(self) -> None:
        without = compute_layout(800, 500, 40, 20, 50, 60, has_legend=False)
        with_legend = compute_layout(
            800,
            500,
            40,
            20,
            50,
            60,
            has_legend=True,
            legend_position="right",
        )
        assert with_legend.plot_area.width < without.plot_area.width
        assert with_legend.legend_area is not None

    def test_no_title_returns_none(self) -> None:
        result = compute_layout(800, 500, 40, 20, 50, 60, has_title=False)
        assert result.title_pos is None


class TestAvoidCollisions:
    """Tests for the ggrepel-style collision avoidance."""

    def test_no_labels(self) -> None:
        result = avoid_collisions([])
        assert result == []

    def test_single_label_unchanged(self) -> None:
        labels = [TextLabel("hello", 100, 100, 12)]
        result = avoid_collisions(labels)
        assert len(result) == 1
        assert result[0].x == 100
        assert result[0].y == 100

    def test_non_overlapping_unchanged(self) -> None:
        labels = [
            TextLabel("A", 50, 50, 12),
            TextLabel("B", 300, 300, 12),
        ]
        result = avoid_collisions(labels)
        # Should not have moved significantly
        assert abs(result[0].y - 50) < 1
        assert abs(result[1].y - 300) < 1

    def test_overlapping_labels_separated(self) -> None:
        # Place two labels at the exact same position
        labels = [
            TextLabel("Label A", 100, 100, 12),
            TextLabel("Label B", 100, 100, 12),
        ]
        result = avoid_collisions(labels)
        # They should be nudged apart
        assert result[0].y != result[1].y
