import marimo

__generated_with = "0.20.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # botplotlib

    **Beautiful plots. Simple API. No matplotlib.**

    A Python library that produces publication-ready plots with a simple,
    declarative API. Designed for humans *and* coding agents
    (Claude Code, Codex, Antigravity) alike.
    """)
    return


@app.cell
def _():
    import botplotlib as bpl

    return (bpl,)


@app.cell(hide_code=True)
def _():
    import random

    random.seed(42)
    _n = 80
    _weights = [2.0 + random.gauss(0, 0.6) for _ in range(_n)]
    _mpg = [45 - 8 * w + random.gauss(0, 2.5) for w in _weights]
    _origins = random.choices(["USA", "Europe", "Japan"], weights=[4, 3, 3], k=_n)
    gallery_scatter = {
        "weight": _weights,
        "mpg": _mpg,
        "origin": _origins,
    }
    _months = list(range(1, 13)) * 3
    _products = ["SaaS"] * 12 + ["Hardware"] * 12 + ["Services"] * 12
    _base = {"SaaS": 120, "Hardware": 80, "Services": 50}
    _revenue = []
    for _p, _m in zip(_products, _months):
        _trend = _base[_p] + _m * (8 if _p == "SaaS" else 3 if _p == "Hardware" else 5)
        _revenue.append(round(_trend + random.gauss(0, 6), 1))
    gallery_line = {
        "month": _months,
        "revenue": _revenue,
        "product": _products,
    }
    return gallery_line, gallery_scatter, random


@app.cell
def _(bpl, gallery_line, gallery_scatter, mo):
    _fig_s = bpl.scatter(
        gallery_scatter,
        x="weight",
        y="mpg",
        color="origin",
        title="Fuel Efficiency",
        x_label="Weight (1000 lbs)",
        y_label="MPG",
        width=350,
        height=250,
    )
    _fig_l = bpl.line(
        gallery_line,
        x="month",
        y="revenue",
        color="product",
        title="Revenue Trend",
        x_label="Month",
        y_label="Revenue ($K)",
        width=350,
        height=250,
    )
    _fig_b = bpl.bar(
        {
            "language": [
                "Python",
                "JS",
                "TypeScript",
                "Rust",
                "Go",
                "Java",
            ],
            "score": [92, 78, 71, 54, 48, 45],
        },
        x="language",
        y="score",
        title="Popularity",
        x_label="Language",
        y_label="Score",
        width=350,
        height=250,
    )
    mo.hstack(
        [
            mo.Html(_fig_s.to_svg()),
            mo.Html(_fig_l.to_svg()),
            mo.Html(_fig_b.to_svg()),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Your First Plot in One Line

    botplotlib takes a dict of columns and produces a beautiful plot.
    No figure setup, no axis configuration, no style tweaking.
    """)
    return


@app.cell
def _(bpl):
    bpl.scatter(
        {"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 7, 5]},
        x="x",
        y="y",
        title="Five Points",
        width=600,
        height=380,
    )
    return


@app.cell
def _(bpl, random):
    random.seed(42)
    _n = 27  # points per cluster
    scatter_data = {"x": [], "y": [], "group": []}
    for _name, _cx, _cy in [
        ("Cluster A", 2, 6),
        ("Cluster B", 6, 9),
        ("Cluster C", 9, 3),
    ]:
        for _ in range(_n):
            scatter_data["x"].append(round(random.gauss(_cx, 1.0), 1))
            scatter_data["y"].append(round(random.gauss(_cy, 1.0), 1))
            scatter_data["group"].append(_name)

    fig_scatter = bpl.scatter(
        scatter_data,
        x="x",
        y="y",
        color="group",
        title="Three Clusters",
        x_label="Feature 1",
        y_label="Feature 2",
        width=600,
        height=380,
    )
    fig_scatter
    return (fig_scatter,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Line and Bar Charts

    Same API, different geometries. `bpl.line()` and `bpl.bar()` use the
    same signature as `bpl.scatter()`.
    """)
    return


@app.cell
def _(bpl):
    _months = list(range(1, 13))
    revenue_data = {
        "month": _months * 3,
        "revenue": (
            [10, 13, 15, 14, 18, 22, 25, 28, 26, 30, 35, 40]  # SaaS
            + [20, 19, 21, 22, 23, 22, 24, 25, 26, 25, 27, 28]  # Hardware
            + [5, 6, 7, 8, 8, 10, 11, 13, 14, 16, 18, 20]  # Services
        ),
        "segment": ["SaaS"] * 12 + ["Hardware"] * 12 + ["Services"] * 12,
    }
    fig_line = bpl.line(
        revenue_data,
        x="month",
        y="revenue",
        color="segment",
        title="Revenue by Segment (2024)",
        x_label="Month",
        y_label="Revenue ($M)",
        width=600,
        height=380,
    )
    fig_line
    return


@app.cell
def _(bpl):
    fig_bar = bpl.bar(
        {
            "language": [
                "Python",
                "JavaScript",
                "TypeScript",
                "Rust",
                "Go",
                "Java",
            ],
            "popularity": [30, 25, 18, 10, 9, 8],
        },
        x="language",
        y="popularity",
        title="Programming Language Popularity",
        x_label="Language",
        y_label="Popularity (%)",
        width=600,
        height=380,
    )
    fig_bar
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data Format Flexibility

    botplotlib accepts data in multiple formats: `dict` of columns,
    `list[dict]` of records, Polars DataFrames, Pandas DataFrames, and
    Arrow tables. Use whatever your pipeline produces.
    """)
    return


@app.cell
def _(bpl):
    records = [
        {"language": "Python", "popularity": 30},
        {"language": "JavaScript", "popularity": 25},
        {"language": "TypeScript", "popularity": 18},
        {"language": "Rust", "popularity": 10},
        {"language": "Go", "popularity": 9},
        {"language": "Java", "popularity": 8},
    ]
    fig_records = bpl.bar(
        records,
        x="language",
        y="popularity",
        title="Same Data, Row-Oriented Format",
        x_label="Language",
        y_label="Popularity (%)",
        width=600,
        height=380,
    )
    fig_records
    return


@app.cell
def _(bpl):
    fig_layered = (
        bpl.plot(
            {
                "year": [2019, 2020, 2021, 2022, 2023, 2024],
                "actual": [4.2, 3.8, 5.1, 6.3, 7.0, 8.2],
                "forecast": [4.0, 4.5, 5.0, 5.5, 6.0, 6.5],
            }
        )
        .add_line(x="year", y="forecast")
        .add_scatter(x="year", y="actual")
    )
    fig_layered.title = "Actual vs Forecast Revenue ($B)"
    fig_layered
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Platform Themes

    Every theme produces publication-ready output with zero configuration.
    All palettes are WCAG AA compliant ($\geq$ 3 : 1 contrast ratio).

    | Theme | Use case | Style |
    |-------|----------|-------|
    | `default` | General purpose | Clean sans-serif, colorful palette |
    | `bluesky` | Social media posts | Larger text, bolder strokes |
    | `magazine` | Longform articles | Editorial serif, warm background |
    | `pdf` | Digital academic papers (arxiv, SSRN) | Serif, muted colors |
    | `print` | Physical print / B&W journals | Grayscale, serif fonts |
    """)
    return


@app.cell(hide_code=True)
def _():
    import math as _math

    _n = 63  # ~2pi / 0.1
    _xs = [i * 0.1 for i in range(_n)]
    wave_data = {
        "x": _xs + _xs,
        "y": [_math.sin(v) for v in _xs] + [_math.cos(v) for v in _xs],
        "series": ["sin(x)"] * _n + ["cos(x)"] * _n,
    }
    return (wave_data,)


@app.cell
def _(bpl, mo, wave_data):
    fig_default = bpl.line(
        wave_data,
        x="x",
        y="y",
        color="series",
        title="Default",
        width=400,
        height=280,
    )
    fig_bluesky = bpl.line(
        wave_data,
        x="x",
        y="y",
        color="series",
        title="Bluesky",
        theme="bluesky",
        width=400,
        height=280,
    )
    mo.hstack([mo.Html(fig_default.to_svg()), mo.Html(fig_bluesky.to_svg())])
    return


@app.cell
def _(bpl, mo, wave_data):
    fig_magazine = bpl.line(
        wave_data,
        x="x",
        y="y",
        color="series",
        title="Magazine",
        theme="magazine",
        width=400,
        height=280,
    )
    fig_pdf = bpl.line(
        wave_data,
        x="x",
        y="y",
        color="series",
        title="PDF (arxiv / SSRN)",
        theme="pdf",
        width=400,
        height=280,
    )
    mo.hstack([mo.Html(fig_magazine.to_svg()), mo.Html(fig_pdf.to_svg())])
    return


@app.cell
def _(bpl, mo, wave_data):
    fig_print = bpl.line(
        wave_data,
        x="x",
        y="y",
        color="series",
        title="Print (B&W)",
        theme="print",
        width=500,
        height=320,
    )
    mo.Html(fig_print.to_svg())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Accessibility by default.** The `print` theme uses a grayscale
    > palette with serif fonts for physical journals. The `pdf` theme
    > uses muted academic colors for on-screen papers. Every theme
    > enforces WCAG AA contrast ratios — this is a compiler error, not
    > a linter warning. You can't accidentally ship an inaccessible plot.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Under the Hood: PlotSpec

    Every botplotlib figure is backed by a `PlotSpec` — a Pydantic model
    that fully describes the plot as data. The pipeline is:

    **PlotSpec** (declarative proposal) &rarr; **Compiler** (deterministic
    executor) &rarr; **SVG**

    This separation is why botplotlib is agent-native: an LLM proposes a
    spec, the compiler handles pixels, fonts, and contrast ratios. No
    visual iteration needed.
    """)
    return


@app.cell
def _(fig_scatter, mo):
    _json = fig_scatter.spec.model_dump_json(indent=2)
    mo.md(f"```json\n{_json}\n```")
    return


@app.cell
def _(bpl):
    spec_from_dict = bpl.PlotSpec.model_validate(
        {
            "data": {
                "columns": {
                    "x": [1, 2, 3, 4, 5],
                    "y": [1, 4, 9, 16, 25],
                }
            },
            "layers": [{"geom": "line", "x": "x", "y": "y"}],
            "labels": {
                "title": "Perfect Squares",
                "x": "n",
                "y": "n\u00b2",
            },
            "theme": "bluesky",
        }
    )
    fig_roundtrip = bpl.render(spec_from_dict)
    fig_roundtrip
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Why this matters for agents.** PlotSpecs are JSON-serializable,
    > diffable, versionable, and transmittable between agents. An LLM
    > never needs to reason about pixel positions or font metrics — the
    > compiler handles all of that deterministically.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Matplotlib Refactor

    Got existing matplotlib code? botplotlib can convert it. The
    `from_matplotlib()` function parses matplotlib scripts via AST
    analysis and extracts an equivalent `PlotSpec` — no matplotlib
    installation required.
    """)
    return


@app.cell
def _(mo):
    import textwrap

    MPL_SCRIPT = textwrap.dedent("""\
        import matplotlib.pyplot as plt

        x = [1, 2, 3, 4, 5]
        y = [2, 4, 7, 11, 16]

        plt.scatter(x, y)
        plt.title("Growth Over Time")
        plt.xlabel("Year")
        plt.ylabel("Value")
        plt.show()
    """)
    mo.md(f"```python\n{MPL_SCRIPT}```")
    return (MPL_SCRIPT,)


@app.cell
def _(MPL_SCRIPT, bpl):
    from botplotlib.refactor.from_matplotlib import from_matplotlib

    spec_refactored = from_matplotlib(MPL_SCRIPT)
    fig_refactored = bpl.render(spec_refactored)
    fig_refactored
    return (spec_refactored,)


@app.cell
def _(mo, spec_refactored):
    _json = spec_refactored.model_dump_json(indent=2)
    mo.accordion({"Extracted PlotSpec (JSON)": mo.md(f"```json\n{_json}\n```")})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why botplotlib?

    matplotlib is 20 years old and 200,000 lines of code. It was built
    for humans tweaking knobs in a GUI. Today, most plots are generated
    by code — increasingly by AI agents that can't see what they produce.

    botplotlib is built for this world:

    - **Token-efficient**: fewer tokens = fewer failure points for LLMs
    - **Declarative**: propose a spec, let the compiler handle the pixels
    - **Accessible by default**: WCAG compliance is a structural gate,
      not a review step
    - **Beautiful out of the box**: publication-ready with zero
      configuration

    [GitHub](https://github.com/migdaepp/botplotlib) &middot;
    [Architecture Guide](AGENTS.md)
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
