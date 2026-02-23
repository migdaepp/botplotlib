"""botplotlib — magazine theme demo.

Demonstrates the magazine/editorial theme with left-aligned title,
subtitle, y-axis label above the plot, and footnotes in the footer.

Run:  uv run python examples/demo_magazine.py
Then open the generated SVGs in your browser.
"""

import random
from pathlib import Path

import botplotlib as bpl

OUT = Path(__file__).parent
random.seed(42)

# ---------------------------------------------------------------------------
# Bar chart: magazine-style categorical data
# ---------------------------------------------------------------------------
fig_bar = bpl.bar(
    {
        "country": ["China", "United States", "India", "Germany", "Japan", "UK"],
        "gdp": [17.96, 25.46, 3.73, 4.26, 4.23, 3.07],
    },
    x="country",
    y="gdp",
    title="The world's largest economies",
    subtitle="GDP in 2023, trillions of dollars",
    x_label="",
    y_label="$, trillions",
    footnote="Source: World Bank",
    theme="magazine",
    width=600,
    height=420,
)
fig_bar.save_svg(OUT / "demo_magazine_bar.svg")
print("  wrote demo_magazine_bar.svg")

# ---------------------------------------------------------------------------
# Scatter plot: magazine-style with groups
# ---------------------------------------------------------------------------
n = 60
life_exp = [70 + random.gauss(0, 5) for _ in range(n)]
gdp_pc = [20 + le * 0.5 + random.gauss(0, 3) for le in life_exp]
regions = random.choices(["Europe", "Asia", "Americas"], weights=[3, 4, 3], k=n)

fig_scatter = bpl.scatter(
    {"life_expectancy": life_exp, "gdp_per_capita": gdp_pc, "region": regions},
    x="life_expectancy",
    y="gdp_per_capita",
    color="region",
    title="Health and wealth",
    subtitle="Life expectancy vs GDP per capita, by region",
    x_label="Life expectancy (years)",
    y_label="GDP per capita ($000s)",
    footnote="Source: World Development Indicators",
    theme="magazine",
    width=650,
    height=480,
    legend_position="top",
)
fig_scatter.save_svg(OUT / "demo_magazine_scatter.svg")
print("  wrote demo_magazine_scatter.svg")

print("\nMagazine theme demos generated! Open the SVG files in your browser.")
