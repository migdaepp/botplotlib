from __future__ import annotations
from dataclasses import dataclass

@dataclass
class LinearScale:
    """Maps numeric values linearly to pixel range."""
    data_min: float
    data_max: float
    pixel_min: float
    pixel_max: float

    def map(self, value: float) -> float:
        """Map a data value to pixel position."""
        if self.data_max == self.data_min:
            return (self.pixel_min + self.pixel_max) / 2
        t = (value - self.data_min) / (self.data_max - self.data_min)
        return self.pixel_min + t * (self.pixel_max - self.pixel_min)

    def invert(self, pixel: float) -> float:
        """Map a pixel position back to data value."""
        if self.pixel_max == self.pixel_min:
            return (self.data_min + self.data_max) / 2
        t = (pixel - self.pixel_min) / (self.pixel_max - self.pixel_min)
        return self.data_min + t * (self.data_max - self.data_min)

@dataclass
class CategoricalScale:
    """Maps categorical values to evenly-spaced pixel positions."""
    categories: list[str]
    pixel_min: float
    pixel_max: float

    def map(self, category: str) -> float:
        """Map a category to its center pixel position."""
        idx = self.categories.index(category)
        n = len(self.categories)
        band_width = (self.pixel_max - self.pixel_min) / n
        return self.pixel_min + band_width * (idx + 0.5)

    @property
    def band_width(self) -> float:
        """Width of each category band in pixels."""
        return (self.pixel_max - self.pixel_min) / len(self.categories)
