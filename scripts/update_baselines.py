#!/usr/bin/env python3
"""Regenerate all golden SVG baseline files.

This script renders reference specs and saves the output as golden SVGs
in tests/baselines/. Maps to the `update_baselines` orchestration tool
(destructiveHint: true) in AGENTS.md.

Usage:
    uv run python scripts/update_baselines.py
    # or via pytest:
    uv run pytest --update-baselines
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> None:
    from botplotlib import bar, line, scatter

    baselines_dir = Path(__file__).parent.parent / "tests" / "baselines"
    baselines_dir.mkdir(parents=True, exist_ok=True)

    # Reference specs for baseline generation
    specs = {
        "scatter_basic": lambda: scatter(
            {"x": [1, 2, 3, 4, 5], "y": [2, 4, 1, 5, 3]},
            x="x",
            y="y",
            title="Basic Scatter",
        ),
        "scatter_color": lambda: scatter(
            {
                "x": [1, 2, 3, 4, 5, 6],
                "y": [2, 4, 1, 5, 3, 6],
                "g": ["A", "A", "A", "B", "B", "B"],
            },
            x="x",
            y="y",
            color="g",
            title="Scatter with Color",
        ),
        "line_basic": lambda: line(
            {"x": [1, 2, 3, 4, 5], "y": [10, 20, 15, 25, 18]},
            x="x",
            y="y",
            title="Basic Line",
        ),
        "bar_basic": lambda: bar(
            {
                "category": ["A", "B", "C", "D"],
                "value": [23, 17, 35, 12],
            },
            x="category",
            y="value",
            title="Basic Bar",
        ),
    }

    for name, create_fig in specs.items():
        fig = create_fig()
        svg = fig.to_svg()
        path = baselines_dir / f"{name}.svg"
        path.write_text(svg)
        print(f"  Updated: {path}")

    print(f"\nDone. {len(specs)} baselines updated.")


if __name__ == "__main__":
    main()
