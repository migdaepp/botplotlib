# API Reference

![a robot walks into a deli](images/a-robot-walks-into-a-deli.png){ width="400" }

## Top-level functions

::: botplotlib.scatter
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.line
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.bar
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.waterfall
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.plot
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.render
    options:
      show_root_heading: true
      heading_level: 3

---

## Figure

::: botplotlib.figure.Figure
    options:
      show_root_heading: true
      heading_level: 3
      members:
        - from_json
        - from_dict
        - to_svg
        - save_svg
        - save_png
        - spec
        - compiled
        - title
        - subtitle
        - footnote
        - add_scatter
        - add_line
        - add_bar

---

## Spec models

### PlotSpec

::: botplotlib.spec.models.PlotSpec
    options:
      show_root_heading: true
      heading_level: 4
      members: false

PlotSpec fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `DataSpec` | empty | Columnar data |
| `layers` | `list[LayerSpec]` | `[]` | Plot layers |
| `labels` | `LabelsSpec` | empty | Title and axis labels |
| `legend` | `LegendSpec` | show, right | Legend config |
| `size` | `SizeSpec` | 800x500 | Canvas dimensions |
| `theme` | `str` | `"default"` | Theme name |

### DataSpec

::: botplotlib.spec.models.DataSpec
    options:
      show_root_heading: true
      heading_level: 4
      members: false

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `columns` | `dict[str, list]` | `{}` | Column name to values mapping |

### LayerSpec

::: botplotlib.spec.models.LayerSpec
    options:
      show_root_heading: true
      heading_level: 4
      members: false

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `geom` | `str` | *required* | Geometry type (validated against registry) |
| `x` | `str` | *required* | Column name for x-axis |
| `y` | `str` | *required* | Column name for y-axis |
| `color` | `str \| None` | `None` | Column name for color grouping |
| `labels` | `bool` | `False` | Show value labels on bars |
| `label_format` | `str \| None` | `None` | Python format string for labels |

### LabelsSpec

::: botplotlib.spec.models.LabelsSpec
    options:
      show_root_heading: true
      heading_level: 4
      members: false

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `title` | `str \| None` | `None` | Plot title |
| `subtitle` | `str \| None` | `None` | Plot subtitle |
| `x` | `str \| None` | `None` | X-axis label |
| `y` | `str \| None` | `None` | Y-axis label |
| `footnote` | `str \| None` | `None` | Footnote below the plot |

### SizeSpec

::: botplotlib.spec.models.SizeSpec
    options:
      show_root_heading: true
      heading_level: 4
      members: false

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `width` | `float` | `800` | Canvas width in pixels |
| `height` | `float` | `500` | Canvas height in pixels |

---

## ThemeSpec

::: botplotlib.spec.theme.ThemeSpec
    options:
      show_root_heading: true
      heading_level: 3
      members: false

See the [Guide](../guide.md#themes) for usage examples.

---

## Refactor module

::: botplotlib.refactor.from_matplotlib
    options:
      show_root_heading: true
      heading_level: 3

::: botplotlib.refactor.to_botplotlib_code
    options:
      show_root_heading: true
      heading_level: 3

---

## Geom plugin API

### Geom (abstract base class)

::: botplotlib.geoms.Geom
    options:
      show_root_heading: true
      heading_level: 4

### Registry functions

::: botplotlib.geoms.register_geom
    options:
      show_root_heading: true
      heading_level: 4

::: botplotlib.geoms.get_geom
    options:
      show_root_heading: true
      heading_level: 4

### Built-in geoms

| Name | Class | Description |
|------|-------|-------------|
| `scatter` | `ScatterGeom` | Scatter plot points |
| `line` | `LineGeom` | Connected line series |
| `bar` | `BarGeom` | Vertical bar chart |
| `waterfall` | `WaterfallGeom` | Waterfall chart with running totals |

See [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md) for instructions on adding custom geoms.

---

## Data normalization

::: botplotlib.compiler.data_prep.normalize_data
    options:
      show_root_heading: true
      heading_level: 3

See the [Guide](../guide.md#data-formats) for supported formats.
