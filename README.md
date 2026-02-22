# botplotlib

**Beautiful plots, simple API, no matplotlib.**

botplotlib is an AI-native Python plotting library that produces publication-quality SVG and PNG output with zero configuration. The API is flat and simple — designed so both humans and LLMs generate correct code on the first try.

## Why botplotlib?

The February 2026 Matplotlib agent incident showed what happens when AI tools struggle with complex, stateful APIs: confusing output, wasted tokens, frustrated users. botplotlib takes a different approach:

- **AI-native API**: one function call per plot, no figure/axes juggling
- **Beautiful by default**: clean, modern theme with WCAG-compliant colors
- **Matplotlib-free**: renders directly to SVG with zero heavy dependencies
- **A cyborg open-source project**: proving that human+AI collaboration can build something genuinely excellent

This project embodies Donna Haraway's cyborg framework — we reject the human/machine binary. Every contribution is a cyborg contribution.

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

## Auto-Refactor from Matplotlib

Paste your matplotlib spaghetti, get a clean spec back:

```python
from botplotlib.refactor import from_matplotlib

spec = from_matplotlib("my_old_script.py")
fig = bpl.render(spec)
fig.save_svg("migrated.svg")
```

## Platform Presets

botplotlib ships with themes optimized for different output targets:

| Theme | Use case |
|-------|----------|
| `default` | Screen / notebook |
| `bluesky` | Social media (larger type, 4:3 aspect) |
| `substack` | Email / web articles |
| `print` | Publication-quality, serif-friendly |

## Contributing

See [AGENTS.md](AGENTS.md) for the contributor guide, architecture overview, and the Cyborg Social Contract.

## License

MIT
