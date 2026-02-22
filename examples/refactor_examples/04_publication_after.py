"""botplotlib version: theme='pdf' handles all publication styling."""

import botplotlib as bpl

data = {
    "year": [
        1970,
        1975,
        1980,
        1985,
        1990,
        1995,
        2000,
        2005,
        2010,
        2015,
        2020,
    ],
    "anomaly": [
        0.08,
        0.12,
        0.18,
        0.25,
        0.32,
        0.40,
        0.52,
        0.65,
        0.78,
        0.90,
        1.02,
    ],
}

fig = bpl.line(
    data,
    x="year",
    y="anomaly",
    title="Global Temperature Anomaly",
    theme="pdf",
)
fig.save_svg("temperature.svg")
