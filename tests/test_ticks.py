"""Tests for the tick generation module (Heckbert nice numbers)."""

from __future__ import annotations

import pytest

from botplotlib.compiler.ticks import format_tick, nice_num, nice_ticks

# ---------------------------------------------------------------------------
# nice_num
# ---------------------------------------------------------------------------


class TestNiceNum:
    """Tests for the Heckbert nice_num helper."""

    def test_round_up_1_5(self) -> None:
        assert nice_num(1.5) == 2.0

    def test_round_up_3_5(self) -> None:
        assert nice_num(3.5) == 5.0

    def test_round_up_7(self) -> None:
        assert nice_num(7.0) == 10.0

    def test_round_up_0_15(self) -> None:
        assert nice_num(0.15) == 0.2

    def test_round_up_exact_1(self) -> None:
        assert nice_num(1.0) == 1.0

    def test_round_up_exact_2(self) -> None:
        assert nice_num(2.0) == 2.0

    def test_round_up_exact_5(self) -> None:
        assert nice_num(5.0) == 5.0

    def test_round_up_exact_10(self) -> None:
        assert nice_num(10.0) == 10.0

    def test_round_up_small(self) -> None:
        assert nice_num(0.03) == 0.05

    def test_round_up_large(self) -> None:
        assert nice_num(750.0) == 1000.0

    def test_round_down_1_5(self) -> None:
        assert nice_num(1.5, round_down=True) == 1.0

    def test_round_down_3_5(self) -> None:
        assert nice_num(3.5, round_down=True) == 2.0

    def test_round_down_7(self) -> None:
        assert nice_num(7.0, round_down=True) == 5.0

    def test_round_down_0_15(self) -> None:
        assert nice_num(0.15, round_down=True) == 0.1

    def test_round_down_large(self) -> None:
        assert nice_num(750.0, round_down=True) == 500.0

    def test_rejects_zero(self) -> None:
        with pytest.raises(ValueError):
            nice_num(0)

    def test_rejects_negative(self) -> None:
        with pytest.raises(ValueError):
            nice_num(-5)


# ---------------------------------------------------------------------------
# nice_ticks
# ---------------------------------------------------------------------------


class TestNiceTicks:
    """Tests for the nice_ticks generator."""

    def test_range_0_to_10(self) -> None:
        ticks = nice_ticks(0, 10)
        assert ticks[0] <= 0
        assert ticks[-1] >= 10
        assert len(ticks) >= 3
        assert len(ticks) <= 8  # max_ticks default is 7, +1 tolerance

    def test_range_0_to_100(self) -> None:
        ticks = nice_ticks(0, 100)
        assert ticks[0] <= 0
        assert ticks[-1] >= 100
        assert len(ticks) >= 3

    def test_range_negative(self) -> None:
        ticks = nice_ticks(-5, 5)
        assert ticks[0] <= -5
        assert ticks[-1] >= 5
        assert any(t < 0 for t in ticks)
        assert any(t > 0 for t in ticks)

    def test_range_fractional(self) -> None:
        ticks = nice_ticks(0.1, 0.9)
        assert ticks[0] <= 0.1
        assert ticks[-1] >= 0.9
        assert len(ticks) >= 3

    def test_equal_min_max_nonzero(self) -> None:
        ticks = nice_ticks(5, 5)
        assert len(ticks) >= 3
        # Should still produce a meaningful range around the value.
        assert ticks[0] <= 5
        assert ticks[-1] >= 5

    def test_equal_min_max_zero(self) -> None:
        ticks = nice_ticks(0, 0)
        assert len(ticks) >= 3
        assert any(t < 0 for t in ticks)
        assert any(t > 0 for t in ticks)

    def test_ticks_sorted(self) -> None:
        ticks = nice_ticks(3, 97)
        assert ticks == sorted(ticks)

    def test_ticks_no_duplicates(self) -> None:
        ticks = nice_ticks(0, 10)
        assert len(ticks) == len(set(ticks))

    def test_tick_count_respects_max(self) -> None:
        for max_t in (5, 7, 10):
            ticks = nice_ticks(0, 100, max_ticks=max_t)
            assert len(ticks) >= 3
            assert len(ticks) <= max_t + 1

    def test_reversed_min_max(self) -> None:
        """Passing data_min > data_max should still work."""
        ticks = nice_ticks(10, 0)
        assert ticks[0] <= 0
        assert ticks[-1] >= 10

    def test_very_small_range(self) -> None:
        ticks = nice_ticks(1.0, 1.0001)
        assert len(ticks) >= 2

    def test_large_range(self) -> None:
        ticks = nice_ticks(0, 1_000_000)
        assert ticks[0] <= 0
        assert ticks[-1] >= 1_000_000


# ---------------------------------------------------------------------------
# format_tick
# ---------------------------------------------------------------------------


class TestFormatTick:
    """Tests for the format_tick display formatter."""

    def test_whole_number(self) -> None:
        assert format_tick(2.0) == "2"

    def test_integer_value(self) -> None:
        assert format_tick(100.0) == "100"

    def test_negative_whole(self) -> None:
        assert format_tick(-3.0) == "-3"

    def test_zero(self) -> None:
        assert format_tick(0.0) == "0"

    def test_fractional(self) -> None:
        assert format_tick(1.5) == "1.5"

    def test_trailing_zeros_removed(self) -> None:
        # 0.10 should display as "0.1", not "0.10"
        assert format_tick(0.1) == "0.1"

    def test_long_fraction(self) -> None:
        assert format_tick(0.25) == "0.25"

    def test_negative_fraction(self) -> None:
        assert format_tick(-0.5) == "-0.5"

    def test_large_integer(self) -> None:
        assert format_tick(10000.0) == "10000"
