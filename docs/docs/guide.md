# Guide

## Themes

Same data, five themes. The data is real — [Nathan's Famous Hot Dog Eating Contest](https://en.wikipedia.org/wiki/Nathan%27s_Hot_Dog_Eating_Contest), Coney Island, every July 4th since 1916.

All theme palettes enforce WCAG AA contrast ratios (>= 3:1 against white). This is a compiler error, not a warning. You literally cannot ship inaccessible colors.

| Theme | Alias | Personality |
|-------|-------|-------------|
| `default` | — | general purpose, colorful, fine, whatever |
| `bluesky` | `social` | scroll-stopping titles, fat dots for mobile thumbs |
| `pdf` | `arxiv` | academic and restrained, everyone will think u r v smart |
| `print` | — | sometimes you weirdly still need grayscale |
| `magazine` | `economist` | we all know which magazine it is we're just not gonna say it |

```python
import botplotlib as bpl

years = list(range(2011, 2026))
data = {
    "year": years * 2,
    "hot_dogs": [62, 68, 69, 61, 62, 70, 72, 74, 71, 75, 76, 63, 62, 58, 70,
                 40, 45, 37, 34, 38, 38, 41, 37, 31, 48, 31, 40, 40, 51, 33],
    "division": ["men"] * 15 + ["women"] * 15,
}
```

### Default

```python
fig = bpl.line(data, x="year", y="hot_dogs", color="division",
               title="Nathan's Hot Dog Eating Contest",
               x_label="Year", y_label="Hot Dogs Eaten")
```

![Default theme](assets/examples/gallery_default.svg)

### Bluesky

```python
fig = bpl.line(data, x="year", y="hot_dogs", color="division",
               title="Nathan's Hot Dog Eating Contest",
               x_label="Year", y_label="Hot Dogs Eaten",
               theme="bluesky")
```

![Bluesky theme](assets/examples/gallery_bluesky.svg)

### PDF

```python
fig = bpl.line(data, x="year", y="hot_dogs", color="division",
               title="Nathan's Hot Dog Eating Contest",
               x_label="Year", y_label="Hot Dogs Eaten",
               theme="pdf")
```

![PDF theme](assets/examples/gallery_pdf.svg)

### Print

```python
fig = bpl.line(data, x="year", y="hot_dogs", color="division",
               title="Nathan's Hot Dog Eating Contest",
               x_label="Year", y_label="Hot Dogs Eaten",
               theme="print")
```

![Print theme](assets/examples/gallery_print.svg)

### Magazine

```python
fig = bpl.line(data, x="year", y="hot_dogs", color="division",
               title="Nathan's Hot Dog Eating Contest",
               x_label="Year", y_label="Hot Dogs Eaten",
               theme="magazine")
```

![Magazine theme](assets/examples/gallery_magazine.svg)

Aliases work too — `social`, `arxiv`, and `economist` map to their obvious counterparts. See the [API Reference](api/index.md) for the full `ThemeSpec` schema.

---

## Plot types

Four built-in plot types. Each is a single function call that returns a `Figure` object.

### Scatter

Two numeric variables, optionally grouped by a categorical column.

```python
import botplotlib as bpl

fig = bpl.scatter(
    {
        "weight": [2.5, 3.0, 3.5, 4.0, 4.5, 3.2, 2.8],
        "mpg": [30, 28, 25, 22, 20, 26, 29],
        "origin": ["US", "EU", "EU", "US", "JP", "JP", "EU"],
    },
    x="weight",
    y="mpg",
    color="origin",
    title="Fuel Efficiency by Vehicle Weight",
    x_label="Weight (1000 lbs)",
    y_label="Miles per Gallon",
)
```

![Scatter plot with color groups](assets/examples/pt_scatter.svg)

### Line

Trends and time series. Multiple series are created automatically when `color` is specified.

```python
months = list(range(1, 13))
fig = bpl.line(
    {
        "month": months * 2,
        "revenue": [10, 13, 15, 14, 18, 22, 25, 28, 26, 30, 35, 40,
                    20, 19, 21, 22, 23, 22, 24, 25, 26, 25, 27, 28],
        "segment": ["SaaS"] * 12 + ["Hardware"] * 12,
    },
    x="month",
    y="revenue",
    color="segment",
    title="Revenue by Segment",
    x_label="Month",
    y_label="Revenue ($M)",
)
```

![Multi-series line chart](assets/examples/pt_line.svg)

### Bar

Always starts from zero because bar charts that don't start from zero are lying to you.

```python
fig = bpl.bar(
    {
        "language": ["Python", "JavaScript", "TypeScript", "Rust", "Go", "Java"],
        "score": [92, 78, 71, 54, 48, 45],
    },
    x="language",
    y="score",
    title="Programming Language Popularity",
    x_label="Language",
    y_label="Popularity Score",
)
```

![Bar chart](assets/examples/pt_bar.svg)

Add `labels=True` for value labels on each bar. Use `label_format` for custom formatting (e.g. `"${:,.0f}"`).

### Waterfall

Shows how an initial value gets increased or decreased by intermediate values until you reach a final total. If you've ever had to explain where the money went, this is the chart for that.

```python
fig = bpl.waterfall(
    {
        "category": ["Revenue", "COGS", "Gross Profit", "OpEx",
                      "Tax", "Net Income"],
        "amount": [500, -200, 300, -150, -45, 105],
    },
    x="category",
    y="amount",
    title="Income Statement Waterfall",
    x_label="",
    y_label="Amount ($K)",
)
```

![Waterfall chart](assets/examples/pt_waterfall.svg)

!!! note
    Waterfall does not support the `color` parameter — colors are determined automatically based on positive/negative values.

### Parameters

All plot functions share these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | any | *required* | Data in any supported format (see below) |
| `x` | `str` | *required* | Column name for x-axis |
| `y` | `str` | *required* | Column name for y-axis |
| `color` | `str` | `None` | Column name for color grouping |
| `title` | `str` | `None` | Plot title |
| `subtitle` | `str` | `None` | Plot subtitle |
| `x_label` | `str` | `None` | X-axis label |
| `y_label` | `str` | `None` | Y-axis label |
| `footnote` | `str` | `None` | Footnote below the plot |
| `theme` | `str` | `"default"` | Theme name |
| `width` | `float` | `800` | Canvas width in pixels |
| `height` | `float` | `500` | Canvas height in pixels |

Bar and waterfall also accept `labels` (`bool`, default `False`) and `label_format` (`str`).

### Layered plots

For multi-layer plots (e.g., line + scatter overlay), use `bpl.plot()` with chained `.add_*()` methods:

```python
fig = (
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
fig.title = "Actual vs Forecast Revenue ($B)"
fig.save_svg("layered.svg")
```

![Layered line and scatter plot](assets/examples/pt_layered.svg)

Available layer methods: `.add_scatter()`, `.add_line()`, `.add_bar()`. Each accepts `x`, `y`, and optional `color` parameters.

---

## Data formats

Pass whatever your pipeline produces. botplotlib figures it out.

Supported formats:

1. **Dict of columns** — `{"x": [1, 2, 3], "y": [4, 5, 6]}` (recommended)
2. **List of dicts** — `[{"x": 1, "y": 4}, {"x": 2, "y": 5}]`
3. **Polars DataFrame**
4. **Pandas DataFrame**
5. **Arrow Table / RecordBatch**
6. **Generator / iterator** — materialized to list of dicts automatically

If a column doesn't exist, the compiler raises a clear `ValueError` naming the missing column.

---

## JSON path

Agents can generate plots by producing a `PlotSpec` as JSON — no Python code execution required. Same structural gates (WCAG contrast, validation) apply regardless of who built the spec.

### `Figure.from_json()`

Parse a PlotSpec from a JSON string:

```python
import botplotlib as bpl

json_string = '''{
    "data": {
        "columns": {
            "x": [1, 2, 3, 4, 5],
            "y": [1, 4, 9, 16, 25]
        }
    },
    "layers": [{"geom": "scatter", "x": "x", "y": "y"}],
    "labels": {"title": "Perfect Squares", "x": "n", "y": "n squared"},
    "theme": "default"
}'''

fig = bpl.Figure.from_json(json_string)
fig.save_svg("from_json.svg")
```

![Plot from JSON](assets/examples/json_from_dict.svg)

### `Figure.from_dict()`

Construct from a plain dict — the typical output of an LLM function/tool call:

```python
spec_dict = {
    "data": {
        "columns": {
            "year": [2020, 2021, 2022, 2023, 2024],
            "revenue": [4.2, 3.8, 5.1, 6.3, 8.2],
        }
    },
    "layers": [{"geom": "line", "x": "year", "y": "revenue"}],
    "labels": {"title": "Revenue Growth"},
    "theme": "bluesky",
}

fig = bpl.Figure.from_dict(spec_dict)
fig.save_svg("from_dict.svg")
```

![Plot from dict](assets/examples/json_from_dict_line.svg)

### PlotSpec JSON schema

```json
{
    "data": {
        "columns": {
            "column_name": [values...]
        }
    },
    "layers": [
        {
            "geom": "scatter | line | bar | waterfall",
            "x": "column_name",
            "y": "column_name",
            "color": "column_name (optional)",
            "labels": "boolean, default false (optional)",
            "label_format": "string (optional)"
        }
    ],
    "labels": {
        "title": "string (optional)",
        "subtitle": "string (optional)",
        "x": "string (optional)",
        "y": "string (optional)",
        "footnote": "string (optional)"
    },
    "legend": {
        "show": true,
        "position": "top | bottom | left | right"
    },
    "size": {
        "width": 800,
        "height": 500
    },
    "theme": "default | bluesky | pdf | print | magazine"
}
```

---

## Refactoring from matplotlib

Feed it your matplotlib scripts. The translation is often shorter than the import block it replaces.

```python
from botplotlib.refactor import to_botplotlib_code

bpl_code = to_botplotlib_code("""
import matplotlib.pyplot as plt
import numpy as np

x = [0, 1, 2, 3, 4, 5]
y = [0, 1, 4, 9, 16, 25]

plt.figure(figsize=(8, 5))
plt.scatter(x, y)
plt.title("x squared")
plt.xlabel("x")
plt.ylabel("x^2")
plt.savefig("old_plot.png")
""")

print(bpl_code)
```

Output:

```python
import botplotlib as bpl

fig = bpl.scatter(
    {"x": [0, 1, 2, 3, 4, 5], "y": [0, 1, 4, 9, 16, 25]},
    x="x",
    y="y",
    title="x squared",
    x_label="x",
    y_label="x^2",
)
fig.save_svg("plot.svg")
```

9 lines of matplotlib become 1 function call. Because it uses AST analysis rather than execution, matplotlib doesn't even need to be installed.

You can also extract a `PlotSpec` directly:

```python
from botplotlib.refactor import from_matplotlib
import botplotlib as bpl

spec = from_matplotlib("my_old_script.py")
fig = bpl.render(spec)
fig.save_svg("migrated.svg")
```
