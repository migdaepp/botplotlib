"""SVG renderer: CompiledPlot → SVG string.

Converts the positioned geometry from the compiler into SVG elements
using the svg_builder module.
"""

from __future__ import annotations

from botplotlib.compiler.compiler import CompiledPlot
from botplotlib.render.svg_builder import (
    SvgDocument,
    circle,
    group,
    line,
    polyline,
    rect,
    text,
)


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

    # Clipped plot content
    plot_group = group(clip_path=f"url(#{compiled.clip_id})")

    # Bars (behind points/lines)
    for bar in compiled.bars:
        plot_group.add(rect(
            bar.px, bar.py, bar.bar_width, bar.bar_height,
            fill=bar.color,
        ))

    # Lines
    for ln in compiled.lines:
        if len(ln.points) >= 2:
            plot_group.add(polyline(
                ln.points,
                fill="none",
                stroke=ln.color,
                stroke_width=ln.width,
                stroke_linejoin="round",
                stroke_linecap="round",
            ))

    # Points (on top)
    for pt in compiled.points:
        plot_group.add(circle(
            pt.px, pt.py, pt.radius,
            fill=pt.color,
        ))

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
            attrs["transform"] = (
                f"rotate({txt.rotation},{txt.x},{txt.y})"
            )
        doc.add(text(txt.text, txt.x, txt.y, **attrs))

    # Legend
    if compiled.legend_entries and compiled.legend_area:
        _render_legend(doc, compiled)

    return doc.to_string()


def _render_grid(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render grid lines."""
    theme = compiled.theme
    pa = compiled.plot_area

    if theme.show_y_grid:
        for tick in compiled.y_ticks:
            if pa.y <= tick.pixel_pos <= pa.bottom:
                doc.add(line(
                    pa.x, tick.pixel_pos, pa.right, tick.pixel_pos,
                    stroke=theme.grid_color,
                    stroke_width=1,
                ))

    if theme.show_x_grid:
        for tick in compiled.x_ticks:
            if pa.x <= tick.pixel_pos <= pa.right:
                doc.add(line(
                    tick.pixel_pos, pa.y, tick.pixel_pos, pa.bottom,
                    stroke=theme.grid_color,
                    stroke_width=1,
                ))


def _render_axes(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render axis lines."""
    theme = compiled.theme
    pa = compiled.plot_area

    if theme.show_x_axis:
        doc.add(line(
            pa.x, pa.bottom, pa.right, pa.bottom,
            stroke=theme.axis_color,
            stroke_width=theme.axis_stroke_width,
        ))

    if theme.show_y_axis:
        doc.add(line(
            pa.x, pa.y, pa.x, pa.bottom,
            stroke=theme.axis_color,
            stroke_width=theme.axis_stroke_width,
        ))


def _render_ticks(doc: SvgDocument, compiled: CompiledPlot) -> None:
    """Render tick marks and labels."""
    theme = compiled.theme
    pa = compiled.plot_area

    for tick in compiled.x_ticks:
        # Tick mark
        doc.add(line(
            tick.pixel_pos, pa.bottom,
            tick.pixel_pos, pa.bottom + 5,
            stroke=theme.axis_color,
            stroke_width=theme.axis_stroke_width,
        ))
        # Label
        doc.add(text(
            tick.label, tick.pixel_pos, pa.bottom + 18,
            font_family=theme.font_family,
            font_size=theme.tick_font_size,
            fill=theme.text_color,
            text_anchor="middle",
        ))

    for tick in compiled.y_ticks:
        if pa.y <= tick.pixel_pos <= pa.bottom:
            # Tick mark
            doc.add(line(
                pa.x - 5, tick.pixel_pos,
                pa.x, tick.pixel_pos,
                stroke=theme.axis_color,
                stroke_width=theme.axis_stroke_width,
            ))
            # Label
            doc.add(text(
                tick.label, pa.x - 8, tick.pixel_pos + 4,
                font_family=theme.font_family,
                font_size=theme.tick_font_size,
                fill=theme.text_color,
                text_anchor="end",
            ))


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
        doc.add(text(
            entry.label, la.x + 18, y_offset + 2,
            font_family=theme.font_family,
            font_size=theme.tick_font_size,
            fill=theme.text_color,
            text_anchor="start",
        ))
        y_offset += 22
