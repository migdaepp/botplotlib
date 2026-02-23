# botplotlib

**Beautiful plots, simple API, no matplotlib.**

botplotlib is an AI-native Python plotting library that produces publication-quality SVG and PNG output with zero configuration. The API is flat and simple — designed so both humans and LLMs generate correct code on the first try.

---

## Why botplotlib?

Matplotlib was designed for humans writing code at keyboards. botplotlib is designed for the way people actually make plots now: you describe what you want, your AI partner writes the code, and you iterate on it together until the result looks good.

That cyborg workflow needs an API that's more often correct on the first try. It should be beautiful by default, accessible by construction, and token-efficient by design.

<div class="grid cards" markdown>

-   :material-lightning-bolt:{ .lg .middle } **One line, one plot**

    ---

    `bpl.scatter(data, x="a", y="b", theme="bluesky")` — no figure/axes juggling, no style boilerplate.

-   :material-palette:{ .lg .middle } **Beautiful by default**

    ---

    Platform-specific themes (Bluesky, PDF, print, magazine) produce publication-ready output with zero configuration.

-   :material-check-circle:{ .lg .middle } **Accessible by construction**

    ---

    WCAG contrast validation is a compiler-level gate, not a warning — the system won't produce an inaccessible plot.

-   :material-code-braces:{ .lg .middle } **Token-efficient**

    ---

    A matplotlib scatter plot with decent styling is 15-25 lines; botplotlib is 1. Fewer tokens = fewer places an LLM can go wrong.

-   :material-file-code:{ .lg .middle } **Declarative spec**

    ---

    PlotSpec is a JSON-serializable Pydantic model that any LLM can generate, any human can inspect, and any agent can modify.

-   :material-swap-horizontal:{ .lg .middle } **Matplotlib bridge**

    ---

    The refactor module translates existing matplotlib scripts into clean PlotSpecs — see what your old code *means*.

</div>

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

One function call. Beautiful output. WCAG-compliant colors. No configuration needed.

## What's next?

- [**Getting Started**](getting-started.md) — install and make your first plot
- [**Plot Types**](guide/plot-types.md) — scatter, line, bar, and waterfall charts
- [**Themes**](guide/themes.md) — platform-optimized visual presets
- [**Gallery**](gallery/index.md) — visual examples with code
- [**API Reference**](api/index.md) — full public API documentation
