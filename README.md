<p align="center">
  <img src="docs/docs/images/the-future-is-cyborg-source.png" alt="the future is cyborg" width="500">
</p>

# botplotlib

**Deadly serious plotting tools.** *Also sandwiches.*

A conversation in the open-source plotting world made us wonder: what does a project look like when it's built *by* human-AI teams, *for* human-AI teams — from the ground up? Not just the code, but the governance, the quality gates, the social contract?

We didn't have an answer, so we started building one. It turned out to be a plotting library with a Bayesian reputation system and a Donna Haraway citation. We named it after a sandwich.

```python
import botplotlib as bpl
```

## What it does

- **One line, one plot** — `bpl.scatter(data, x="a", y="b")` and you're done
- **Beautiful by default** — five themes (Bluesky, PDF, print, magazine, default), all designed so the first render is the final render
- **Accessible by construction** — WCAG contrast is a compiler error, not a warning
- **Token-efficient** — 1 line instead of 15. Fewer tokens, fewer places to go wrong
- **Declarative spec** — PlotSpec is JSON — any agent can generate it, any human can read it
- **Matplotlib-free** — hand-rolled SVG renderer (~230 lines), no heavy C dependencies
- **Matplotlib bridge** — translate your old recipes — sometimes the translation is surprisingly short

## Quick example

```python
import botplotlib as bpl

data = {
    "weight": [2.5, 3.0, 3.5, 4.0, 4.5],
    "mpg": [30, 28, 25, 22, 20],
    "origin": ["US", "EU", "EU", "US", "JP"],
}
fig = bpl.scatter(data, x="weight", y="mpg", color="origin",
                  title="Fuel Efficiency by Weight")
fig.save_svg("plot.svg")
```

One function call. Colors are WCAG-compliant out of the box.

## Cyborg Social Contract

Humans and AIs contribute under the same rules.

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Social trust is emergent** — reputation through contribution quality, not biological status
5. **Provenance is transparent but not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

For the full architecture overview, design principles, and module map, see [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md).

## Platform Presets

| Theme | Alias | Personality |
|-------|-------|-------------|
| `default` | — | General purpose, colorful palette |
| `bluesky` | `social` | Scroll-stopping titles, fat dots for mobile thumbs |
| `pdf` | `arxiv` | Academic restraint — the kind of plot that footnotes itself |
| `print` | — | For the journal that believes in grayscale |
| `magazine` | `economist` | Warm parchment, serif authority |

These themes are chosen to seed the project around open platforms and open science. X/Twitter is not included; we invest in platforms aligned with open access and open discourse. But botplotlib is fully open-source, so contributors are welcome to add themes for other platforms.

## Installation

botplotlib is not yet on PyPI — install directly from GitHub:

```bash
pip install git+https://github.com/migdaepp/botplotlib.git
```

For PNG export support:

```bash
pip install "botplotlib[png] @ git+https://github.com/migdaepp/botplotlib.git"
```

## Documentation

Documentation is not yet hosted — to browse it locally:

```bash
cd docs && uv run --group docs mkdocs serve
# → http://127.0.0.1:8000/botplotlib/
```

## Tutorial

The interactive tutorial is a [marimo](https://marimo.io) notebook:

```bash
pip install marimo
marimo edit docs/tutorial.py
```

It walks through scatter/line/bar charts, data formats, all themes, the PlotSpec data model, and the matplotlib refactor — with live, editable plots.

Additional examples live in [`examples/`](examples/).

## Governance

Trust in botplotlib is progressive and origin-agnostic. See [GOVERNANCE.md](GOVERNANCE.md) for the full system: contributor tiers, promotion rubrics, reputation signals, and anti-gaming mechanisms. This is wildly over-engineered for our current contributor count. That's the point.

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — public domain. Because copyright requires an author, and we're not interested in drawing that line. Bots especially welcome.
