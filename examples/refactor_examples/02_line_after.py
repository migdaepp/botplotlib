"""botplotlib version: clean spines and grid are the default."""

import botplotlib as blt

data = {
    "year": [2019, 2020, 2021, 2022, 2023, 2024],
    "revenue": [85, 100, 120, 115, 140, 160],
}

fig = blt.line(data, x="year", y="revenue", title="Annual Revenue Growth")
fig.save_svg("revenue.svg")
