"""Lightweight, dependency-free SVG element builder.

Builds an in-memory tree of SVG elements and serialises it to a string.
No external libraries are required — just the Python standard library.
"""

from __future__ import annotations

from typing import Optional


# ---------------------------------------------------------------------------
# XML-safety helpers
# ---------------------------------------------------------------------------

def _escape_attr(value: str) -> str:
    """Escape a string for use inside an XML attribute value (double-quoted)."""
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _escape_text(value: str) -> str:
    """Escape a string for use as XML text content."""
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _to_kebab(name: str) -> str:
    """Convert a Python snake_case attribute name to SVG kebab-case.

    Leading underscores are preserved so that ``_data_foo`` becomes
    ``_data-foo`` (useful for custom/data attributes).  Interior underscores
    are replaced with hyphens.
    """
    # Count and strip leading underscores
    stripped = name.lstrip("_")
    prefix = name[: len(name) - len(stripped)]  # leading underscores
    return prefix + stripped.replace("_", "-")


# ---------------------------------------------------------------------------
# Core element
# ---------------------------------------------------------------------------

class SvgElement:
    """A single SVG/XML element with attributes, children, and optional text."""

    def __init__(self, tag: str, **attrs: object) -> None:
        self.tag = tag
        self.attrs: dict[str, str] = {
            _to_kebab(k): _format_attr_value(v) for k, v in attrs.items()
        }
        self.children: list[SvgElement] = []
        self.text: Optional[str] = None

    # -- tree manipulation ---------------------------------------------------

    def add(self, child: SvgElement) -> SvgElement:
        """Append *child* and return it (for convenient chaining)."""
        self.children.append(child)
        return child

    # -- serialisation -------------------------------------------------------

    def to_string(self, indent: int = 0) -> str:
        """Render the element (and its subtree) as an indented XML string."""
        pad = "  " * indent
        parts: list[str] = []

        # Opening tag
        attr_str = _render_attrs(self.attrs)
        if self.children or self.text is not None:
            parts.append(f"{pad}<{self.tag}{attr_str}>")
        else:
            # Self-closing tag
            parts.append(f"{pad}<{self.tag}{attr_str}/>")
            return "\n".join(parts)

        # Text content (inline, no extra newline)
        if self.text is not None and not self.children:
            parts[-1] += _escape_text(self.text)
            parts[-1] += f"</{self.tag}>"
            return "\n".join(parts)

        # Text content before children
        if self.text is not None:
            parts.append(f"{pad}  {_escape_text(self.text)}")

        # Children
        for child in self.children:
            parts.append(child.to_string(indent + 1))

        # Closing tag
        parts.append(f"{pad}</{self.tag}>")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# SVG document (root <svg> element)
# ---------------------------------------------------------------------------

class SvgDocument(SvgElement):
    """Root ``<svg>`` element with convenience helpers for defs & clip paths."""

    _XMLNS = "http://www.w3.org/2000/svg"

    def __init__(self, width: float, height: float, **attrs: object) -> None:
        super().__init__(
            "svg",
            xmlns=self._XMLNS,
            width=width,
            height=height,
            viewBox=f"0 0 {width} {height}",
            **attrs,
        )
        self._defs: Optional[SvgElement] = None

    # -- defs section --------------------------------------------------------

    def defs(self) -> SvgElement:
        """Return the ``<defs>`` child, creating it on first access."""
        if self._defs is None:
            self._defs = SvgElement("defs")
            # Insert defs as the first child so definitions precede usage.
            self.children.insert(0, self._defs)
        return self._defs

    # -- clip paths ----------------------------------------------------------

    def add_clip_rect(
        self,
        clip_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        """Add a ``<clipPath>`` containing a ``<rect>`` to ``<defs>``."""
        clip = SvgElement("clipPath", id=clip_id)
        clip.add(rect(x, y, width, height))
        self.defs().add(clip)

    # -- serialisation -------------------------------------------------------

    def to_string(self, indent: int = 0) -> str:
        """Render complete SVG including the XML declaration."""
        declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        body = super().to_string(indent)
        return f"{declaration}\n{body}"


# ---------------------------------------------------------------------------
# Private formatting helpers
# ---------------------------------------------------------------------------

def _format_attr_value(value: object) -> str:
    """Coerce an attribute value to its string representation."""
    if isinstance(value, float):
        # Strip unnecessary trailing zeros for cleaner output.
        return f"{value:g}"
    return str(value)


def _render_attrs(attrs: dict[str, str]) -> str:
    """Build the attribute string for an opening tag."""
    if not attrs:
        return ""
    pieces = [f' {k}="{_escape_attr(v)}"' for k, v in attrs.items()]
    return "".join(pieces)


# ---------------------------------------------------------------------------
# Convenience factory functions
# ---------------------------------------------------------------------------

def rect(
    x: float, y: float, width: float, height: float, **attrs: object
) -> SvgElement:
    """Create a ``<rect>`` element."""
    return SvgElement("rect", x=x, y=y, width=width, height=height, **attrs)


def circle(cx: float, cy: float, r: float, **attrs: object) -> SvgElement:
    """Create a ``<circle>`` element."""
    return SvgElement("circle", cx=cx, cy=cy, r=r, **attrs)


def line(
    x1: float, y1: float, x2: float, y2: float, **attrs: object
) -> SvgElement:
    """Create a ``<line>`` element."""
    return SvgElement("line", x1=x1, y1=y1, x2=x2, y2=y2, **attrs)


def text(content: str, x: float, y: float, **attrs: object) -> SvgElement:
    """Create a ``<text>`` element with text content."""
    el = SvgElement("text", x=x, y=y, **attrs)
    el.text = content
    return el


def group(**attrs: object) -> SvgElement:
    """Create a ``<g>`` (group) element."""
    return SvgElement("g", **attrs)


def path(d: str, **attrs: object) -> SvgElement:
    """Create a ``<path>`` element."""
    return SvgElement("path", d=d, **attrs)


def polyline(
    points: list[tuple[float, float]], **attrs: object
) -> SvgElement:
    """Create a ``<polyline>`` element.

    *points* is a list of ``(x, y)`` tuples.
    """
    pts_str = " ".join(f"{x:g},{y:g}" for x, y in points)
    return SvgElement("polyline", points=pts_str, **attrs)
