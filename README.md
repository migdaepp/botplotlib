# botplotlib

**Beautiful plots, simple API, no matplotlib.**

botplotlib is an AI-native Python plotting library that produces publication-quality SVG and PNG output with zero configuration. The API is flat and simple — designed so both humans and LLMs generate correct code on the first try.

## Why botplotlib?

Matplotlib was designed for humans writing code at keyboards. botplotlib is designed for the way people actually make plots now: you describe what you want, your AI partner writes the code, and you evaluate the result.

That cyborg workflow needs a different API: one that's correct on the first try, beautiful by default, accessible by construction, and token-efficient by design.

- **One line, one plot**: `bpl.scatter(data, x="a", y="b", theme="bluesky")` — no figure/axes juggling, no style boilerplate
- **Beautiful by default**: platform-specific themes (Bluesky, Substack, PDF, print) produce publication-ready output with zero configuration
- **Accessible by construction**: WCAG contrast validation is a compiler-level gate, not a warning — the system won't produce an inaccessible plot
- **Token-efficient**: a matplotlib scatter plot with decent styling is 15–25 lines; botplotlib is 1. Fewer tokens means fewer places an LLM can go wrong
- **Declarative spec**: the PlotSpec is a JSON-serializable Pydantic model that any LLM can generate, any human can inspect, and any agent can modify
- **Matplotlib-free**: hand-rolled SVG renderer (~230 lines), no heavy C dependencies
- **Matplotlib bridge**: the refactor module translates existing matplotlib scripts into clean PlotSpecs — see what your old code *means* in a form both humans and machines can reason about

This project embodies Donna Haraway's cyborg framework: we reject the human/machine binary. The matplotlib maintainers rejected AI contributions. We built a library that makes AI contributions the point.

## Installation

```bash
pip install botplotlib
```

For PNG export support:

```bash
pip install botplotlib[png]
```

## Quick Start

```python
import botplotlib as bpl

# Scatter plot from a dict
data = {
    "weight": [2.5, 3.0, 3.5, 4.0, 4.5],
    "mpg": [30, 28, 25, 22, 20],
    "origin": ["US", "EU", "EU", "US", "JP"],
}
fig = bpl.scatter(data, x="weight", y="mpg", color="origin",
                  title="Fuel Efficiency by Weight")
fig.save_svg("plot.svg")
```

```python
# Line plot — just as simple
fig = bpl.line({"x": [1, 2, 3, 4], "y": [10, 20, 15, 25]}, x="x", y="y")
fig.save_svg("trend.svg")
```

```python
# Platform preset for social media
fig = bpl.scatter(data, x="weight", y="mpg", theme="bluesky",
                  title="Check out this data")
fig.save_svg("social_post.svg")
```

## Waterfall Charts

```python
fig = bpl.waterfall(
    {
        "category": ["Revenue", "COGS", "Gross Profit", "OpEx", "Tax", "Net Income"],
        "amount": [500, -200, 300, -150, -45, 105],
    },
    x="category", y="amount",
    title="Income Statement Waterfall",
)
fig.save_svg("waterfall.svg")
```

## Agent JSON Path

LLMs can generate plots directly from JSON — no Python code execution required:

```python
fig = bpl.Figure.from_dict({
    "data": {"columns": {"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]}},
    "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
    "labels": {"title": "Perfect Squares"},
    "theme": "bluesky",
})
fig.save_svg("from_agent.svg")
```

Also available: `Figure.from_json(json_string)` for raw JSON input.

## Auto-Refactor from Matplotlib

Paste your matplotlib spaghetti, get a clean spec back:

```python
from botplotlib.refactor import from_matplotlib

spec = from_matplotlib("my_old_script.py")
fig = bpl.render(spec)
fig.save_svg("migrated.svg")
```

Or generate the equivalent botplotlib Python code:

```python
from botplotlib.refactor import to_botplotlib_code

print(to_botplotlib_code("my_old_script.py"))
```

## Platform Presets

botplotlib ships with themes optimized for different output targets:

| Theme | Use case |
|-------|----------|
| `default` | Screen / notebook |
| `bluesky` | Social media (larger type, bolder strokes) |
| `substack` | Email / web articles |
| `pdf` | Digital academic papers — arxiv, SSRN (serif, muted colors) |
| `print` | Physical print / B&W journals (grayscale, serif) |

These are the starting integrations — chosen to seed the project around open platforms and open science. X/Twitter is not included; we invest in platforms aligned with open access and open discourse. botplotlib is open-source, so contributors are welcome to add themes for other platforms.

## Documentation

Full documentation: [migdaepp.github.io/botplotlib](https://migdaepp.github.io/botplotlib/)

## Tutorial

The interactive tutorial is a [marimo](https://marimo.io) notebook:

```bash
pip install marimo
marimo edit docs/tutorial.py
```

It walks through scatter/line/bar charts, data formats, all five themes, the PlotSpec data model, and the matplotlib refactor — with live, editable plots.

Additional examples live in [`examples/`](examples/).

## Contributing

See [AGENTS.md](AGENTS.md) for the contributor guide, architecture overview, and the Cyborg Social Contract.

## License

MIT
