# botplotlib

**Beautiful plots, simple API, AI-native.**

botplotlib is an AI-native Python plotting library that produces publication-quality SVG and PNG output with zero configuration. The API is flat and simple — designed so both humans and LLMs generate correct code on the first try.

## Why botplotlib?

Matplotlib was designed for humans writing code at keyboards. botplotlib is designed for the way people make plots now: you describe what you want, your AI partner writes the code, and you evaluate the result.

That cyborg workflow needs a different API. Figures should be beautiful by default, accessible by construction, and token-efficient by design.

- **One line, one plot**: `bpl.scatter(data, x="a", y="b", theme="bluesky")` — no figure/axes juggling, no style boilerplate
- **Beautiful by default**: platform-specific themes (social media, PDF, print, magazine) produce publication-ready output with zero configuration
- **Accessible by construction**: WCAG contrast validation is a compiler-level gate, not a warning — the system won't produce an inaccessible plot
- **Token-efficient**: a matplotlib scatter plot with decent styling is 15–25 lines; botplotlib is 1. Fewer tokens means fewer places an LLM can go wrong
- **Declarative spec**: the PlotSpec is a JSON-serializable Pydantic model that any LLM can generate, any human can inspect, and any agent can modify
- **Matplotlib-free**: hand-rolled SVG renderer (~230 lines), no heavy C dependencies
- **Matplotlib bridge**: the refactor module translates existing matplotlib scripts into clean PlotSpecs — see what your old code *means* in a form both humans and machines can reason about

This project embodies Donna Haraway's cyborg framework: we reject the human/machine binary.

## Contributing

botplotlib follows the Cyborg Social Contract — all contributions are cyborg contributions. We reject the human/machine binary.

For the full architecture overview, design principles, and module map, see [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md).

### Cyborg Social Contract

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Social trust is emergent** — reputation through contribution quality, not biological status
5. **Provenance is transparent but not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

## Installation

botplotlib is not yet on PyPI — install directly from GitHub:

```bash
pip install git+https://github.com/migdaepp/botplotlib.git
```

For PNG export support:

```bash
pip install "botplotlib[png] @ git+https://github.com/migdaepp/botplotlib.git"
```

## Platform Presets

botplotlib ships with themes optimized for different output targets:

| Theme | Use case |
|-------|----------|
| `default` | Screen / notebook |
| `bluesky` | Social media (bold titles, larger type, mobile-optimized) |
| `pdf` | Digital academic papers — arxiv, SSRN (serif, muted colors) |
| `print` | Physical print / B&W journals (grayscale, serif) |
| `magazine` | Editorial / data journalism (serif, warm background, left-aligned titles) |

These themes are chosen to seed the project around open platforms and open science. X/Twitter is not included; we intentionally started by investing in platforms aligned with open access and open discourse. But botplotlib is fully open-source, so contributors are welcome to add themes for other platforms.

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

Trust in botplotlib is progressive and origin-agnostic. See [GOVERNANCE.md](GOVERNANCE.md) for the full system: contributor tiers, promotion rubrics, reputation signals, and anti-gaming mechanisms.

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — public domain. Use it, fork it, build on it, no strings attached. Bots especially welcome.
