# Contributing

botplotlib follows the Cyborg Social Contract — all contributions are cyborg contributions. We reject the human/machine binary.

For the full architecture overview, design principles, and module map, see [AGENTS.md](https://github.com/migdaepp/botplotlib/blob/main/AGENTS.md).

## Cyborg Social Contract

1. **All contributions are cyborg** — the human/machine binary is rejected
2. **Quality gates are structural, not supervisory** — CI/tests/linters apply equally regardless of origin
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

### Step 1: Create the geom file

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

### Step 2: Register it

Add your geom to `_register_builtins()` in `botplotlib/geoms/__init__.py`:

```python
from botplotlib.geoms.yourgeom import YourGeom
register_geom(YourGeom())
```

### Step 3: Add a convenience API function

Add a thin factory in `botplotlib/_api.py`:

```python
def yourgeom(data, x, y, *, title=None, theme="default", ...):
    return _build_figure(data, x, y, "yourgeom", title=title, theme=theme, ...)
```

Then add the re-export in `botplotlib/__init__.py`.

### Step 4: Write tests

Create `tests/test_yourgeom.py`. Cover:

- Basic rendering (SVG contains expected elements)
- Compilation (correct number of primitives)
- Validation (missing columns produce clear errors)
- Edge cases (single data point, empty data, extreme values)

### Step 5: Run the gate

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

### Atomic, verifiable PRs

Contributions must be submitted as atomic, single-concern pull requests. The size of a PR must not exceed:

- The system's capacity to provide clear visual regression evidence
- The human's capacity to easily verify it

### PR payload expectations

- **Spec-diff for rendering changes**: if a PR changes plot output, include before/after spec diffs
- **Visual regression evidence**: PRs that change rendering must include baseline comparisons
- **Tests travel with code**: new geoms, features, or bug fixes include tests in the same PR
