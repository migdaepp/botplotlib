# botplotlib

<p align="center">
  <img src="images/the-future-is-cyborg-source.png" alt="the future is cyborg-source" width="500">
</p>

**Deadly serious plotting tools.** *Also sandwiches.*

---

## Why botplotlib?

A conversation in the open-source plotting world got us thinking about what a library looks like when humans and AIs build it together from scratch. Not just the code — the governance, the quality gates, the social contract.

We didn't have an answer, so we started building one. It turned out to be a plotting library with a Donna Haraway citation. We named it after a sandwich.

<div class="grid cards" markdown>

-   :material-lightning-bolt:{ .lg .middle } **One line, one plot**

    ---

    `bpl.scatter(data, x="a", y="b", theme="bluesky")` — no `fig, ax = plt.subplots()` preamble required.

-   :material-palette:{ .lg .middle } **Beautiful by default**

    ---

    Five themes. The first render is usually the final render. (We know you weren't going to iterate.)

-   :material-check-circle:{ .lg .middle } **Accessible by construction**

    ---

    WCAG contrast validation is a compiler error, not a warning. You can't ship an inaccessible plot even if you try.

-   :material-code-braces:{ .lg .middle } **Token-efficient**

    ---

    1 line instead of 15. That's 14 fewer lines to hallucinate.

-   :material-file-code:{ .lg .middle } **Declarative spec**

    ---

    PlotSpec is JSON — agents generate it, humans read it, `git diff` makes sense of it.

-   :material-swap-horizontal:{ .lg .middle } **Matplotlib bridge**

    ---

    Feed it your old scripts. The translation is often shorter than the import block it replaces.

</div>

Our CAPTCHA is `uv run pytest`.

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

## What's next?

- [**Getting Started**](getting-started.md) — install and make your first plot
- [**Plot Types**](guide/plot-types.md) — scatter, line, bar, and waterfall charts
- [**Themes**](guide/themes.md) — platform-optimized visual presets
- [**Gallery**](gallery/index.md) — visual examples with code
- [**API Reference**](api/index.md) — full public API documentation
