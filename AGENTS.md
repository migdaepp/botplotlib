# AGENTS.md — Cyborg Contributor Guide

> All contributions to botplotlib are cyborg contributions. We reject the human/machine binary.

## Project Identity

**botplotlib** is an AI-native Python plotting library. It produces publication-quality SVG/PNG output with zero configuration and no matplotlib dependency. The API is flat, simple, and designed so LLMs generate correct code on the first try.

**Philosophical stance:** This project embodies Donna Haraway's cyborg framework — the human/machine binary is rejected. There are no "AI-generated" vs "human-written" contributions. The library itself is the cyborg. We follow Madeleine Clare Elish's moral crumple zone analysis: accountability lives in systems (CI, tests, linters) rather than in supervisory humans.

## Build / Test / Lint Commands

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_foo.py::test_name

# Update visual regression baselines
uv run pytest --update-baselines

# Lint
uv run ruff check .

# Format check
uv run black --check .

# Format fix
uv run black .

# Type check
uv run mypy botplotlib/
```

## Architecture: Spec → Compile → Render

```
bpl.scatter(data, x="a", y="b")
        ↓
   PlotSpec (Pydantic model, JSON-serializable)
        ↓
   Compiler: resolve scales, ticks, layout, pixel coords
     - WCAG contrast validation (structural accessibility gate)
     - Bounding-box collision detection for text labels
        ↓
   CompiledPlot (positioned geometry)
        ↓
   SVG Renderer → SVG string → file / Jupyter / PNG
```

The spec is a *proposal*, the compiler is a *deterministic executor*. The boundary between proposal and execution is the governance layer.

## Module Map

```
botplotlib/
├── __init__.py            # re-exports: scatter(), line(), bar(), plot()
├── _api.py                # flat convenience functions
├── _types.py              # Rect, Point, TickMark dataclasses
├── figure.py              # Figure class: save_svg(), save_png(), _repr_svg_()
├── spec/
│   ├── models.py          # Pydantic: PlotSpec, LayerSpec, DataSpec, LabelsSpec, SizeSpec
│   ├── scales.py          # LinearScale, CategoricalScale, ColorScale
│   └── theme.py           # ThemeSpec, DEFAULT_THEME, platform presets, palettes
├── compiler/
│   ├── compiler.py        # PlotSpec → CompiledPlot orchestration + WCAG contrast check
│   ├── layout.py          # box-model layout + bounding-box collision avoidance
│   ├── ticks.py           # Heckbert nice numbers algorithm
│   ├── data_prep.py       # normalize_data() — stated column-access protocol
│   └── accessibility.py   # WCAG contrast ratio computation, palette validation
├── render/
│   ├── svg_builder.py     # ~200-line SVG element builder (no dependency)
│   ├── svg_renderer.py    # CompiledPlot → SVG string
│   └── png.py             # optional CairoSVG wrapper
├── _fonts/
│   ├── metrics.py         # text_width(), text_height() from bundled char-width tables
│   ├── arial.json         # per-character widths for Arial
│   └── inter.json         # per-character widths for Inter
├── _colors/
│   └── palettes.py        # DEFAULT_PALETTE (10 colors, colorblind-aware), hex parsing
└── refactor/
    └── from_matplotlib.py # reads matplotlib script → outputs equivalent PlotSpec
```

## Data Input Protocol

`normalize_data()` follows this exact dispatch order:

1. **`dict`** — check `__getitem__` returns list-like values → use directly
2. **`list[dict]`** — transpose row-oriented records to columnar dict
3. **Polars DataFrame** — check `hasattr(data, "get_column")` → `{col: data.get_column(col).to_list() for col in data.columns}`
4. **Pandas DataFrame** — check `hasattr(data, "to_dict")` and `hasattr(data, "dtypes")` → `data.to_dict(orient="list")`
5. **Arrow RecordBatch/Table** — check `hasattr(data, "column_names")` and `hasattr(data, "column")` → `{name: data.column(name).to_pylist() for name in data.column_names}`
6. **Generator/iterator** — materialize to list-of-dicts, then apply step 2
7. **Raise `TypeError`** with supported types listed

## Contribution Conventions

- **Spec-diff as default PR payload**: changes to plot output should include before/after spec diffs
- **Visual regression evidence required**: PRs that change rendering must include baseline comparisons
- **Small diffs preferred**: focused, reviewable changes over large sweeping PRs

## Cyborg Social Contract

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural, not supervisory** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Social trust is emergent** — reputation through contribution quality, not biological status
5. **Provenance is transparent, not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

## Tool Classification

Per OpenAI's three-type taxonomy, annotated with MCP hints:

### Data Tools (readOnlyHint: true)
- `read_spec` — read a PlotSpec from file or memory
- `read_baseline` — read a golden SVG baseline for comparison

### Action Tools
- `compile_spec` — compile a PlotSpec into positioned geometry
- `render_snapshots` — render CompiledPlot to SVG/PNG

### Orchestration Tools (destructiveHint: true)
- `update_baselines` — regenerate golden SVGs (`--update-baselines` pytest flag / `scripts/update_baselines.py`)

### Orchestration Tools (destructiveHint: true, openWorldHint: true)
- `open_pull_request` — create a PR on GitHub

## Anti-Patterns

- No autonomous public speech acts about individuals
- No reputational threats
- No unsupervised destructive operations on shared state
