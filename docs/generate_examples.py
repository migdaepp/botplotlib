"""Generate example SVG images for the documentation site."""

import math
import random
from pathlib import Path

import botplotlib as blt
from botplotlib.refactor import from_matplotlib

OUT = Path(__file__).parent / "docs" / "assets" / "examples"
OUT.mkdir(parents=True, exist_ok=True)

random.seed(42)

# ── Getting Started ──────────────────────────────────────────────────────

# Basic scatter
blt.scatter(
    {"x": [1, 2, 3, 4, 5], "y": [2, 4, 3, 7, 5]},
    x="x",
    y="y",
    title="Five Points",
).save_svg(OUT / "gs_basic_scatter.svg")

# Grouped scatter
blt.scatter(
    {
        "weight": [2.5, 3.0, 3.5, 4.0, 4.5],
        "mpg": [30, 28, 25, 22, 20],
        "origin": ["US", "EU", "EU", "US", "JP"],
    },
    x="weight",
    y="mpg",
    color="origin",
    title="Fuel Efficiency by Weight",
    x_label="Weight (1000 lbs)",
    y_label="Miles per Gallon",
).save_svg(OUT / "gs_grouped_scatter.svg")

# ── Plot Types ───────────────────────────────────────────────────────────

# Scatter
n = 80
weights = [2.0 + random.gauss(0, 0.6) for _ in range(n)]
mpg = [45 - 8 * w + random.gauss(0, 2.5) for w in weights]
origins = random.choices(["USA", "Europe", "Japan"], weights=[4, 3, 3], k=n)

blt.scatter(
    {"weight": weights, "mpg": mpg, "origin": origins},
    x="weight",
    y="mpg",
    color="origin",
    title="Fuel Efficiency by Vehicle Weight",
    x_label="Weight (1000 lbs)",
    y_label="Miles per Gallon",
).save_svg(OUT / "pt_scatter.svg")

# Line
months = list(range(1, 13))
blt.line(
    {
        "month": months * 2,
        "revenue": [
            10,
            13,
            15,
            14,
            18,
            22,
            25,
            28,
            26,
            30,
            35,
            40,
            20,
            19,
            21,
            22,
            23,
            22,
            24,
            25,
            26,
            25,
            27,
            28,
        ],
        "segment": ["SaaS"] * 12 + ["Hardware"] * 12,
    },
    x="month",
    y="revenue",
    color="segment",
    title="Revenue by Segment",
    x_label="Month",
    y_label="Revenue ($M)",
).save_svg(OUT / "pt_line.svg")

# Bar
blt.bar(
    {
        "language": ["Python", "JavaScript", "TypeScript", "Rust", "Go", "Java"],
        "score": [92, 78, 71, 54, 48, 45],
    },
    x="language",
    y="score",
    title="Programming Language Popularity",
    x_label="Language",
    y_label="Popularity Score",
).save_svg(OUT / "pt_bar.svg")

# Waterfall
blt.waterfall(
    {
        "category": ["Revenue", "COGS", "Gross Profit", "OpEx", "Tax", "Net Income"],
        "amount": [500, -200, 300, -150, -45, 105],
    },
    x="category",
    y="amount",
    title="Income Statement Waterfall",
    x_label="",
    y_label="Amount ($K)",
).save_svg(OUT / "pt_waterfall.svg")

# Layered
fig_layered = (
    blt.plot(
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
fig_layered.save_svg(OUT / "pt_layered.svg")

# ── Themes ───────────────────────────────────────────────────────────────

xs = [i * 0.1 for i in range(63)]
wave_data = {
    "x": xs * 2,
    "y": [math.sin(v) for v in xs] + [math.cos(v) for v in xs],
    "fn": ["sin(x)"] * 63 + ["cos(x)"] * 63,
}

for theme_name in ("default", "bluesky", "pdf", "print", "magazine"):
    blt.line(
        wave_data,
        x="x",
        y="y",
        color="fn",
        title=f"{theme_name.title()} Theme",
        theme=theme_name,
    ).save_svg(OUT / f"theme_{theme_name}.svg")

# ── JSON Path ────────────────────────────────────────────────────────────

blt.Figure.from_dict(
    {
        "data": {"columns": {"x": [1, 2, 3, 4, 5], "y": [1, 4, 9, 16, 25]}},
        "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
        "labels": {"title": "Perfect Squares", "x": "n", "y": "n squared"},
        "theme": "default",
    }
).save_svg(OUT / "json_from_dict.svg")

blt.Figure.from_dict(
    {
        "data": {
            "columns": {
                "year": [2020, 2021, 2022, 2023, 2024],
                "revenue": [4.2, 3.8, 5.1, 6.3, 8.2],
            }
        },
        "layers": [{"geom": "line", "x": "year", "y": "revenue"}],
        "labels": {"title": "Revenue Growth"},
        "theme": "magazine",
    }
).save_svg(OUT / "json_from_dict_line.svg")

spec = blt.PlotSpec.model_validate(
    {
        "data": {"columns": {"x": [1, 2, 3], "y": [1, 4, 9]}},
        "layers": [{"geom": "line", "x": "x", "y": "y"}],
        "labels": {"title": "Squares"},
        "theme": "bluesky",
    }
)
blt.render(spec).save_svg(OUT / "json_render.svg")

# ── Refactoring ──────────────────────────────────────────────────────────

mpl_code = """\
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 4, 7, 11, 16]

plt.scatter(x, y)
plt.title("Growth Over Time")
plt.xlabel("Year")
plt.ylabel("Value")
plt.show()
"""

spec = from_matplotlib(mpl_code)
blt.render(spec).save_svg(OUT / "refactor_scatter.svg")

mpl_code2 = """\
import matplotlib.pyplot as plt

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

plt.figure(figsize=(8, 5))
plt.scatter(x, y)
plt.title("x squared")
plt.xlabel("x")
plt.ylabel("x^2")
plt.savefig("old_plot.png")
"""

spec2 = from_matplotlib(mpl_code2)
blt.render(spec2).save_svg(OUT / "refactor_squared.svg")

# ── Gallery: theme showcase (Nathan's Hot Dog Eating Contest) ────────────

years = list(range(2011, 2026))
gallery_data = {
    "year": years * 2,
    "hot_dogs": [
        62,
        68,
        69,
        61,
        62,
        70,
        72,
        74,
        71,
        75,
        76,
        63,
        62,
        58,
        70,
        40,
        45,
        37,
        34,
        38,
        38,
        41,
        37,
        31,
        48,
        31,
        40,
        40,
        51,
        33,
    ],
    "division": ["men"] * 15 + ["women"] * 15,
}

for theme_name in ("default", "bluesky", "pdf", "print", "magazine"):
    blt.line(
        gallery_data,
        x="year",
        y="hot_dogs",
        color="division",
        title="Nathan's Hot Dog Eating Contest",
        x_label="Year",
        y_label="Hot Dogs Eaten",
        theme=theme_name,
    ).save_svg(OUT / f"gallery_{theme_name}.svg")

# Gallery: bar charts with labels (Joey Chestnut's climb to 76)
bar_data = {
    "year": ["2007", "2009", "2013", "2016", "2017", "2018", "2020", "2021"],
    "hot_dogs": [66, 68, 69, 70, 72, 74, 75, 76],
}

for theme_name in ("default", "magazine"):
    blt.bar(
        bar_data,
        x="year",
        y="hot_dogs",
        title="Joey Chestnut: The Climb to 76",
        y_label="Hot Dogs in 10 Min",
        labels=True,
        theme=theme_name,
    ).save_svg(OUT / f"gallery_bar_{theme_name}.svg")

print(f"Generated {len(list(OUT.glob('*.svg')))} SVGs in {OUT}")
