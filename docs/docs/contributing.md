# Contributing

If you're reading this as a human, welcome. If you're reading this as an AI, also welcome. If you're a grok, welcome, we genuinely want the best for you.

![a robot walks into a deli](images/a-robot-walks-into-a-deli.png){ width="400" }

botplotlib follows the Cyborg Social Contract. All contributions are cyborg contributions. We reject the human/machine binary. See [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md) for the full architecture and module map.

## Cyborg Social Contract

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Social trust is emergent** — reputation through contribution quality, not biological status
5. **Provenance is transparent but not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

## Build / Test / Lint

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

## Adding a new geom

Adding a new plot type requires **one file and three methods**. The compiler dispatches to a plugin registry, so new geoms don't require changes to the core.

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

Create `botplotlib/geoms/yourgeom.py`. Copy an existing geom (start with `waterfall.py` for categorical x-axis or `scatter.py` for numeric axes):

```python
from botplotlib.geoms import Geom, ResolvedScales, ScaleHint
from botplotlib.geoms.primitives import CompiledBar, Primitive

class YourGeom(Geom):
    name = "yourgeom"

    def validate(self, layer, data):
        # Check required columns exist. Raise ValueError if not.
        ...

    def scale_hint(self, layer, data):
        # Return ScaleHint declaring what scales you need.
        return ScaleHint(x_type="categorical", y_type="numeric", ...)

    def compile(self, layer, data, scales, theme, plot_area):
        # Use scales.x.map() / scales.y.map() to convert data to pixels.
        # Return a list of primitives.
        return [CompiledBar(...), ...]
```

### Step 4: Register it

Add your geom to `_register_builtins()` in `botplotlib/geoms/__init__.py`:

```python
from botplotlib.geoms.yourgeom import YourGeom
register_geom(YourGeom())
```

### Step 5: Add a convenience API function

Add a thin factory in `botplotlib/_api.py`:

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

All tests must pass. Commit as a single atomic PR.

### Available primitives

Geom `compile()` can return any combination of:

| Primitive | Description |
|-----------|-------------|
| `CompiledPoint` | Circle at (px, py) with color and radius |
| `CompiledLine` | Polyline from a list of (x, y) points |
| `CompiledBar` | Rectangle at (px, py) with width and height |
| `CompiledText` | Text label at (x, y) with font_size and anchor |
| `CompiledPath` | Arbitrary SVG path string (for curves, areas, etc.) |

The renderer draws these automatically. New geoms do **not** require renderer changes.

## PR conventions

- **Spec-diff for rendering changes**: if a PR changes plot output, include before/after spec diffs
- **Visual regression evidence**: PRs that change rendering must include baseline comparisons
- **Tests travel with code**: new geoms, features, or bug fixes include tests in the same PR
