"""botplotlib version: data + one call."""

import botplotlib as bpl

data = {
    "lang": ["Python", "JavaScript", "Rust", "Go", "TypeScript"],
    "score": [92, 88, 45, 62, 78],
}

fig = bpl.bar(
    data,
    x="lang",
    y="score",
    title="Programming Language Popularity",
)
fig.save_svg("languages.svg")
