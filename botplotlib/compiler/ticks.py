"""Tick generation using the Heckbert nice numbers algorithm.

Reference:
    Paul S. Heckbert, "Nice Numbers for Graph Labels",
    *Graphics Gems*, Academic Press, 1990, pp. 61-63.
"""

from __future__ import annotations

import math


def nice_num(x: float, round_down: bool = False) -> float:
    """Return a "nice" number approximately equal to *x*.

    A nice number is 1, 2, or 5 times a power of 10.  When *round_down* is
    ``False`` (the default) the result is >= *x*; when ``True`` the result
    is <= *x*.

    Parameters
    ----------
    x:
        A positive number.
    round_down:
        If ``True``, return the largest nice number <= *x*.
        If ``False``, return the smallest nice number >= *x*.

    Returns
    -------
    float
        A nice number (1, 2, or 5 times a power of 10).
    """
    if x <= 0:
        raise ValueError(f"x must be positive, got {x}")

    exp = math.floor(math.log10(x))
    frac = x / (10**exp)  # fraction in [1, 10)

    if round_down:
        if frac < 2:
            nice = 1.0
        elif frac < 5:
            nice = 2.0
        else:
            nice = 5.0
    else:
        if frac <= 1:
            nice = 1.0
        elif frac <= 2:
            nice = 2.0
        elif frac <= 5:
            nice = 5.0
        else:
            nice = 10.0

    return nice * (10**exp)


def nice_ticks(
    data_min: float, data_max: float, max_ticks: int = 7
) -> list[float]:
    """Generate nicely spaced tick values covering *data_min* .. *data_max*.

    Uses Heckbert's algorithm to choose a "nice" tick spacing, then
    generates tick values that span the data range.

    Edge cases
    ----------
    * If *data_min* == *data_max*, the range is padded by 1 in each
      direction (or by the absolute value when non-zero) so that
      meaningful ticks are still produced.
    * Negative values, very small ranges, and zero-crossing ranges are
      handled gracefully.

    Parameters
    ----------
    data_min:
        Minimum data value.
    data_max:
        Maximum data value.
    max_ticks:
        Desired maximum number of tick marks (default 7).

    Returns
    -------
    list[float]
        Sorted list of tick values.
    """
    if max_ticks < 2:
        max_ticks = 2

    # Handle equal min/max: pad the range so we get real ticks.
    if data_min == data_max:
        if data_min == 0:
            data_min, data_max = -1.0, 1.0
        else:
            pad = abs(data_min)
            data_min = data_min - pad
            data_max = data_max + pad

    # Ensure min < max
    if data_min > data_max:
        data_min, data_max = data_max, data_min

    data_range = data_max - data_min

    # Guard against near-zero ranges caused by floating-point dust.
    if data_range < 1e-15:
        return [data_min]

    tick_spacing = nice_num(data_range / (max_ticks - 1))
    graph_min = math.floor(data_min / tick_spacing) * tick_spacing
    graph_max = math.ceil(data_max / tick_spacing) * tick_spacing

    # Build the list of tick values.
    ticks: list[float] = []
    # Determine decimal places to use for rounding, avoiding float noise.
    # We round to enough decimal places to represent the tick spacing
    # faithfully.
    if tick_spacing > 0:
        nfrac = max(0, -math.floor(math.log10(tick_spacing))) + 1
    else:
        nfrac = 0

    t = graph_min
    # Use a generous upper bound to avoid infinite loops from float drift.
    while t <= graph_max + tick_spacing * 0.5:
        ticks.append(round(t, nfrac))
        t += tick_spacing

    # Remove any duplicate ticks that might appear due to rounding.
    seen: set[float] = set()
    unique: list[float] = []
    for v in ticks:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    ticks = unique

    return ticks


def format_tick(value: float) -> str:
    """Format a tick value for display on an axis.

    * Whole numbers are shown without a decimal point (``2.0`` -> ``"2"``).
    * Fractional values have trailing zeros stripped (``0.10`` -> ``"0.1"``).

    Parameters
    ----------
    value:
        The numeric tick value.

    Returns
    -------
    str
        A human-friendly string representation.
    """
    if value == int(value) and math.isfinite(value):
        return str(int(value))
    # Format with enough precision, then strip trailing zeros.
    formatted = f"{value:.10g}"
    return formatted
