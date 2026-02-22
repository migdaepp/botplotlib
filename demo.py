"""botplotlib — flashy demo.

Run:  uv run python demo.py
Then open the generated SVGs in your browser.
"""

import math
import random

import botplotlib as bpl
from botplotlib.refactor.from_matplotlib import from_matplotlib

random.seed(42)

# ---------------------------------------------------------------------------
# 1. Scatter: "Fuel Efficiency by Vehicle Weight"
# ---------------------------------------------------------------------------
n = 80
weights = [2.0 + random.gauss(0, 0.6) for _ in range(n)]
mpg = [45 - 8 * w + random.gauss(0, 2.5) for w in weights]
origins = random.choices(["USA", "Europe", "Japan"], weights=[4, 3, 3], k=n)

fig_scatter = bpl.scatter(
    {"weight": weights, "mpg": mpg, "origin": origins},
    x="weight",
    y="mpg",
    color="origin",
    title="Fuel Efficiency by Vehicle Weight",
    x_label="Weight (1000 lbs)",
    y_label="Miles per Gallon",
)
fig_scatter.save_svg("demo_scatter.svg")
print("  wrote demo_scatter.svg")

# ---------------------------------------------------------------------------
# 2. Line: "Monthly Revenue by Product Line"
# ---------------------------------------------------------------------------
months = list(range(1, 13)) * 3
products = ["SaaS"] * 12 + ["Hardware"] * 12 + ["Services"] * 12
base = {"SaaS": 120, "Hardware": 80, "Services": 50}
revenue = []
for p, m in zip(products, months):
    trend = base[p] + m * (8 if p == "SaaS" else 3 if p == "Hardware" else 5)
    revenue.append(round(trend + random.gauss(0, 6), 1))

fig_line = bpl.line(
    {"month": months, "revenue": revenue, "product": products},
    x="month",
    y="revenue",
    color="product",
    title="Monthly Revenue by Product Line",
    x_label="Month",
    y_label="Revenue ($K)",
)
fig_line.save_svg("demo_line.svg")
print("  wrote demo_line.svg")

# ---------------------------------------------------------------------------
# 3. Bar: "Programming Language Popularity"
# ---------------------------------------------------------------------------
fig_bar = bpl.bar(
    {
        "language": [
            "Python", "JavaScript", "TypeScript", "Rust", "Go", "Java",
        ],
        "score": [92, 78, 71, 54, 48, 45],
    },
    x="language",
    y="score",
    title="Programming Language Popularity (2026)",
    x_label="Language",
    y_label="Popularity Score",
)
fig_bar.save_svg("demo_bar.svg")
print("  wrote demo_bar.svg")

# ---------------------------------------------------------------------------
# 4. Theme showcase — same data, four themes
# ---------------------------------------------------------------------------
sine_x = [i / 10 for i in range(0, 63)]
data_wave = {
    "x": sine_x * 2,
    "y": [math.sin(x) for x in sine_x] + [math.cos(x) for x in sine_x],
    "fn": ["sin(x)"] * len(sine_x) + ["cos(x)"] * len(sine_x),
}

for theme_name in ("default", "bluesky", "substack", "print"):
    fig = bpl.line(
        data_wave,
        x="x",
        y="y",
        color="fn",
        theme=theme_name,
        title=f"Theme: {theme_name}",
        x_label="x",
        y_label="f(x)",
    )
    fname = f"demo_theme_{theme_name}.svg"
    fig.save_svg(fname)
    print(f"  wrote {fname}")

# ---------------------------------------------------------------------------
# 5. Matplotlib auto-refactor demo
# ---------------------------------------------------------------------------
MPL_SCRIPT = '''
import matplotlib.pyplot as plt
import numpy as np

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

plt.figure(figsize=(8, 5))
plt.scatter(x, y)
plt.title("x squared")
plt.xlabel("x")
plt.ylabel("x^2")
plt.savefig("old_plot.png")
'''

spec = from_matplotlib(MPL_SCRIPT)
fig_refactor = bpl.render(spec)
fig_refactor.save_svg("demo_refactored.svg")
print("  wrote demo_refactored.svg  (auto-converted from matplotlib!)")

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
print("\nAll demos generated! Open the SVG files in your browser.")
