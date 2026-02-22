"""Tests for botplotlib.render.svg_builder."""

from __future__ import annotations

import xml.etree.ElementTree as ET

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
# SvgElement basics
# ---------------------------------------------------------------------------


class TestSvgElement:
    """Core SvgElement behaviour."""

    def test_renders_correct_tag(self) -> None:
        el = SvgElement("rect", x=0, y=0, width=10, height=10)
        output = el.to_string()
        assert output.startswith("<rect")
        assert output.endswith("/>")

    def test_self_closing_when_no_children_or_text(self) -> None:
        el = SvgElement("circle", cx=5, cy=5, r=3)
        assert el.to_string().endswith("/>")

    def test_snake_case_to_kebab_case(self) -> None:
        el = SvgElement("text", font_size=12, text_anchor="middle", fill_opacity=0.5)
        output = el.to_string()
        assert 'font-size="12"' in output
        assert 'text-anchor="middle"' in output
        assert 'fill-opacity="0.5"' in output
        # Original snake_case should NOT appear
        assert "font_size" not in output
        assert "text_anchor" not in output
        assert "fill_opacity" not in output

    def test_leading_underscore_preserved(self) -> None:
        el = SvgElement("rect", _data_value="hello")
        output = el.to_string()
        assert '_data-value="hello"' in output

    def test_nested_elements_with_indentation(self) -> None:
        parent = SvgElement("g")
        child = SvgElement("rect", x=0, y=0, width=10, height=10)
        parent.add(child)
        output = parent.to_string()
        lines = output.split("\n")
        assert len(lines) == 3  # <g>, indented <rect/>, </g>
        assert lines[0] == "<g>"
        assert lines[1].startswith("  ")  # two-space indent
        assert lines[2] == "</g>"

    def test_text_content_escaped(self) -> None:
        el = SvgElement("text", x=0, y=0)
        el.text = "A & B < C > D"
        output = el.to_string()
        assert "A &amp; B &lt; C &gt; D" in output

    def test_attribute_values_escaped(self) -> None:
        el = SvgElement("rect", title='say "hello" & <bye>')
        output = el.to_string()
        assert "say &quot;hello&quot; &amp; &lt;bye&gt;" in output

    def test_add_returns_child(self) -> None:
        parent = SvgElement("g")
        child = SvgElement("rect")
        returned = parent.add(child)
        assert returned is child


# ---------------------------------------------------------------------------
# SvgDocument
# ---------------------------------------------------------------------------


class TestSvgDocument:
    """SvgDocument (root <svg>) behaviour."""

    def test_includes_xmlns_and_viewbox(self) -> None:
        doc = SvgDocument(800, 600)
        output = doc.to_string()
        assert 'xmlns="http://www.w3.org/2000/svg"' in output
        assert 'viewBox="0 0 800 600"' in output

    def test_includes_xml_declaration(self) -> None:
        doc = SvgDocument(100, 100)
        output = doc.to_string()
        assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_width_and_height(self) -> None:
        doc = SvgDocument(640, 480)
        output = doc.to_string()
        assert 'width="640"' in output
        assert 'height="480"' in output

    def test_defs_created_on_first_access(self) -> None:
        doc = SvgDocument(100, 100)
        d = doc.defs()
        assert d.tag == "defs"
        # Calling again returns the same object
        assert doc.defs() is d

    def test_defs_appears_in_output(self) -> None:
        doc = SvgDocument(100, 100)
        doc.defs()  # force creation
        output = doc.to_string()
        assert "<defs" in output

    def test_add_clip_rect(self) -> None:
        doc = SvgDocument(200, 200)
        doc.add_clip_rect("clip0", 10, 20, 180, 160)
        output = doc.to_string()
        assert "<clipPath" in output
        assert 'id="clip0"' in output
        assert "<rect" in output

    def test_defs_is_first_child(self) -> None:
        doc = SvgDocument(100, 100)
        doc.add(SvgElement("rect"))
        doc.add_clip_rect("c1", 0, 0, 100, 100)
        assert doc.children[0].tag == "defs"


# ---------------------------------------------------------------------------
# Helper / factory functions
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    """Module-level convenience factory functions."""

    def test_rect(self) -> None:
        el = rect(10, 20, 100, 50, fill="red")
        assert el.tag == "rect"
        assert el.attrs["x"] == "10"
        assert el.attrs["y"] == "20"
        assert el.attrs["width"] == "100"
        assert el.attrs["height"] == "50"
        assert el.attrs["fill"] == "red"

    def test_circle(self) -> None:
        el = circle(50, 50, 25, stroke="blue")
        assert el.tag == "circle"
        assert el.attrs["cx"] == "50"
        assert el.attrs["cy"] == "50"
        assert el.attrs["r"] == "25"
        assert el.attrs["stroke"] == "blue"

    def test_line(self) -> None:
        el = line(0, 0, 100, 100, stroke="black", stroke_width=2)
        assert el.tag == "line"
        assert el.attrs["x1"] == "0"
        assert el.attrs["y1"] == "0"
        assert el.attrs["x2"] == "100"
        assert el.attrs["y2"] == "100"
        assert "stroke-width" in el.attrs

    def test_text(self) -> None:
        el = text("Hello", 10, 20, font_size=14)
        assert el.tag == "text"
        assert el.text == "Hello"
        assert "font-size" in el.attrs

    def test_group(self) -> None:
        el = group(transform="translate(10,20)")
        assert el.tag == "g"
        assert el.attrs["transform"] == "translate(10,20)"

    def test_path(self) -> None:
        el = path("M0 0 L10 10", fill="none", stroke="green")
        assert el.tag == "path"
        assert el.attrs["d"] == "M0 0 L10 10"

    def test_polyline(self) -> None:
        pts = [(0, 0), (10, 20), (30, 40.5)]
        el = polyline(pts, fill="none", stroke="red")
        assert el.tag == "polyline"
        assert el.attrs["points"] == "0,0 10,20 30,40.5"

    def test_polyline_renders_correctly(self) -> None:
        pts = [(1, 2), (3, 4)]
        el = polyline(pts)
        output = el.to_string()
        assert 'points="1,2 3,4"' in output


# ---------------------------------------------------------------------------
# Valid XML output
# ---------------------------------------------------------------------------


class TestValidXml:
    """Verify that generated SVG is well-formed XML."""

    def test_simple_document_parses(self) -> None:
        doc = SvgDocument(400, 300)
        doc.add(rect(0, 0, 400, 300, fill="#fff"))
        doc.add(circle(200, 150, 50, fill="blue"))
        output = doc.to_string()
        # Should not raise
        ET.fromstring(output)

    def test_document_with_text_parses(self) -> None:
        doc = SvgDocument(400, 300)
        doc.add(text("Hello & <World>", 10, 20))
        output = doc.to_string()
        ET.fromstring(output)

    def test_document_with_defs_parses(self) -> None:
        doc = SvgDocument(400, 300)
        doc.add_clip_rect("myClip", 0, 0, 400, 300)
        g = group(clip_path="url(#myClip)")
        g.add(rect(0, 0, 400, 300, fill="green"))
        doc.add(g)
        output = doc.to_string()
        ET.fromstring(output)

    def test_nested_groups_parse(self) -> None:
        doc = SvgDocument(200, 200)
        outer = group(id="outer")
        inner = group(id="inner")
        inner.add(rect(5, 5, 10, 10))
        outer.add(inner)
        doc.add(outer)
        output = doc.to_string()
        ET.fromstring(output)

    def test_polyline_in_document_parses(self) -> None:
        doc = SvgDocument(200, 200)
        doc.add(polyline([(0, 0), (50, 100), (100, 50)], fill="none", stroke="red"))
        output = doc.to_string()
        ET.fromstring(output)

    def test_complex_document_parses(self) -> None:
        """A more realistic document with multiple element types."""
        doc = SvgDocument(640, 480)
        doc.add_clip_rect("plot-area", 50, 30, 560, 400)

        # Background
        doc.add(rect(0, 0, 640, 480, fill="#f8f8f8"))

        # Plot group
        plot = group(clip_path="url(#plot-area)")
        plot.add(line(50, 430, 610, 430, stroke="#ccc", stroke_width=1))
        plot.add(path("M50 430 L100 380 L150 350 L200 300", fill="none", stroke="steelblue"))
        plot.add(circle(100, 380, 3, fill="steelblue"))
        doc.add(plot)

        # Labels
        doc.add(text("X Axis", 330, 470, text_anchor="middle", font_size=12))
        doc.add(text('Values & "Stuff"', 20, 240, text_anchor="middle", font_size=12))

        output = doc.to_string()
        root = ET.fromstring(output)
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
