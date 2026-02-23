"""Tests for botplotlib._colors.palettes."""

from __future__ import annotations

import re

import pytest

from botplotlib._colors.palettes import (
    DEFAULT_PALETTE,
    assign_colors,
    contrast_ratio,
    hex_to_rgb,
    relative_luminance,
    rgb_to_hex,
)

# ---------------------------------------------------------------------------
# hex_to_rgb
# ---------------------------------------------------------------------------


class TestHexToRgb:
    """Tests for hex_to_rgb."""

    def test_long_form_with_hash(self) -> None:
        assert hex_to_rgb("#FF8800") == (255, 136, 0)

    def test_long_form_without_hash(self) -> None:
        assert hex_to_rgb("FF8800") == (255, 136, 0)

    def test_short_form_with_hash(self) -> None:
        assert hex_to_rgb("#abc") == (0xAA, 0xBB, 0xCC)

    def test_short_form_without_hash(self) -> None:
        assert hex_to_rgb("abc") == (0xAA, 0xBB, 0xCC)

    def test_lowercase(self) -> None:
        assert hex_to_rgb("#ff0000") == (255, 0, 0)

    def test_black(self) -> None:
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self) -> None:
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_invalid_length_raises(self) -> None:
        with pytest.raises(ValueError):
            hex_to_rgb("#12345")


# ---------------------------------------------------------------------------
# rgb_to_hex
# ---------------------------------------------------------------------------


class TestRgbToHex:
    """Tests for rgb_to_hex."""

    def test_basic(self) -> None:
        assert rgb_to_hex(255, 136, 0) == "#FF8800"

    def test_black(self) -> None:
        assert rgb_to_hex(0, 0, 0) == "#000000"

    def test_white(self) -> None:
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"

    def test_single_digit_channels_are_zero_padded(self) -> None:
        result = rgb_to_hex(1, 2, 3)
        assert result == "#010203"
        assert len(result) == 7


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """hex_to_rgb -> rgb_to_hex should be lossless."""

    @pytest.mark.parametrize(
        "hex_color",
        ["#000000", "#FFFFFF", "#4E79A7", "#F28E2B", "#123456"],
    )
    def test_round_trip(self, hex_color: str) -> None:
        r, g, b = hex_to_rgb(hex_color)
        assert rgb_to_hex(r, g, b) == hex_color


# ---------------------------------------------------------------------------
# assign_colors
# ---------------------------------------------------------------------------


class TestAssignColors:
    """Tests for assign_colors."""

    def test_fewer_groups_than_palette(self) -> None:
        groups = ["A", "B", "C"]
        result = assign_colors(groups)
        assert list(result.keys()) == ["A", "B", "C"]
        assert result["A"] == DEFAULT_PALETTE[0]
        assert result["B"] == DEFAULT_PALETTE[1]
        assert result["C"] == DEFAULT_PALETTE[2]

    def test_more_groups_than_palette(self) -> None:
        palette = ["#AA0000", "#00BB00"]
        groups = ["x", "y", "z"]
        result = assign_colors(groups, palette=palette)
        assert result["x"] == "#AA0000"
        assert result["y"] == "#00BB00"
        assert result["z"] == "#AA0000"  # cycles back

    def test_consistent_ordering(self) -> None:
        """The same input should always produce the same mapping."""
        groups = ["cat", "dog", "fish"]
        result1 = assign_colors(groups)
        result2 = assign_colors(groups)
        assert result1 == result2
        assert list(result1.keys()) == groups

    def test_duplicates_are_deduplicated(self) -> None:
        groups = ["A", "B", "A", "C", "B"]
        result = assign_colors(groups)
        assert list(result.keys()) == ["A", "B", "C"]
        assert result["A"] == DEFAULT_PALETTE[0]
        assert result["B"] == DEFAULT_PALETTE[1]
        assert result["C"] == DEFAULT_PALETTE[2]

    def test_uses_default_palette_when_none(self) -> None:
        groups = ["only"]
        result = assign_colors(groups, palette=None)
        assert result["only"] == DEFAULT_PALETTE[0]


# ---------------------------------------------------------------------------
# relative_luminance
# ---------------------------------------------------------------------------


class TestRelativeLuminance:
    """Tests for relative_luminance (WCAG)."""

    def test_white(self) -> None:
        assert relative_luminance("#FFFFFF") == pytest.approx(1.0)

    def test_black(self) -> None:
        assert relative_luminance("#000000") == pytest.approx(0.0)

    def test_mid_gray(self) -> None:
        # sRGB (127,127,127) should give a luminance around 0.212
        lum = relative_luminance("#7F7F7F")
        assert 0.0 < lum < 1.0

    def test_pure_red(self) -> None:
        lum = relative_luminance("#FF0000")
        assert lum == pytest.approx(0.2126, abs=1e-4)

    def test_pure_green(self) -> None:
        lum = relative_luminance("#00FF00")
        assert lum == pytest.approx(0.7152, abs=1e-4)

    def test_pure_blue(self) -> None:
        lum = relative_luminance("#0000FF")
        assert lum == pytest.approx(0.0722, abs=1e-4)


# ---------------------------------------------------------------------------
# contrast_ratio
# ---------------------------------------------------------------------------


class TestContrastRatio:
    """Tests for contrast_ratio (WCAG)."""

    def test_black_and_white(self) -> None:
        ratio = contrast_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, abs=0.05)

    def test_same_color(self) -> None:
        ratio = contrast_ratio("#4E79A7", "#4E79A7")
        assert ratio == pytest.approx(1.0)

    def test_order_independent(self) -> None:
        ratio1 = contrast_ratio("#000000", "#FFFFFF")
        ratio2 = contrast_ratio("#FFFFFF", "#000000")
        assert ratio1 == pytest.approx(ratio2)

    def test_range(self) -> None:
        ratio = contrast_ratio("#4E79A7", "#F28E2B")
        assert 1.0 <= ratio <= 21.0


# ---------------------------------------------------------------------------
# DEFAULT_PALETTE validation
# ---------------------------------------------------------------------------


class TestDefaultPalette:
    """Validate the default palette constant."""

    def test_has_10_entries(self) -> None:
        assert len(DEFAULT_PALETTE) == 10

    def test_all_valid_hex(self) -> None:
        hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for color in DEFAULT_PALETTE:
            assert hex_re.match(color), f"{color!r} is not a valid 6-digit hex color"

    def test_all_unique(self) -> None:
        assert len(set(DEFAULT_PALETTE)) == len(DEFAULT_PALETTE)
