"""Tests for botplotlib.compiler.accessibility."""

from __future__ import annotations

import pytest

from botplotlib.compiler.accessibility import (
    ContrastError,
    check_adjacent_contrast,
    check_palette_contrast,
    check_text_contrast,
    validate_theme_accessibility,
)


class TestCheckTextContrast:
    """Tests for WCAG text contrast checking."""

    def test_black_on_white_passes(self) -> None:
        # 21:1 ratio — well above any threshold
        check_text_contrast("#000000", "#FFFFFF")

    def test_white_on_black_passes(self) -> None:
        check_text_contrast("#FFFFFF", "#000000")

    def test_low_contrast_fails(self) -> None:
        # Light gray on white — very low contrast
        with pytest.raises(ContrastError, match="below"):
            check_text_contrast("#CCCCCC", "#FFFFFF")

    def test_large_text_has_lower_threshold(self) -> None:
        # Medium contrast that passes large text but fails normal text
        # #767676 on white is about 4.54:1 — passes normal text
        # #959595 on white is about 2.86:1 — fails normal text, fails large text too
        # #757575 on white is about 4.6:1 — passes both
        # Let's use a color that's between 3.0 and 4.5 contrast
        # #888888 on white ≈ 3.54:1
        with pytest.raises(ContrastError):
            check_text_contrast("#888888", "#FFFFFF", font_size=12.0)
        # Same color passes for large text (threshold 3.0)
        check_text_contrast("#888888", "#FFFFFF", font_size=18.0)


class TestCheckPaletteContrast:
    """Tests for palette-vs-background contrast."""

    def test_dark_palette_on_white_passes(self) -> None:
        palette = ["#000000", "#333333", "#666666"]
        check_palette_contrast(palette, "#FFFFFF")

    def test_light_palette_on_white_fails(self) -> None:
        palette = ["#000000", "#FAFAFA"]  # near-white on white
        with pytest.raises(ContrastError, match="Palette color 1"):
            check_palette_contrast(palette, "#FFFFFF")

    def test_custom_min_ratio(self) -> None:
        palette = ["#888888"]  # ~3.54:1 against white
        # Passes at 3.0 threshold
        check_palette_contrast(palette, "#FFFFFF", min_ratio=3.0)
        # Fails at 4.0 threshold
        with pytest.raises(ContrastError):
            check_palette_contrast(palette, "#FFFFFF", min_ratio=4.0)


class TestCheckAdjacentContrast:
    """Tests for adjacent palette color distinguishability."""

    def test_distinct_colors_pass(self) -> None:
        palette = ["#000000", "#FFFFFF", "#FF0000"]
        check_adjacent_contrast(palette)

    def test_similar_colors_fail(self) -> None:
        palette = ["#808080", "#818181"]
        with pytest.raises(ContrastError, match="Adjacent"):
            check_adjacent_contrast(palette)


class TestValidateThemeAccessibility:
    """Tests for the full theme validation."""

    def test_default_theme_passes(self) -> None:
        from botplotlib._colors.palettes import DEFAULT_PALETTE

        # The default theme colors should pass all checks
        validate_theme_accessibility(
            text_color="#333333",
            background_color="#FFFFFF",
            palette=DEFAULT_PALETTE,
        )

    def test_bad_text_color_fails(self) -> None:
        with pytest.raises(ContrastError):
            validate_theme_accessibility(
                text_color="#DDDDDD",
                background_color="#FFFFFF",
                palette=["#000000"],
            )

    def test_bad_palette_fails(self) -> None:
        with pytest.raises(ContrastError):
            validate_theme_accessibility(
                text_color="#000000",
                background_color="#FFFFFF",
                palette=["#FEFEFE"],
            )
