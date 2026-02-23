"""Tests for the figure critic SVG quality checker."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

# Add project root for script imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.figure_critic import (
    SvgText,
    check_contrast,
    check_min_font_size,
    check_text_clipping,
    check_text_overlap,
    check_tight_spacing,
    critique_svg,
    parse_svg_canvas,
    parse_svg_texts,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _write_svg(tmp_path: Path, body: str, width: int = 200, height: int = 200) -> Path:
    """Write a minimal SVG file and return its path."""
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{width}" height="{height}"'
        f' viewBox="0 0 {width} {height}">\n'
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>\n'
        f"  {body}\n"
        "</svg>\n"
    )
    path = tmp_path / "test.svg"
    path.write_text(svg)
    return path


# ---------------------------------------------------------------------------
# parse_svg_texts
# ---------------------------------------------------------------------------


def test_parse_svg_texts(tmp_path: Path) -> None:
    body = (
        '<text x="50" y="30" font-size="14" text-anchor="middle" '
        'fill="#333333" font-family="Inter, Arial">Hello</text>'
    )
    path = _write_svg(tmp_path, body)
    texts = parse_svg_texts(path)

    assert len(texts) == 1
    t = texts[0]
    assert t.x == 50.0
    assert t.y == 30.0
    assert t.font_size == 14.0
    assert t.text_anchor == "middle"
    assert t.content == "Hello"
    assert t.fill == "#333333"
    assert t.font_name == "inter"


def test_parse_svg_texts_rotation(tmp_path: Path) -> None:
    body = (
        '<text x="10" y="100" font-size="12" fill="#000000" '
        'text-anchor="middle" transform="rotate(-90,10,100)">Y axis</text>'
    )
    path = _write_svg(tmp_path, body)
    texts = parse_svg_texts(path)

    assert len(texts) == 1
    t = texts[0]
    assert t.rotation == -90.0
    assert t.rotation_cx == 10.0
    assert t.rotation_cy == 100.0


# ---------------------------------------------------------------------------
# check_text_overlap
# ---------------------------------------------------------------------------


def test_overlap_detected() -> None:
    # Two texts at the exact same position → guaranteed overlap
    texts = [
        SvgText(
            x=50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="Hello",
            fill="#000000",
        ),
        SvgText(
            x=50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="World",
            fill="#000000",
        ),
    ]
    issues = check_text_overlap(texts)
    assert len(issues) >= 1
    assert issues[0].check == "text_overlap"
    assert issues[0].severity == "error"


def test_no_overlap_clean() -> None:
    # Two texts far apart → no overlap
    texts = [
        SvgText(
            x=10, y=20, font_size=10, text_anchor="start", content="A", fill="#000000"
        ),
        SvgText(
            x=500, y=400, font_size=10, text_anchor="start", content="B", fill="#000000"
        ),
    ]
    issues = check_text_overlap(texts)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# check_text_clipping
# ---------------------------------------------------------------------------


def test_clipping_detected() -> None:
    # Text at x=-50 with start anchor → left edge is at -50
    texts = [
        SvgText(
            x=-50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="Clipped",
            fill="#000000",
        ),
    ]
    issues = check_text_clipping(texts, width=200, height=200)
    assert len(issues) == 1
    assert issues[0].check == "text_clipping"
    assert issues[0].severity == "error"
    assert "left" in issues[0].details["directions"]


def test_clipping_bottom() -> None:
    # Text near the bottom of the canvas
    texts = [
        SvgText(
            x=50,
            y=200,
            font_size=12,
            text_anchor="start",
            content="Bottom",
            fill="#000000",
        ),
    ]
    # bbox bottom = y - font_size + font_size * 1.2 = y + 0.2 * font_size
    # = 200 + 2.4 = 202.4 > 200
    issues = check_text_clipping(texts, width=200, height=200)
    assert len(issues) == 1
    assert "bottom" in issues[0].details["directions"]


def test_no_clipping() -> None:
    texts = [
        SvgText(
            x=50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="Safe",
            fill="#000000",
        ),
    ]
    issues = check_text_clipping(texts, width=800, height=500)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# check_tight_spacing
# ---------------------------------------------------------------------------


def test_tight_spacing_detected() -> None:
    # Place two texts vertically so their bboxes are close but don't overlap.
    # First text at y=50, bbox top ≈ 38, bottom ≈ 50 + 0.2*12 = 52.4
    # Second text at y=55, bbox top ≈ 43, bottom ≈ 55 + 0.2*12 = 57.4
    # These overlap, so adjust: put second at y=67 → top ≈ 55, which is
    # 55 - 52.4 = 2.6px gap (< 3px)
    texts = [
        SvgText(
            x=100, y=50, font_size=12, text_anchor="start", content="A", fill="#000000"
        ),
        SvgText(
            x=100, y=67, font_size=12, text_anchor="start", content="B", fill="#000000"
        ),
    ]
    issues = check_tight_spacing(texts, min_gap=3.0)
    assert len(issues) >= 1
    assert issues[0].check == "tight_spacing"
    assert issues[0].severity == "warning"


def test_no_tight_spacing() -> None:
    texts = [
        SvgText(
            x=10, y=20, font_size=10, text_anchor="start", content="A", fill="#000000"
        ),
        SvgText(
            x=400, y=300, font_size=10, text_anchor="start", content="B", fill="#000000"
        ),
    ]
    issues = check_tight_spacing(texts, min_gap=3.0)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# check_contrast
# ---------------------------------------------------------------------------


def test_contrast_failure() -> None:
    # Light gray text on white background → poor contrast
    texts = [
        SvgText(
            x=50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="Faint",
            fill="#CCCCCC",
        ),
    ]
    issues = check_contrast(texts, bg_color="#FFFFFF")
    assert len(issues) == 1
    assert issues[0].check == "contrast"
    assert issues[0].severity == "error"


def test_contrast_pass() -> None:
    # Dark text on white background → good contrast
    texts = [
        SvgText(
            x=50,
            y=50,
            font_size=12,
            text_anchor="start",
            content="Visible",
            fill="#333333",
        ),
    ]
    issues = check_contrast(texts, bg_color="#FFFFFF")
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# check_min_font_size
# ---------------------------------------------------------------------------


def test_min_font_size() -> None:
    texts = [
        SvgText(
            x=50, y=50, font_size=6, text_anchor="start", content="Tiny", fill="#000000"
        ),
    ]
    issues = check_min_font_size(texts, min_size=8.0)
    assert len(issues) == 1
    assert issues[0].check == "min_font_size"
    assert issues[0].severity == "warning"


def test_font_size_ok() -> None:
    texts = [
        SvgText(
            x=50,
            y=50,
            font_size=10,
            text_anchor="start",
            content="Normal",
            fill="#000000",
        ),
    ]
    issues = check_min_font_size(texts, min_size=8.0)
    assert len(issues) == 0


# ---------------------------------------------------------------------------
# critique_svg (full integration)
# ---------------------------------------------------------------------------


def test_full_critique_on_clean_svg(tmp_path: Path) -> None:
    """A well-formed SVG with properly spaced, high-contrast text → 0 issues."""
    body = (
        '<text x="100" y="30" font-size="16" text-anchor="middle" '
        'fill="#333333">Title</text>\n'
        '  <text x="100" y="180" font-size="12" text-anchor="middle" '
        'fill="#333333">X label</text>'
    )
    path = _write_svg(tmp_path, body)
    issues = critique_svg(path)
    assert len(issues) == 0


def test_critique_tags_file_path(tmp_path: Path) -> None:
    """Issues produced by critique_svg carry the file path."""
    body = (
        '<text x="50" y="50" font-size="6" text-anchor="start" '
        'fill="#333333">Small</text>'
    )
    path = _write_svg(tmp_path, body)
    issues = critique_svg(path)
    assert len(issues) >= 1
    assert all(i.file == str(path) for i in issues)


# ---------------------------------------------------------------------------
# parse_svg_canvas
# ---------------------------------------------------------------------------


def test_parse_svg_canvas(tmp_path: Path) -> None:
    path = _write_svg(tmp_path, "", width=800, height=500)
    w, h, bg = parse_svg_canvas(path)
    assert w == 800.0
    assert h == 500.0
    assert bg == "#FFFFFF"


def test_parse_svg_canvas_colored_bg(tmp_path: Path) -> None:
    svg = textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg"
             width="400" height="300" viewBox="0 0 400 300">
          <rect x="0" y="0" width="400" height="300" fill="#1A1A2E"/>
        </svg>
    """)
    path = tmp_path / "dark.svg"
    path.write_text(svg)
    w, h, bg = parse_svg_canvas(path)
    assert w == 400.0
    assert h == 300.0
    assert bg == "#1A1A2E"


# ---------------------------------------------------------------------------
# CLI --json output
# ---------------------------------------------------------------------------


def test_cli_json_output(tmp_path: Path) -> None:
    body = (
        '<text x="100" y="30" font-size="16" text-anchor="middle" '
        'fill="#333333">Title</text>'
    )
    path = _write_svg(tmp_path, body)

    result = subprocess.run(
        [
            sys.executable,
            str(_PROJECT_ROOT / "scripts" / "figure_critic.py"),
            "--json",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert "files_checked" in data
    assert "issues" in data
    assert "summary" in data
    assert data["files_checked"] == 1
