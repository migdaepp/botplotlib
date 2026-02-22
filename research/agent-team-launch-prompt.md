# Agent Team Launch Prompt

Start a new session:

```bash
claude --dangerously-skip-permissions
```

Then paste everything below the line.

---

Create an agent team with 5 teammates to build out the botplotlib extensibility architecture and polish the library for real-world use. This covers the geom plugin system, renderer generalization, agent JSON path, matplotlib refactor polish, and CI governance infrastructure.

Before creating the team, read these files to understand the project:
- `AGENTS.md` and `CLAUDE.md` — project conventions and architecture
- `research/cyborg-extensibility-and-governance.md` — extensibility design
- `botplotlib/compiler/compiler.py` — current compiler (will be heavily refactored)
- `botplotlib/spec/models.py` — PlotSpec and LayerSpec models
- `botplotlib/render/svg_renderer.py` — current renderer
- `botplotlib/_api.py` — public API functions
- `botplotlib/figure.py` — Figure class

Important context: the end goal is making it trivially easy for a cyborg team (human + AI agent) to add new plot types. The first real test will be Charlie (co-creator, climate scientist) and his agent adding a waterfall chart. Everything we build here is infrastructure for that moment.

## Team structure

### Teammate 1: "geom-architect"
**Priority: HIGHEST. Other teammates depend on this work.**
Require plan approval before implementation.

The foundational refactor: replace hardcoded geom dispatch with a plugin architecture.

Tasks:
1. Define the Geom protocol in `botplotlib/geoms/__init__.py`. A base class or Protocol with three methods: `validate(layer, data)`, `compile(layer, data, scales, theme, plot_area) -> list[Primitive]`, and `default_scales(layer, data) -> dict`. Also define unified primitive types — extend the existing CompiledPoint/CompiledLine/CompiledBar/CompiledText, and add CompiledPath for arbitrary SVG shapes (needed for future geoms like Sankey).

2. Create a geom registry: a dict mapping geom name strings to handler classes. The compiler dispatches to the registry instead of the current hardcoded if/elif chain.

3. Migrate scatter, line, and bar into the new protocol. Create `botplotlib/geoms/scatter.py`, `botplotlib/geoms/line.py`, `botplotlib/geoms/bar.py`. Extract the existing compile logic from `compiler.py` into classes implementing the Geom protocol. `compile_spec()` should now do `registry[layer.geom].compile(...)`.

4. Change `LayerSpec.geom` from `Literal["scatter", "line", "bar"]` to `str`, validated against the geom registry at compile time. Error message must be specific: "Unknown geom 'xyz'. Available geoms: scatter, line, bar. See AGENTS.md for how to add new geoms."

5. Run `uv run pytest` — ALL existing tests must pass. Run `uv run ruff check .` and `uv run black --check .`. Fix anything that breaks. Commit.

**Files owned**: `botplotlib/compiler/compiler.py`, `botplotlib/spec/models.py`, new `botplotlib/geoms/` directory (all files within). Do NOT touch `_api.py`, `figure.py`, `render/`, or `AGENTS.md`.

### Teammate 2: "renderer-engineer"
**Depends on geom-architect finishing tasks 1-3** (needs to know the primitive types).

Generalize the renderer so new geoms require zero renderer changes.

Tasks (blocked until geom-architect finishes):
1. Refactor `svg_renderer.py` so that instead of iterating `compiled.points`, `compiled.lines`, `compiled.bars` as separate lists, it iterates a unified list of primitives. Each primitive type knows how to render itself (or has a corresponding render function). This means a new geom that returns standard primitives (Rect, Line, Circle, Path, Text) gets rendered automatically.

2. Add SVG path rendering support for `CompiledPath` — needed for future geoms like area charts, Sankey diagrams, violin plots.

3. Ensure all existing golden SVG baselines still match (run `uv run pytest`). The renderer refactor must be behavior-preserving — identical SVG output for identical inputs.

4. Run lint and format checks. Commit.

**Files owned**: `botplotlib/render/svg_renderer.py`, `botplotlib/render/svg_builder.py`. Do NOT touch `compiler/compiler.py`, `geoms/`, or `_api.py`.

While waiting for the geom-architect, this teammate can read the current renderer code and plan the refactor.

### Teammate 3: "json-engineer"
**Independent — can start immediately.**

Wire up the agent JSON path so the dual-path architecture (AGENTS.md diagram) actually works end-to-end.

Tasks:
1. Add `Figure.from_json(json_string)` classmethod that takes a PlotSpec JSON string, validates with Pydantic, and returns a Figure ready to render. Also add `Figure.from_dict(d)` for plain dicts (the typical LLM function-call output format).

2. Add `bpl.from_json()` and `bpl.from_dict()` as top-level convenience re-exports in `__init__.py`.

3. Write tests in `tests/test_json_path.py`: valid round-trip (PlotSpec → JSON → from_json → SVG matches original), missing required fields (clear error), extra fields (ignored gracefully), realistic LLM-generated dict example, malformed types.

4. Run tests, lint, format. Commit.

**Files owned**: `botplotlib/figure.py`, `botplotlib/__init__.py` (add re-exports only), new `tests/test_json_path.py`. Do NOT touch `compiler/`, `spec/models.py`, `_api.py`, or `render/`.

### Teammate 4: "refactor-polish"
**Independent — can start immediately.**

The matplotlib refactor module is the marketing hook for external adoption. Polish it.

Tasks:
1. Read the current `botplotlib/refactor/from_matplotlib.py` and its tests. Understand what patterns it handles and what it misses.

2. Test it against realistic matplotlib scripts. Write 3-5 test scripts covering common patterns: basic scatter/line/bar with styling, subplots (should produce a clear error or best-effort), custom colors/markers, title/label/legend configuration, savefig calls.

3. Improve pattern coverage for the most common gaps found in step 2. Focus on the patterns that data scientists actually use (pandas DataFrame.plot(), seaborn-style calls, etc.).

4. Create compelling before/after comparison examples in `examples/refactor_examples/` — showing the matplotlib original and the botplotlib equivalent side by side. These will go in the README eventually.

5. Run tests, lint, format. Commit.

**Files owned**: `botplotlib/refactor/` (all files), new `examples/refactor_examples/` directory, new or updated tests in `tests/` related to refactor. Do NOT touch `compiler/`, `render/`, `_api.py`, or `figure.py`.

### Teammate 5: "ci-engineer"
**Independent — can start immediately.**

Build the automated validation infrastructure described in `research/cyborg-extensibility-and-governance.md`. This is what replaces the human maintainer bottleneck.

Tasks:
1. Create a pytest plugin or conftest fixture for **geom stress testing**: given a geom name, automatically run it against edge-case data — empty dataset, single point, NaN values, very large values, negative values, mixed types, 10000 points. Every registered geom should survive these without unhandled exceptions.

2. Create a **geom protocol structural check**: a test that discovers all registered geoms and verifies each one implements the full protocol (has validate, compile, default_scales with correct signatures). This catches incomplete contributions automatically.

3. Set up **GitHub Actions CI** in `.github/workflows/ci.yml`: run pytest, ruff, black on every push and PR. This is the basic automated gate.

4. Add a visual regression helper: a test utility that renders a geom's test cases to SVG and diffs against golden baselines, with clear failure output showing what changed. (The `--update-baselines` pytest flag already exists; make sure it works cleanly with the new geom architecture.)

5. Run tests, lint, format. Commit.

**Files owned**: `.github/` (new), `tests/conftest.py`, new test utilities in `tests/`. Do NOT touch `compiler/`, `render/`, `_api.py`, or `figure.py`.

## Task dependencies

Set these up when creating the task list:
- **renderer-engineer's tasks** are ALL blocked by geom-architect's tasks 1-3
- Everything else can start immediately
- The geom-architect should be the FIRST teammate to get plan approval so others aren't waiting long

## Coordination rules

- **Require plan approval** for geom-architect before implementation. Approve it quickly — other work depends on it.
- **File ownership is strict.** If a teammate needs a change in another teammate's files, they message that teammate. They do NOT edit the file themselves.
- **Every task ends with**: `uv run pytest && uv run ruff check . && uv run black --check .`
- **Commit after each major task.** Atomic commits, descriptive messages.
- **Do NOT push to remote** — just commit locally. The human will review and push.
- When geom-architect finishes, **message renderer-engineer immediately** so they can unblock.
- **Lead: do NOT implement tasks yourself.** Your job is coordination. Wait for teammates to finish. Reassign work if someone gets stuck.
