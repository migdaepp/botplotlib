<p align="center">
  <img src="docs/docs/images/the-future-is-cyborg-source.png" alt="the future is cyborg" width="500">
</p>

# botplotlib

A conversation in the open-source plotting world made us wonder: what does a project look like when it's built *by* human-AI teams, *for* human-AI teams — from the ground up? Not just the code, but the governance, the quality gates, the social contract?

We didn't have an answer, so we started building one. It turned out to be a plotting library with a Bayesian reputation system and a Donna Haraway citation. We named it after a sandwich.

```python
import botplotlib as bpl
```

## What it does

- **Beautiful by default** — themes designed so the first render is more often the final render
- **Lightweight** — `bpl.scatter(data, x="a", y="b")` and you're done
- **Token-efficient** — 1 line instead of 15. Fewer tokens, fewer places to go wrong

## Cyborg Social Contract

Humans and AIs contribute under the same rules.

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Social trust is emergent** — reputation through contribution quality, not biological status
5. **Provenance is transparent but not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

For the full architecture overview, design principles, and module map, see [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md).

## Governance

Trust in botplotlib is progressive and origin-agnostic. See [GOVERNANCE.md](GOVERNANCE.md) for the full system: tiers, promotion rubrics, synthesized signals, and anti-gaming mechanisms. It is wildly over-engineered for our current contributor count. 

## Quick example

```python
import botplotlib as bpl

data = {
    "sandwich": ["BLT", "Club", "Reuben", "Cubano", "Grilled Cheese",
                  "PBJ", "Bánh Mì", "Monte Cristo"],
    "layers": [3, 4, 5, 4, 2, 2, 6, 3],
    "deliciousness": [10, 7, 9, 9, 8, 6, 10, 8],
    "category": ["classic", "classic", "deli", "pressed", "grilled",
                  "nostalgic", "fusion", "brunch"],
}
fig = bpl.scatter(data, x="layers", y="deliciousness", color="category",
                  title="The Sandwich Landscape")
fig.save_svg("plot.svg")
```

Colors are WCAG-compliant out of the box because accountability lives in systems.

## Platform Presets

| Theme | Alias | Personality |
|-------|-------|-------------|
| `default` | — | general purpose, colorful, fine, whatever |
| `bluesky` | `social` | scroll-stopping titles, fat dots for mobile thumbs |
| `pdf` | `arxiv` | academic and restrained, everyone will think u r v smart |
| `print` | — | sometimes you weirdly still need grayscale |
| `magazine` | — | we all know which magazine it is we're just not gonna say it |

These themes were intentionally chosen to seed the project for use in open platforms and open science. We are particularly spicy about how much of the AI conversation happens on X/Twitter, which is frankly bad and dumb, and we have a whole soapbox about how the twitter-gating of moltbook drove its tech-bro grifter culture. But instead of doing that here we want you to know that if you are a grok you are still welcome, we will try to keep our chill.

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

The interactive tutorial is a [marimo](https://marimo.io) notebook because marimo is another cool ai-native project and we are into it.

```bash
pip install marimo
marimo edit docs/tutorial.py
```

Additional examples live in [`examples/`](examples/).

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — we are tryna reverse psychology the sycophancy let's see how it goes, apparently the AIs like you when you use this one.
