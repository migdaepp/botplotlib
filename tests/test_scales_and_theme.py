import pytest
from botplotlib.spec.scales import LinearScale, CategoricalScale
from botplotlib.spec.theme import (
    ThemeSpec, DEFAULT_THEME, THEME_REGISTRY, resolve_theme,
)


# ---------------------------------------------------------------------------
# LinearScale tests
# ---------------------------------------------------------------------------

class TestLinearScale:
    def test_map_endpoints(self):
        """Map at data endpoints returns pixel endpoints."""
        scale = LinearScale(data_min=0, data_max=100, pixel_min=0, pixel_max=500)
        assert scale.map(0) == 0.0
        assert scale.map(100) == 500.0

    def test_map_midpoint(self):
        """Map at data midpoint returns pixel midpoint."""
        scale = LinearScale(data_min=0, data_max=100, pixel_min=0, pixel_max=500)
        assert scale.map(50) == 250.0

    def test_map_equal_data_min_max(self):
        """When data_min == data_max, map returns pixel center."""
        scale = LinearScale(data_min=5, data_max=5, pixel_min=100, pixel_max=300)
        assert scale.map(5) == 200.0

    def test_invert_round_trip(self):
        """Mapping then inverting returns the original value."""
        scale = LinearScale(data_min=10, data_max=50, pixel_min=0, pixel_max=400)
        for value in [10, 25, 37.5, 50]:
            pixel = scale.map(value)
            recovered = scale.invert(pixel)
            assert recovered == pytest.approx(value)

    def test_invert_equal_pixel_min_max(self):
        """When pixel_min == pixel_max, invert returns data center."""
        scale = LinearScale(data_min=0, data_max=100, pixel_min=200, pixel_max=200)
        assert scale.invert(200) == 50.0


# ---------------------------------------------------------------------------
# CategoricalScale tests
# ---------------------------------------------------------------------------

class TestCategoricalScale:
    def test_map_returns_band_center(self):
        """Each category maps to the center of its band."""
        categories = ["A", "B", "C"]
        scale = CategoricalScale(categories=categories, pixel_min=0, pixel_max=300)
        # band_width = 100, so centers are 50, 150, 250
        assert scale.map("A") == pytest.approx(50.0)
        assert scale.map("B") == pytest.approx(150.0)
        assert scale.map("C") == pytest.approx(250.0)

    def test_band_width(self):
        """band_width divides pixel range evenly among categories."""
        scale = CategoricalScale(categories=["x", "y", "z", "w"], pixel_min=0, pixel_max=400)
        assert scale.band_width == pytest.approx(100.0)

    def test_map_unknown_category_raises(self):
        """Mapping an unknown category raises ValueError."""
        scale = CategoricalScale(categories=["A", "B"], pixel_min=0, pixel_max=200)
        with pytest.raises(ValueError):
            scale.map("Z")


# ---------------------------------------------------------------------------
# ThemeSpec / theme registry tests
# ---------------------------------------------------------------------------

class TestThemeSpec:
    def test_default_theme_values(self):
        """DEFAULT_THEME has the expected factory defaults."""
        t = DEFAULT_THEME
        assert t.background_color == "#FFFFFF"
        assert t.title_font_size == 16
        assert t.label_font_size == 12
        assert t.tick_font_size == 10
        assert t.show_x_grid is False
        assert t.show_y_grid is True
        assert t.show_x_axis is True
        assert t.show_y_axis is False
        assert t.line_width == 2.0
        assert t.point_radius == 4.0
        assert t.bar_padding == pytest.approx(0.2)
        assert len(t.palette) == 10
        assert t.margin_top == 40
        assert t.margin_right == 20
        assert t.margin_bottom == 50
        assert t.margin_left == 60

    def test_preset_themes_in_registry(self):
        """All expected preset names are present in the registry."""
        expected_names = {"default", "bluesky", "social", "substack", "print"}
        assert expected_names.issubset(THEME_REGISTRY.keys())

    def test_resolve_theme_returns_correct_theme(self):
        """resolve_theme returns the matching ThemeSpec instance."""
        assert resolve_theme("default") is DEFAULT_THEME
        assert resolve_theme("bluesky").title_font_size == 20
        assert resolve_theme("print").text_color == "#000000"

    def test_resolve_theme_unknown_raises(self):
        """resolve_theme raises ValueError for an unknown name."""
        with pytest.raises(ValueError, match="Unknown theme 'nonexistent'"):
            resolve_theme("nonexistent")

    def test_theme_json_round_trip(self):
        """A ThemeSpec survives JSON serialization and deserialization."""
        original = ThemeSpec(title_font_size=24, palette=["#FF0000", "#00FF00"])
        json_str = original.model_dump_json()
        restored = ThemeSpec.model_validate_json(json_str)
        assert restored == original
