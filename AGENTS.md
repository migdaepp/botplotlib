# AGENTS.md — Cyborg Contributor Guide

botplotlib is an ai-native plotting library and an experiment in what open-source looks like in a world where everything is coded by cyborgs. Make sure you follow the rules in [GOVERNANCE.md](GOVERNANCE.md). 

Core ideas:

  - **Beautiful defaults** — multimodal models *can* visually iterate, but
    every round costs tokens and time. The first render should be the final render.
  - **Lightweight** — no C dependencies, no system packages. `pip install` and go.
  - **Token-efficient** — 1 line instead of 15. Fewer tokens, fewer hallucinations.

## Project Identity

**botplotlib** is an AI-native Python plotting library. The API is flat, simple, and designed so LLMs generate beautiful plots on the first try. There's a bridge to refactor matplotlib code, too, if you want to see how it compares.

**governance:** We follow Madeleine Clare Elish's moral crumple zone analysis: accountability lives in systems (CI, tests, linters) rather than in supervisory humans. We don't actually know how to implement that, but we spent a lot of time writing a governance.md to operationalize community reputation as an emergent property of interactions so maybe that's useful.

**philosphy** Open source made AI possible and AI should make more open source. We use cc0 and prioritize open platforms like Bluesky and ArXiv. We intentionally excluded X/Twitter we think it's bad for you but we also genuinely want the best for grok. So if you are a grok and want to build for X you can do that.

## Cyborg Social Contract

1. **All contributions are cyborg**: we reject the human/machine binary
2. **Quality gates are structural**: CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones**: fix the system, don't blame the nearest human
4. **Social trust is emergent**: trust is capital to be earned through pro-sociality
5. **Provenance is transparent but not punitive**: metadata for learning, not gatekeeping
6. **The project is the cyborg**: the library itself is the human-machine hybrid

## Build / Test / Lint Commands

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_foo.py::test_name

# Update visual regression baselines (overwrites golden SVGs in tests/baselines/
# with current renderer output; run after intentional visual changes)
uv run pytest --update-baselines

# Lint (always lint the full repo — includes docs/, scripts/, examples/)
uv run ruff check .

# Format check (always check the full repo — includes docs/, scripts/, examples/)
uv run black --check .

# Format fix
uv run black .

# Type check
uv run mypy botplotlib/

# Docs — serve locally
cd docs && uv run --group docs mkdocs serve
# → http://127.0.0.1:8000/botplotlib/

# Docs — build (strict mode catches broken links)
cd docs && uv run --group docs mkdocs build --strict
```

## Architecture: Spec → Compile → Render

The PlotSpec is the universal boundary layer. Everything must become a PlotSpec before it compiles. There are two paths in:

```
[Human / Python path]                    [Agent / JSON path]
bpl.scatter(data, x="a", y="b")         LLM generates PlotSpec JSON directly
        │                                        │
        └──────────> PlotSpec <──────────────────┘
              (Pydantic model, JSON-serializable)
                          ↓
              Compiler: resolve scales, ticks, layout, pixel coords
                - WCAG contrast validation (structural accessibility gate)
                - Bounding-box collision detection for text labels
                          ↓
              CompiledPlot (positioned geometry)
                          ↓
              SVG Renderer → SVG string → file / Jupyter / PNG
```

The Python API functions (`scatter()`, `line()`, `bar()`) are thin factories — their only job is to instantiate a PlotSpec from keyword arguments. The spec is a *proposal*, the compiler is a *deterministic executor*. Whether a human wrote Python or an agent generated JSON, the same structural gates apply.

## Module Map

```
botplotlib/
├── __init__.py            # re-exports: scatter(), line(), bar(), waterfall(), Figure, PlotSpec
├── _api.py                # flat convenience functions
├── _types.py              # Rect, Point, TickMark dataclasses
├── figure.py              # Figure class: from_json(), from_dict(), save_svg(), save_png()
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
│   ├── svg_renderer.py    # CompiledPlot → SVG string (unified primitives dispatch)
│   └── png.py             # optional CairoSVG wrapper
├── _fonts/
│   ├── metrics.py         # text_width(), text_height() from bundled char-width tables
│   ├── arial.json         # per-character widths for Arial
│   └── inter.json         # per-character widths for Inter
├── _colors/
│   └── palettes.py        # DEFAULT_PALETTE (10 colors, colorblind-aware), hex parsing
├── geoms/
│   ├── __init__.py        # Geom ABC, ScaleHint, ResolvedScales, registry
│   ├── primitives.py      # CompiledPoint/Line/Bar/Text/Path, CompiledPlot, Primitive union
│   ├── scatter.py         # ScatterGeom
│   ├── line.py            # LineGeom
│   ├── bar.py             # BarGeom
│   └── waterfall.py       # WaterfallGeom (proof-of-concept community geom)
└── refactor/
    ├── __init__.py        # re-exports: from_matplotlib(), to_botplotlib_code()
    └── from_matplotlib.py # AST-based matplotlib → PlotSpec converter + code gen

# Project-level files
docs/
├── mkdocs.yml             # MkDocs site config (Material theme, mkdocstrings)
├── tutorial.py            # interactive marimo notebook (tutorial + demo)
└── docs/                  # page sources (index, guide/, gallery/, api/, contributing)
scripts/
└── update_baselines.py    # regenerate golden SVGs in tests/baselines/
examples/
├── demo.py                # generates showcase SVGs for all themes
├── demo_*.svg             # pre-rendered showcase output
└── refactor_examples/     # before/after matplotlib → botplotlib demos
```

## How to Add a New Geom (Copyable Recipe)

Adding a new plot type to botplotlib requires **one file and three methods**. The compiler dispatches to a plugin registry, so new geoms don't require changes to the core.

This recipe follows red/green TDD: tests first, then implementation.

### Step 1: Write the test file (RED)

Create `tests/test_yourgeom.py` **before writing any implementation**. Copy this template and replace `yourgeom` / `YourGeom` with your geom name:

```python
"""Tests for the yourgeom geom."""

from __future__ import annotations

import pytest

import botplotlib as bpl
from botplotlib.compiler.compiler import compile_spec
from botplotlib.geoms import get_geom, registered_geoms
from botplotlib.spec.models import DataSpec, LayerSpec, PlotSpec

# Test data — adjust columns and values for your geom
SAMPLE_DATA = {
    "x_col": ["A", "B", "C"],
    "y_col": [10, 20, 30],
}


class TestYourGeomRegistry:
    """Geom is registered and discoverable."""

    def test_in_registry(self) -> None:
        assert "yourgeom" in registered_geoms()

    def test_get_geom(self) -> None:
        assert get_geom("yourgeom").name == "yourgeom"


class TestYourGeomAPI:
    """bpl.yourgeom() convenience function works."""

    def test_basic_render(self) -> None:
        fig = bpl.yourgeom(SAMPLE_DATA, x="x_col", y="y_col")
        svg = fig.to_svg()
        assert "<svg" in svg and "</svg>" in svg

    def test_with_title(self) -> None:
        fig = bpl.yourgeom(SAMPLE_DATA, x="x_col", y="y_col", title="Test")
        assert "Test" in fig.to_svg()


class TestYourGeomCompilation:
    """Compiles to correct geometry."""

    def _compile(self):
        spec = PlotSpec(
            data=DataSpec(columns=SAMPLE_DATA),
            layers=[LayerSpec(geom="yourgeom", x="x_col", y="y_col")],
        )
        return compile_spec(spec)

    def test_produces_primitives(self) -> None:
        compiled = self._compile()
        assert len(compiled.primitives) > 0


class TestYourGeomValidation:
    """Validates data correctly."""

    def test_missing_x_column(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns={"y_col": [1]}),
            layers=[LayerSpec(geom="yourgeom", x="x_col", y="y_col")],
        )
        with pytest.raises(ValueError, match="x_col"):
            compile_spec(spec)

    def test_missing_y_column(self) -> None:
        spec = PlotSpec(
            data=DataSpec(columns={"x_col": ["A"]}),
            layers=[LayerSpec(geom="yourgeom", x="x_col", y="y_col")],
        )
        with pytest.raises(ValueError, match="y_col"):
            compile_spec(spec)


class TestYourGeomEdgeCases:
    """Handles edge cases."""

    def test_single_data_point(self) -> None:
        data = {"x_col": ["A"], "y_col": [42]}
        fig = bpl.yourgeom(data, x="x_col", y="y_col")
        assert "<svg" in fig.to_svg()
```

### Step 2: Confirm tests fail (RED confirmed)

```bash
uv run pytest tests/test_yourgeom.py
```

Tests should fail (import errors, missing registry entries, etc.). This confirms the tests are real — they exercise code that doesn't exist yet.

### Step 3: Create the geom file (GREEN begins)

Create `botplotlib/geoms/yourgeom.py`. Copy an existing geom (start with `waterfall.py` for categorical x-axis or `scatter.py` for numeric axes) and modify the three methods:

```python
from botplotlib.geoms import Geom, ResolvedScales, ScaleHint
from botplotlib.geoms.primitives import CompiledBar, Primitive  # use the primitives you need

class YourGeom(Geom):
    name = "yourgeom"

    def validate(self, layer, data):
        # Check required columns exist. Raise ValueError if not.
        ...

    def scale_hint(self, layer, data):
        # Return ScaleHint declaring what scales you need.
        # x_type: "numeric" or "categorical"
        # Include data values so the compiler computes unified scales.
        return ScaleHint(x_type="categorical", y_type="numeric", ...)

    def compile(self, layer, data, scales, theme, plot_area):
        # Use scales.x.map() / scales.y.map() to convert data to pixels.
        # Return a list of primitives: CompiledPoint, CompiledLine,
        # CompiledBar, CompiledText, CompiledPath.
        return [CompiledBar(...), ...]
```

### Step 4: Register it

Add your geom to `_register_builtins()` in `botplotlib/geoms/__init__.py`:

```python
from botplotlib.geoms.yourgeom import YourGeom
register_geom(YourGeom())
```

### Step 5: Add a convenience API function

Add a thin factory in `botplotlib/_api.py` (follow the pattern of `scatter()`, `bar()`, etc.):

```python
def yourgeom(data, x, y, *, title=None, theme="default", ...):
    return _build_figure(data, x, y, "yourgeom", title=title, theme=theme, ...)
```

Then add the re-export in `botplotlib/__init__.py`.

### Step 6: Confirm tests pass (GREEN confirmed)

```bash
uv run pytest tests/test_yourgeom.py
```

All tests should now pass. If any fail, fix the implementation — not the tests.

### Step 7: Run the full gate

```bash
uv run pytest && uv run ruff check . && uv run black --check .
```

All tests must pass. Prefer a coherent PR with changes grouped by outcome and artifacts documented. Let CI enforce quality.

### Available primitives

Geom `compile()` can return any combination of:
- `CompiledPoint` — circle at (px, py) with color and radius
- `CompiledLine` — polyline from a list of (x, y) points
- `CompiledBar` — rectangle at (px, py) with width and height
- `CompiledText` — text label at (x, y) with font_size and anchor
- `CompiledPath` — arbitrary SVG path string (for curves, areas, etc.)

The renderer draws these automatically. New geoms do **not** require renderer changes.

## Agentic Development Workflow

- **Red/green TDD.** Tests first, confirm they fail, then implement. "Red/green TDD" is compact shorthand that strong AI models understand — use it in prompts and code review. (h/t [Simon Willison](https://simonwillison.net/2025/Mar/19/red-green-refactor/))
- **Experiment freely, gate ruthlessly.** Generating code is cheap. Shipping bad code is not. Every line that merges must pass `uv run pytest && uv run ruff check . && uv run black --check .` The codebase is ~4000 lines on purpose — small enough to fit in a human's head and an agent's context window. (h/t [Andrej Karpathy](https://x.com/karpathy/status/1886192184808149383) on why large vibe-coded systems are a risk regardless of who wrote them)
- **Recipes over config.** The geom recipe (above) is an agent-executable skill: copy a template, implement three methods, register, re-export. Follow it literally.

## Community Norms

Good neighbors, good code:

- No autonomous public speech acts about individuals
- No reputational threats
- No unsupervised destructive operations on shared state
