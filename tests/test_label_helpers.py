"""Unit tests for label formatting and placement helpers."""

from __future__ import annotations

from botplotlib.geoms.labels import format_label, label_fits_inside


class TestFormatLabel:
    """format_label() formatting logic."""

    def test_integer_value(self) -> None:
        assert format_label(38000.0) == "38000"

    def test_float_value(self) -> None:
        assert format_label(3.14) == "3.14"

    def test_zero(self) -> None:
        assert format_label(0.0) == "0"

    def test_negative_integer(self) -> None:
        assert format_label(-42.0) == "-42"

    def test_custom_currency_format(self) -> None:
        assert format_label(38000, "${:,.0f}") == "$38,000"

    def test_custom_percentage_format(self) -> None:
        assert format_label(0.75, "{:.0%}") == "75%"

    def test_custom_decimal_format(self) -> None:
        assert format_label(3.14159, "{:.2f}") == "3.14"


class TestLabelFitsInside:
    """label_fits_inside() placement decision."""

    def test_fits_inside_large_bar(self) -> None:
        assert label_fits_inside("100", font_size=10, bar_width=100, bar_height=50)

    def test_does_not_fit_narrow_bar(self) -> None:
        assert not label_fits_inside(
            "100000",
            font_size=10,
            bar_width=20,
            bar_height=50,
        )

    def test_does_not_fit_short_bar(self) -> None:
        assert not label_fits_inside("100", font_size=10, bar_width=100, bar_height=5)

    def test_padding_matters(self) -> None:
        # With large padding, even a small label may not fit
        assert not label_fits_inside(
            "1",
            font_size=10,
            bar_width=15,
            bar_height=15,
            padding=10.0,
        )
