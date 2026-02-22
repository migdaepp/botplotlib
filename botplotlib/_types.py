"""Core geometric types used throughout botplotlib."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """A 2D point in pixel coordinates."""

    x: float
    y: float


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle in pixel coordinates."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def intersects(self, other: Rect) -> bool:
        """Check if this rectangle overlaps with another."""
        return (
            self.x < other.right
            and self.right > other.x
            and self.y < other.bottom
            and self.bottom > other.y
        )


@dataclass(frozen=True)
class TickMark:
    """A tick mark on an axis."""

    value: float
    label: str
    pixel_pos: float
