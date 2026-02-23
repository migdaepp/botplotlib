#!/usr/bin/env python3
"""Figure critic — automated SVG quality review for botplotlib.

Parses SVG files and runs quality checks for text overlap, clipping,
tight spacing, contrast, and minimum font size.

Usage:
    uv run python scripts/figure_critic.py                          # all golden SVGs
    uv run python scripts/figure_critic.py examples/demo_bar.svg    # specific file(s)
    uv run python scripts/figure_critic.py --json                   # JSON output
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from botplotlib._colors.palettes import contrast_ratio
from botplotlib._fonts.metrics import text_bbox
from botplotlib._types import Rect
from botplotlib.compiler.accessibility import (
    LARGE_TEXT_THRESHOLD,
    WCAG_AA_LARGE_TEXT,
    WCAG_AA_NORMAL_TEXT,
)

# SVG namespace
_SVG_NS = "http://www.w3.org/2000/svg"

# Common named SVG colors → hex
_NAMED_COLORS: dict[str, str] = {
    "white": "#FFFFFF",
    "black": "#000000",
    "red": "#FF0000",
    "green": "#008000",
    "blue": "#0000FF",
    "gray": "#808080",
    "grey": "#808080",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SvgText:
    """A text element extracted from an SVG file."""

    x: float
    y: float  # SVG baseline y-coordinate
    font_size: float
    text_anchor: str  # "start", "middle", "end"
    content: str
    fill: str
    font_name: str = "arial"
    rotation: float | None = None
    rotation_cx: float | None = None
    rotation_cy: float | None = None


@dataclass
class Issue:
    """A quality issue found in an SVG file."""

    file: str
    check: str
    severity: str  # "error" or "warning"
    message: str
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_color(color: str) -> str:
    """Normalize a color string to uppercase hex format."""
    color = color.strip().lower()
    if color in _NAMED_COLORS:
        return _NAMED_COLORS[color]
    if not color.startswith("#"):
        color = f"#{color}"
    return color.upper()


def _parse_rotation(
    transform: str,
) -> tuple[float, float | None, float | None]:
    """Extract rotation angle and optional center from a transform attribute.

    Returns ``(angle, cx, cy)``.  *cx*/*cy* are ``None`` when the
    transform specifies only an angle (rotation about the origin).
    """
    match = re.search(
        r"rotate\(\s*([-\d.]+)" r"(?:\s*[,\s]\s*([-\d.]+)\s*[,\s]\s*([-\d.]+))?\s*\)",
        transform,
    )
    if not match:
        raise ValueError(f"No rotation found in transform: {transform!r}")
    angle = float(match.group(1))
    cx = float(match.group(2)) if match.group(2) else None
    cy = float(match.group(3)) if match.group(3) else None
    return angle, cx, cy


def _get_text_content(elem: ET.Element) -> str:
    """Get the full text content of an element, including child tspans."""
    parts: list[str] = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        if child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)
    return "".join(parts).strip()


def _detect_font(font_family: str) -> str:
    """Pick the best available metrics table for a CSS ``font-family``."""
    if font_family and "inter" in font_family.lower():
        return "inter"
    return "arial"


# ---------------------------------------------------------------------------
# SVG parsing
# ---------------------------------------------------------------------------


def parse_svg_texts(svg_path: str | Path) -> list[SvgText]:
    """Extract ``<text>`` elements from an SVG file."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    texts: list[SvgText] = []

    # Handle both namespaced and non-namespaced SVG
    for tag in (f"{{{_SVG_NS}}}text", "text"):
        for elem in root.iter(tag):
            content = _get_text_content(elem)
            if not content:
                continue

            x = float(elem.get("x", "0"))
            y = float(elem.get("y", "0"))
            font_size = float(elem.get("font-size", "12"))
            text_anchor = elem.get("text-anchor", "start")
            fill = elem.get("fill", "#000000")
            font_family = elem.get("font-family", "")
            transform = elem.get("transform", "")

            rotation = rotation_cx = rotation_cy = None
            if "rotate" in transform:
                rotation, rotation_cx, rotation_cy = _parse_rotation(transform)

            texts.append(
                SvgText(
                    x=x,
                    y=y,
                    font_size=font_size,
                    text_anchor=text_anchor,
                    content=content,
                    fill=_normalize_color(fill),
                    font_name=_detect_font(font_family),
                    rotation=rotation,
                    rotation_cx=rotation_cx,
                    rotation_cy=rotation_cy,
                )
            )

    return texts


def parse_svg_canvas(
    svg_path: str | Path,
) -> tuple[float, float, str]:
    """Extract canvas width, height, and background color from an SVG.

    Returns ``(width, height, bg_color_hex)``.
    """
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Dimensions from viewBox (preferred) or width/height attributes
    viewbox = root.get("viewBox")
    if viewbox:
        parts = viewbox.split()
        width = float(parts[2])
        height = float(parts[3])
    else:
        width = float(root.get("width", "800"))
        height = float(root.get("height", "500"))

    # Background color: first <rect> that covers the full canvas at (0, 0)
    bg_color = "#FFFFFF"
    for rect_tag in (f"{{{_SVG_NS}}}rect", "rect"):
        for elem in root.iter(rect_tag):
            rx = float(elem.get("x", "0"))
            ry = float(elem.get("y", "0"))
            rw = float(elem.get("width", "0"))
            rh = float(elem.get("height", "0"))
            if rx == 0 and ry == 0 and abs(rw - width) < 1 and abs(rh - height) < 1:
                fill = elem.get("fill", "")
                if fill:
                    bg_color = _normalize_color(fill)
                break

    return width, height, bg_color


# ---------------------------------------------------------------------------
# Bounding-box utilities
# ---------------------------------------------------------------------------


def _compute_bbox(t: SvgText) -> Rect:
    """Compute the axis-aligned bounding box for an :class:`SvgText`."""
    # SVG ``y`` is the baseline; approximate the top as y − font_size.
    top_y = t.y - t.font_size
    bbox = text_bbox(
        t.content,
        t.font_size,
        t.x,
        top_y,
        font_name=t.font_name,
        anchor=t.text_anchor,
    )

    if t.rotation is not None:
        cx = t.rotation_cx if t.rotation_cx is not None else t.x
        cy = t.rotation_cy if t.rotation_cy is not None else t.y
        angle_rad = math.radians(t.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        corners = [
            (bbox.x, bbox.y),
            (bbox.right, bbox.y),
            (bbox.x, bbox.bottom),
            (bbox.right, bbox.bottom),
        ]
        rotated = []
        for px, py in corners:
            dx, dy = px - cx, py - cy
            rx = cx + dx * cos_a - dy * sin_a
            ry = cy + dx * sin_a + dy * cos_a
            rotated.append((rx, ry))

        xs = [p[0] for p in rotated]
        ys = [p[1] for p in rotated]
        return Rect(
            x=min(xs),
            y=min(ys),
            width=max(xs) - min(xs),
            height=max(ys) - min(ys),
        )

    return bbox


def _rect_gap(a: Rect, b: Rect) -> float:
    """Minimum distance between two non-overlapping rects (0 if they overlap)."""
    if a.intersects(b):
        return 0.0
    dx = max(0.0, max(a.x - b.right, b.x - a.right))
    dy = max(0.0, max(a.y - b.bottom, b.y - a.bottom))
    if dx == 0:
        return dy
    if dy == 0:
        return dx
    return math.sqrt(dx * dx + dy * dy)


# ---------------------------------------------------------------------------
# Quality checks
# ---------------------------------------------------------------------------


def check_text_overlap(texts: list[SvgText]) -> list[Issue]:
    """Two ``<text>`` bounding boxes intersect."""
    issues: list[Issue] = []
    bboxes = [(t, _compute_bbox(t)) for t in texts]

    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            t_a, bbox_a = bboxes[i]
            t_b, bbox_b = bboxes[j]
            if bbox_a.intersects(bbox_b):
                issues.append(
                    Issue(
                        file="",
                        check="text_overlap",
                        severity="error",
                        message=(
                            f"Text {t_a.content!r} overlaps with " f"{t_b.content!r}"
                        ),
                        details={
                            "text_a": t_a.content,
                            "text_b": t_b.content,
                            "bbox_a": asdict(bbox_a),
                            "bbox_b": asdict(bbox_b),
                        },
                    )
                )
    return issues


def check_text_clipping(
    texts: list[SvgText], width: float, height: float
) -> list[Issue]:
    """Text bbox extends beyond canvas bounds."""
    issues: list[Issue] = []
    for t in texts:
        bbox = _compute_bbox(t)
        directions: list[str] = []
        if bbox.x < 0:
            directions.append("left")
        if bbox.y < 0:
            directions.append("top")
        if bbox.right > width:
            directions.append("right")
        if bbox.bottom > height:
            directions.append("bottom")
        if directions:
            issues.append(
                Issue(
                    file="",
                    check="text_clipping",
                    severity="error",
                    message=(
                        f"Text {t.content!r} extends beyond canvas "
                        f"({', '.join(directions)})"
                    ),
                    details={
                        "text": t.content,
                        "bbox": asdict(bbox),
                        "canvas": {"width": width, "height": height},
                        "directions": directions,
                    },
                )
            )
    return issues


def check_tight_spacing(texts: list[SvgText], min_gap: float = 3.0) -> list[Issue]:
    """Two text bboxes are within *min_gap* px but not overlapping."""
    issues: list[Issue] = []
    bboxes = [(t, _compute_bbox(t)) for t in texts]

    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            t_a, bbox_a = bboxes[i]
            t_b, bbox_b = bboxes[j]
            if bbox_a.intersects(bbox_b):
                continue  # handled by check_text_overlap
            gap = _rect_gap(bbox_a, bbox_b)
            if 0 < gap < min_gap:
                issues.append(
                    Issue(
                        file="",
                        check="tight_spacing",
                        severity="warning",
                        message=(
                            f"Text {t_a.content!r} is only {gap:.1f}px "
                            f"from {t_b.content!r}"
                        ),
                        details={
                            "text_a": t_a.content,
                            "text_b": t_b.content,
                            "gap_px": round(gap, 1),
                            "min_gap": min_gap,
                        },
                    )
                )
    return issues


def check_contrast(texts: list[SvgText], bg_color: str) -> list[Issue]:
    """Text color vs background fails WCAG AA threshold."""
    issues: list[Issue] = []
    if not bg_color or bg_color.upper() == "NONE":
        return issues

    for t in texts:
        if not t.fill or t.fill.upper() == "NONE":
            continue
        try:
            ratio = contrast_ratio(t.fill, bg_color)
        except (ValueError, KeyError):
            continue  # skip unparseable colors

        threshold = (
            WCAG_AA_LARGE_TEXT
            if t.font_size >= LARGE_TEXT_THRESHOLD
            else WCAG_AA_NORMAL_TEXT
        )
        if ratio < threshold:
            size_label = "large" if t.font_size >= LARGE_TEXT_THRESHOLD else "normal"
            issues.append(
                Issue(
                    file="",
                    check="contrast",
                    severity="error",
                    message=(
                        f"Text {t.content!r} ({t.fill} on {bg_color}) "
                        f"has contrast ratio {ratio:.2f}:1, below WCAG AA "
                        f"{size_label} text minimum of {threshold}:1"
                    ),
                    details={
                        "text": t.content,
                        "text_color": t.fill,
                        "bg_color": bg_color,
                        "ratio": round(ratio, 2),
                        "threshold": threshold,
                        "font_size": t.font_size,
                    },
                )
            )
    return issues


def check_min_font_size(texts: list[SvgText], min_size: float = 8.0) -> list[Issue]:
    """Any ``<text>`` with ``font-size`` below *min_size*."""
    issues: list[Issue] = []
    for t in texts:
        if t.font_size < min_size:
            issues.append(
                Issue(
                    file="",
                    check="min_font_size",
                    severity="warning",
                    message=(
                        f"Text {t.content!r} has font-size {t.font_size}px "
                        f"(minimum: {min_size}px)"
                    ),
                    details={
                        "text": t.content,
                        "font_size": t.font_size,
                        "min_size": min_size,
                    },
                )
            )
    return issues


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def critique_svg(svg_path: str | Path) -> list[Issue]:
    """Run all quality checks on a single SVG file."""
    svg_path = Path(svg_path)
    texts = parse_svg_texts(svg_path)
    width, height, bg_color = parse_svg_canvas(svg_path)

    issues: list[Issue] = []
    issues.extend(check_text_overlap(texts))
    issues.extend(check_text_clipping(texts, width, height))
    issues.extend(check_tight_spacing(texts))
    issues.extend(check_contrast(texts, bg_color))
    issues.extend(check_min_font_size(texts))

    # Tag every issue with the file path
    for issue in issues:
        issue.file = str(svg_path)

    return issues


def _collect_golden_svgs() -> list[Path]:
    """Collect all golden SVG files from examples/ and tests/baselines/."""
    project_root = Path(__file__).resolve().parent.parent
    svgs: list[Path] = []

    examples_dir = project_root / "examples"
    if examples_dir.exists():
        svgs.extend(sorted(examples_dir.glob("demo_*.svg")))

    baselines_dir = project_root / "tests" / "baselines"
    if baselines_dir.exists():
        svgs.extend(sorted(baselines_dir.glob("*.svg")))

    return svgs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Figure critic — automated SVG quality review",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="SVG files to check (default: all golden SVGs)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    args = parser.parse_args()

    if args.files:
        svg_files = [Path(f) for f in args.files]
    else:
        svg_files = _collect_golden_svgs()

    if not svg_files:
        print("No SVG files found.", file=sys.stderr)
        sys.exit(1)

    all_issues: list[Issue] = []
    for svg_file in svg_files:
        all_issues.extend(critique_svg(svg_file))

    errors = sum(1 for i in all_issues if i.severity == "error")
    warnings = sum(1 for i in all_issues if i.severity == "warning")

    if args.json_output:
        report = {
            "files_checked": len(svg_files),
            "issues": [asdict(i) for i in all_issues],
            "summary": {"errors": errors, "warnings": warnings},
        }
        json.dump(report, sys.stdout, indent=2)
        print()  # trailing newline
    else:
        print(f"Checked {len(svg_files)} SVG files\n")
        if not all_issues:
            print("No issues found.")
        else:
            for issue in all_issues:
                icon = "ERROR" if issue.severity == "error" else "WARN"
                print(f"  [{icon}] {issue.file}")
                print(f"         {issue.check}: {issue.message}")
                print()
            print(f"Summary: {errors} error(s), {warnings} warning(s)")

    sys.exit(1 if errors > 0 else 0)


if __name__ == "__main__":
    main()
