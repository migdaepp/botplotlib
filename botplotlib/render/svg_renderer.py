"""SVG renderer: CompiledPlot → SVG string.

Converts the positioned geometry from the compiler into SVG elements
using the svg_builder module.  Plot content is rendered via a unified
primitives pipeline: each compiled geometry object is dispatched by
type through ``_render_primitive()``, which keeps the renderer open to
new geom types without requiring per-type iteration loops.

Rendering z-order (back to front):
    CompiledBar  → behind everything
    CompiledPath → above bars, below lines
    CompiledLine → above paths
    CompiledPoint → on top
"""

from __future__ import annotations

from botplotlib.geoms.primitives import (
    CompiledBar,
    CompiledLine,
    CompiledPath,
    CompiledPlot,
    CompiledPoint,
    Primitive,
    z_order_key,
)
from botplotlib.render.svg_builder import (
    SvgDocument,
    SvgElement,
    circle,
    group,
    line,
    path,
    polyline,
    rect,
    text,
)

# ---------------------------------------------------------------------------
# Primitive dispatch
# ---------------------------------------------------------------------------


def _render_primitive(prim: Primitive) -> SvgElement | None:
    """Render a single primitive to an SVG element.

    Returns ``None`` for primitives that should be skipped (e.g. a line
    with fewer than 2 points).
    """
    if isinstance(prim, CompiledBar):
        return rect(
            prim.px,
            prim.py,
            prim.bar_width,
            prim.bar_height,
            fill=prim.color,
        )

    if isinstance(prim, CompiledPath):
        attrs: dict[str, object] = {"fill": prim.fill, "stroke": prim.stroke}
        if prim.stroke != "none":
            attrs["stroke_width"] = prim.stroke_width
        if prim.opacity < 1.0:
            attrs["opacity"] = prim.opacity
        return path(prim.d, **attrs)

    if isinstance(prim, CompiledLine):
        if len(prim.points) < 2:
            return None
        return polyline(
            prim.points,
            fill="none",
            stroke=prim.color,
            stroke_width=prim.width,
            stroke_linejoin="round",
            stroke_linecap="round",
        )

    if isinstance(prim, CompiledPoint):
        return circle(
            prim.px,
            prim.py,
            prim.radius,
            fill=prim.color,
        )

    return None  # pragma: no cover – unknown primitive type


# ---------------------------------------------------------------------------
# Unified primitives list builder
# ---------------------------------------------------------------------------


def _collect_primitives(compiled: CompiledPlot) -> list[Primitive]:
    """Build a z-ordered primitives list from the compiled geometry.

    Reads from ``compiled.primitives`` (populated by the geom plugin
    compiler) and sorts by z-order so that bars render behind lines,
    which render behind points.  Python's ``sorted()`` is stable, so
    the relative order within each type is preserved.
    """
    if compiled.primitives:
        return sorted(compiled.primitives, key=z_order_key)

    # Fall back to legacy typed lists (backward compat)
    primitives: list[Primitive] = []
    primitives.extend(compiled.bars)
    primitives.extend(compiled.lines)
    primitives.extend(compiled.points)
    return sorted(primitives, key=z_order_key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_svg(compiled: CompiledPlot) -> str:
    """Render a CompiledPlot to an SVG string."""
    theme = compiled.theme
    doc = SvgDocument(compiled.width, compiled.height)

    # Clip path for the plot area
    pa = compiled.plot_area
    doc.add_clip_rect(compiled.clip_id, pa.x, pa.y, pa.width, pa.height)

    # Background
    doc.add(rect(0, 0, compiled.width, compiled.height, fill=theme.background_color))

    # Grid lines
    _render_grid(doc, compiled)

    # Axes
    _render_axes(doc, compiled)

    # Clipped plot content — unified primitives pipeline
    plot_group = group(clip_path=f"url(#{compiled.clip_id})")

    for prim in _collect_primitives(compiled):
        element = _render_primitive(prim)
        if element is not None:
            plot_group.add(element)

    doc.add(plot_group)

    # Tick labels
    _render_ticks(doc, compiled)

    # Text labels (title, axis labels)
    for txt in compiled.texts:
        attrs: dict[str, object] = {
            "font_family": theme.font_family,
            "font_size": txt.font_size,
            "fill": txt.color,
            "text_anchor": txt.anchor,
        }
        if txt.rotation != 0:
            attrs["transform"] = f"rotate({txt.rotation},{txt.x},{txt.y})"
        doc.add(text(txt.text, txt.x, txt.y, **attrs))

    # Legend
    if compiled.legend_entries and compiled.legend_area:
        _render_legend(doc, compiled)

    return doc.to_string()


# ---------------------------------------------------------------------------
# Structural elements (grid, axes, ticks, legend)
# ---------------------------------------------------------------------------


def _render_grid(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render grid lines."""
    theme = compiled.theme
    pa = compiled.plot_area

    if theme.show_y_grid:
        for tick in compiled.y_ticks:
            if pa.y <= tick.pixel_pos <= pa.bottom:
                doc.add(
                    line(
                        pa.x,
                        tick.pixel_pos,
                        pa.right,
                        tick.pixel_pos,
                        stroke=theme.grid_color,
                        stroke_width=1,
                    )
                )

    if theme.show_x_grid:
        for tick in compiled.x_ticks:
            if pa.x <= tick.pixel_pos <= pa.right:
                doc.add(
                    line(
                        tick.pixel_pos,
                        pa.y,
                        tick.pixel_pos,
                        pa.bottom,
                        stroke=theme.grid_color,
                        stroke_width=1,
                    )
                )


def _render_axes(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render axis lines."""
    theme = compiled.theme
    pa = compiled.plot_area

    if theme.show_x_axis:
        doc.add(
            line(
                pa.x,
                pa.bottom,
                pa.right,
                pa.bottom,
                stroke=theme.axis_color,
                stroke_width=theme.axis_stroke_width,
            )
        )

    if theme.show_y_axis:
        doc.add(
            line(
                pa.x,
                pa.y,
                pa.x,
                pa.bottom,
                stroke=theme.axis_color,
                stroke_width=theme.axis_stroke_width,
            )
        )


def _render_ticks(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render tick marks and labels."""
    theme = compiled.theme
    pa = compiled.plot_area

    for tick in compiled.x_ticks:
        # Tick mark
        doc.add(
            line(
                tick.pixel_pos,
                pa.bottom,
                tick.pixel_pos,
                pa.bottom + 5,
                stroke=theme.axis_color,
                stroke_width=theme.axis_stroke_width,
            )
        )
        # Label
        doc.add(
            text(
                tick.label,
                tick.pixel_pos,
                pa.bottom + 18,
                font_family=theme.font_family,
                font_size=theme.tick_font_size,
                fill=theme.text_color,
                text_anchor="middle",
            )
        )

    for tick in compiled.y_ticks:
        if pa.y <= tick.pixel_pos <= pa.bottom:
            # Tick mark
            doc.add(
                line(
                    pa.x - 5,
                    tick.pixel_pos,
                    pa.x,
                    tick.pixel_pos,
                    stroke=theme.axis_color,
                    stroke_width=theme.axis_stroke_width,
                )
            )
            # Label
            doc.add(
                text(
                    tick.label,
                    pa.x - 8,
                    tick.pixel_pos + 4,
                    font_family=theme.font_family,
                    font_size=theme.tick_font_size,
                    fill=theme.text_color,
                    text_anchor="end",
                )
            )


def _render_legend(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render the legend."""
    theme = compiled.theme
    la = compiled.legend_area
    if la is None:
        return

    y_offset = la.y + 10
    for entry in compiled.legend_entries:
        # Color swatch
        doc.add(rect(la.x, y_offset - 8, 12, 12, fill=entry.color, rx=2))
        # Label
        doc.add(
            text(
                entry.label,
                la.x + 18,
                y_offset + 2,
                font_family=theme.font_family,
                font_size=theme.tick_font_size,
                fill=theme.text_color,
                text_anchor="start",
            )
        )
        y_offset += 22
