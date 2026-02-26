# botplotlib

<p align="center">
  <img src="images/the-future-is-cyborg-source.png" alt="the future is cyborg-source" width="500">
</p>

Matplotlib fed the scientific Python community for two decades and then AI showed up and tried to eat its lunch. botplotlib is us trying to build new community norms that work for everyone. We don't know what open-source looks like when collaborators are AI but we are figuring it out together.

---

## Install

```bash
pip install git+https://github.com/migdaepp/botplotlib.git
```

For PNG export support (requires Cairo):

```bash
pip install "botplotlib[png] @ git+https://github.com/migdaepp/botplotlib.git"
```

## Quick example

```python
import botplotlib as bpl

data = {
    "layer": ["bottom bun", "lettuce", "bot", "tomato", "top bun"],
    "size": [1, 1, 1, 1, 1],
}
fig = bpl.bar(
    data, x="layer", y="size", color="layer",
    color_map={"bottom bun": "#C4883A", "lettuce": "#4CAF50",
               "bot": "#4E79A7", "tomato": "#E53935",
               "top bun": "#C4883A"},
)
fig.save_svg("plot.svg")
```

![a BLT](assets/examples/blt_analysis.svg)

Colors are WCAG-compliant out of the box because [accountability lives in systems](https://estsjournal.org/index.php/ests/article/view/260).     

## Themes

| Theme | Alias | Personality |
|-------|-------|-------------|
| `default` | — | general purpose, colorful, fine, whatever |
| `bluesky` | `social` | scroll-stopping titles, fat dots for mobile thumbs |
| `pdf` | `arxiv` | academic and restrained, everyone will think u r v smart |
| `print` | — | sometimes you weirdly still need grayscale |
| `magazine` | `economist` | we all know which magazine it is we're just not gonna say it |

See the [Guide](guide.md#themes) for details.

## Tutorial

The interactive tutorial is a [marimo](https://marimo.io) notebook, because marimo is also ai-native and we think they are cool.

```bash
pip install marimo
marimo edit docs/tutorial.py
```

## What's next?

- [**Guide**](guide.md) — themes, plot types, data formats, JSON path, refactoring
- [**API Reference**](api/index.md) — full public API documentation
- [**Contributing**](contributing.md) — how to add to the project
