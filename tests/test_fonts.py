"""Tests for botplotlib._fonts.metrics."""

from __future__ import annotations

import pytest

from botplotlib._fonts.metrics import (
    _load_font_table,
    text_bbox,
    text_height,
    text_width,
)
from botplotlib._types import Rect

# ---------------------------------------------------------------------------
# _load_font_table
# ---------------------------------------------------------------------------


class TestLoadFontTable:
    """Tests for _load_font_table."""

    def test_arial_loads(self) -> None:
        table = _load_font_table("arial")
        assert isinstance(table, dict)
        assert len(table) > 0

    def test_inter_loads(self) -> None:
        table = _load_font_table("inter")
        assert isinstance(table, dict)
        assert len(table) > 0

    def test_arial_has_all_printable_ascii(self) -> None:
        table = _load_font_table("arial")
        for code in range(32, 127):
            ch = chr(code)
            assert ch in table, f"Missing character {ch!r} (U+{code:04X})"

    def test_inter_has_all_printable_ascii(self) -> None:
        table = _load_font_table("inter")
        for code in range(32, 127):
            ch = chr(code)
            assert ch in table, f"Missing character {ch!r} (U+{code:04X})"

    def test_all_widths_are_positive_floats(self) -> None:
        for font in ("arial", "inter"):
            table = _load_font_table(font)
            for ch, w in table.items():
                assert isinstance(w, (int, float)), f"{font}[{ch!r}] not numeric"
                assert w > 0, f"{font}[{ch!r}] width must be positive"

    def test_unknown_font_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            _load_font_table("nonexistent_font")


# ---------------------------------------------------------------------------
# text_width
# ---------------------------------------------------------------------------


class TestTextWidth:
    """Tests for text_width."""

    def test_returns_positive_float(self) -> None:
        result = text_width("hello", font_size=12)
        assert isinstance(result, float)
        assert result > 0

    def test_wider_chars_produce_wider_measurement(self) -> None:
        narrow = text_width("iii", font_size=12)
        wide = text_width("mmm", font_size=12)
        assert wide > narrow

    def test_empty_string_is_zero(self) -> None:
        assert text_width("", font_size=12) == 0.0

    def test_scales_with_font_size(self) -> None:
        small = text_width("test", font_size=10)
        large = text_width("test", font_size=20)
        assert large == pytest.approx(small * 2)

    def test_unknown_chars_use_default_width(self) -> None:
        # A non-ASCII character not in the table should use 0.5 * font_size.
        width = text_width("\u2603", font_size=10)  # snowman
        assert width == pytest.approx(0.5 * 10)

    def test_works_with_inter(self) -> None:
        result = text_width("hello", font_size=12, font_name="inter")
        assert isinstance(result, float)
        assert result > 0


# ---------------------------------------------------------------------------
# text_height
# ---------------------------------------------------------------------------


class TestTextHeight:
    """Tests for text_height."""

    def test_returns_positive_float(self) -> None:
        result = text_height(12)
        assert isinstance(result, float)
        assert result > 0

    def test_proportional_to_font_size(self) -> None:
        h10 = text_height(10)
        h20 = text_height(20)
        assert h20 == pytest.approx(h10 * 2)

    def test_standard_ratio(self) -> None:
        assert text_height(10) == pytest.approx(12.0)
        assert text_height(16) == pytest.approx(19.2)


# ---------------------------------------------------------------------------
# text_bbox
# ---------------------------------------------------------------------------


class TestTextBbox:
    """Tests for text_bbox."""

    def test_returns_rect(self) -> None:
        result = text_bbox("hello", font_size=12, x=0, y=0)
        assert isinstance(result, Rect)

    def test_start_anchor(self) -> None:
        bbox = text_bbox("hi", font_size=10, x=100, y=50, anchor="start")
        assert bbox.x == 100
        assert bbox.y == 50
        assert bbox.width > 0
        assert bbox.height == pytest.approx(12.0)

    def test_middle_anchor(self) -> None:
        bbox = text_bbox("hi", font_size=10, x=100, y=50, anchor="middle")
        w = text_width("hi", font_size=10)
        assert bbox.x == pytest.approx(100 - w / 2)
        assert bbox.width == pytest.approx(w)

    def test_end_anchor(self) -> None:
        bbox = text_bbox("hi", font_size=10, x=100, y=50, anchor="end")
        w = text_width("hi", font_size=10)
        assert bbox.x == pytest.approx(100 - w)
        assert bbox.width == pytest.approx(w)

    def test_height_matches_text_height(self) -> None:
        bbox = text_bbox("test", font_size=14, x=0, y=0)
        assert bbox.height == pytest.approx(text_height(14))

    def test_width_matches_text_width(self) -> None:
        bbox = text_bbox("test", font_size=14, x=0, y=0, font_name="inter")
        assert bbox.width == pytest.approx(
            text_width("test", font_size=14, font_name="inter")
        )
