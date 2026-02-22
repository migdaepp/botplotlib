"""Shared test fixtures and helpers for botplotlib tests."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

BASELINES_DIR = Path(__file__).parent / "baselines"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-baselines",
        action="store_true",
        default=False,
        help="Regenerate golden SVG baseline files.",
    )


@pytest.fixture
def update_baselines(request: pytest.FixtureRequest) -> bool:
    return bool(request.config.getoption("--update-baselines"))


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def iris_like_data() -> dict[str, list]:
    """Small iris-like dataset for scatter/color tests."""
    return {
        "sepal_length": [5.1, 4.9, 7.0, 6.4, 6.3, 5.8],
        "sepal_width": [3.5, 3.0, 3.2, 3.2, 3.3, 2.7],
        "species": [
            "setosa",
            "setosa",
            "versicolor",
            "versicolor",
            "virginica",
            "virginica",
        ],
    }


@pytest.fixture
def time_series_data() -> dict[str, list]:
    """Simple time series dataset for line tests."""
    return {
        "x": [1, 2, 3, 4, 5, 6, 7, 8],
        "y": [10, 12, 8, 15, 13, 18, 16, 20],
        "group": ["A", "A", "A", "A", "B", "B", "B", "B"],
    }


@pytest.fixture
def categorical_data() -> dict[str, list]:
    """Categorical dataset for bar chart tests."""
    return {
        "category": ["Apple", "Banana", "Cherry", "Date"],
        "value": [23, 17, 35, 12],
    }


# ---------------------------------------------------------------------------
# SVG validation helpers
# ---------------------------------------------------------------------------


def assert_valid_svg(svg_string: str) -> ET.Element:
    """Parse SVG and assert it is well-formed XML. Returns root element."""
    root = ET.fromstring(svg_string)
    assert root.tag == "{http://www.w3.org/2000/svg}svg" or root.tag == "svg"
    return root


def count_svg_elements(svg_string: str, tag: str) -> int:
    """Count elements with a given tag in an SVG string."""
    root = ET.fromstring(svg_string)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    # Try with namespace first, then without
    count = len(root.findall(f".//svg:{tag}", ns))
    if count == 0:
        count = len(root.findall(f".//{tag}"))
    return count


def load_baseline(name: str) -> str | None:
    """Load a golden SVG baseline file. Returns None if it doesn't exist."""
    path = BASELINES_DIR / f"{name}.svg"
    if path.exists():
        return path.read_text()
    return None


def save_baseline(name: str, svg_content: str) -> None:
    """Save an SVG string as a golden baseline file."""
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    path = BASELINES_DIR / f"{name}.svg"
    path.write_text(svg_content)
