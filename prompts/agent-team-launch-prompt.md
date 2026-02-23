# Agent Team Launch Prompt

Start a new session:

```bash
claude --dangerously-skip-permissions
```

Then paste everything below the line.

---

Create an agent team to build out the botplotlib extensibility architecture and polish the library for real-world use. The lead (you) builds the geom plugin system directly. Teammates handle renderer generalization, agent JSON path, matplotlib refactor polish, TOON/AI-native research, and CI governance — in parallel, using worktrees for isolation.

Before creating the team, read these files to understand the project:
- `AGENTS.md` and `CLAUDE.md` — project conventions and architecture
- `research/cyborg-extensibility-and-governance.md` — extensibility design
- `research/open-source-stewardship.md` — governance philosophy, ecological CI/CD, macro synthesis pipeline
- `botplotlib/compiler/compiler.py` — current compiler (will be heavily refactored)
- `botplotlib/spec/models.py` — PlotSpec and LayerSpec models
- `botplotlib/render/svg_renderer.py` — current renderer
- `botplotlib/_api.py` — public API functions
- `botplotlib/figure.py` — Figure class

Important context: the end goal is making it trivially easy for a cyborg team (human + AI agent) to add new plot types. The first real test will be Charlie (co-creator, climate scientist) and his agent adding a waterfall chart. Everything we build here is infrastructure for that moment.

## What you (the lead) build directly

### Track 1: Geom plugin architecture
**Priority: HIGHEST. Teammates depend on this work.**

The foundational refactor: replace hardcoded geom dispatch with a plugin architecture. Sequenced as:

1. Define unified primitive types and `CompiledPlot` unified interface. Extend the existing CompiledPoint/CompiledLine/CompiledBar/CompiledText, and add CompiledPath for arbitrary SVG shapes (needed for future geoms like Sankey). **Commit this first — it unblocks renderer-engineer.**

2. Define the Geom protocol in `botplotlib/geoms/__init__.py`. A base class or Protocol with three methods: `validate(layer, data)`, `compile(layer, data, scales, theme, plot_area) -> list[Primitive]`, and `default_scales(layer, data) -> dict`. Create a geom registry: a dict mapping geom name strings to handler classes.

3. Migrate scatter, line, and bar into the new protocol. Create `botplotlib/geoms/scatter.py`, `botplotlib/geoms/line.py`, `botplotlib/geoms/bar.py`. Extract the existing compile logic from `compiler.py` into classes implementing the Geom protocol. `compile_spec()` should now do `registry[layer.geom].compile(...)`.

4. Change `LayerSpec.geom` from `Literal["scatter", "line", "bar"]` to `str`, validated against the geom registry at compile time. Error message must be specific: "Unknown geom 'xyz'. Available geoms: scatter, line, bar. See AGENTS.md for how to add new geoms."

5. Build waterfall as proof of concept — `botplotlib/geoms/waterfall.py` + `bpl.waterfall()` convenience function + golden baseline tests.

6. Run `uv run pytest` — ALL existing tests must pass. Run `uv run ruff check .` and `uv run black --check .`. Fix anything that breaks. Commit.

After committing primitive types (step 1), **message renderer-engineer immediately** so they can unblock.

### Track 4: Recipe docs
Once waterfall proves the pattern, update AGENTS.md with a copyable "How to add a new geom" recipe. This is what turns architecture into ecosystem.

**Files owned by lead**: `botplotlib/compiler/compiler.py`, `botplotlib/spec/models.py`, new `botplotlib/geoms/` directory (all files within), `botplotlib/_api.py`, `botplotlib/__init__.py`, `AGENTS.md`.

## Team structure

All teammates run in **worktrees** (`isolation: "worktree"`) to avoid git/filesystem collisions.

### Teammate: "renderer-engineer"
**Track 2: Renderer generalization**
Model: Opus. Starts: After lead commits primitive types.

Generalize the renderer so new geoms require zero renderer changes. While waiting for primitive types, read the current renderer code and plan the refactor.

Tasks:
1. Refactor `svg_renderer.py` so that instead of iterating `compiled.points`, `compiled.lines`, `compiled.bars` as separate lists, it iterates a unified list of primitives. Each primitive type knows how to render itself (or has a corresponding render function). This means a new geom that returns standard primitives (Rect, Line, Circle, Path, Text) gets rendered automatically.

2. Add SVG path rendering support for `CompiledPath` — needed for future geoms like area charts, Sankey diagrams, violin plots.

3. Ensure all existing golden SVG baselines still match (run `uv run pytest`). The renderer refactor must be behavior-preserving — identical SVG output for identical inputs.

4. Run lint and format checks. Commit.

**Files owned**: `botplotlib/render/svg_renderer.py`, `botplotlib/render/svg_builder.py`. Do NOT touch `compiler/`, `geoms/`, `_api.py`, `__init__.py`, or `figure.py`.

### Teammate: "json-engineer"
**Track 3: Agent JSON path**
Model: Sonnet. Starts: Immediately.

Wire up the agent JSON path so the dual-path architecture (AGENTS.md diagram) actually works end-to-end.

Tasks:
1. Add `Figure.from_json(json_string)` classmethod that takes a PlotSpec JSON string, validates with Pydantic, and returns a Figure ready to render. Also add `Figure.from_dict(d)` for plain dicts (the typical LLM function-call output format).

2. Write tests in `tests/test_json_path.py`: valid round-trip (PlotSpec → JSON → from_json → SVG matches original), missing required fields (clear error), extra fields (ignored gracefully), realistic LLM-generated dict example, malformed types.

3. When done, message the lead with a summary of what was added. The lead will add `bpl.from_json()` and `bpl.from_dict()` re-exports to `__init__.py`.

4. Run tests, lint, format. Commit.

**Files owned**: `botplotlib/figure.py`, new `tests/test_json_path.py`. Do NOT touch `__init__.py`, `compiler/`, `spec/models.py`, `_api.py`, or `render/`.

### Teammate: "refactor-engineer"
**Track 6: Matplotlib refactor polish**
Model: Opus. Starts: Immediately.

The matplotlib refactor module is the marketing hook for external adoption. Polish it.

Tasks:
1. Read the current `botplotlib/refactor/from_matplotlib.py` and its tests. Understand what patterns it handles and what it misses.

2. Test it against realistic matplotlib scripts. Write 3-5 test scripts covering common patterns: basic scatter/line/bar with styling, subplots (should produce a clear error or best-effort), custom colors/markers, title/label/legend configuration, savefig calls.

3. Improve pattern coverage for the most common gaps found in step 2. Focus on the patterns that data scientists actually use (pandas DataFrame.plot(), seaborn-style calls, etc.).

4. Create compelling before/after comparison examples in `examples/refactor_examples/` — showing the matplotlib original and the botplotlib equivalent side by side. These will go in the README eventually.

5. Run tests, lint, format. Commit.

**Files owned**: `botplotlib/refactor/` (all files), new `examples/refactor_examples/` directory, new or updated tests in `tests/` related to refactor. Do NOT touch `compiler/`, `render/`, `_api.py`, `__init__.py`, or `figure.py`.

### Teammate: "research-agent"
**Track 7: TOON + AI-native research**
Model: Sonnet. Starts: Immediately.

Research spike — markdown output only, no code changes.

Tasks:
1. Research TOON (Token-Optimized Object Notation) and evaluate whether PlotSpec should have a TOON serialization, and whether `normalize_data()` should accept TOON-encoded data. Assess the token-efficiency implications for agent workflows.

2. Research marimo and other cyborg-native notebook/visualization projects. Identify patterns botplotlib should learn from or integrate with.

3. Write findings to `research/toon-and-ai-native-ecosystem.md` with concrete recommendations.

**Files owned**: `research/` (new files only). Do NOT touch any code files.

### Teammate: "ci-engineer"
**Track 8: CI governance**
Model: Sonnet. Starts: Immediately.

Build the automated validation infrastructure from the extensibility and stewardship docs. The philosophy is **stress as environment, not punishment** — validation is the wind and rain that makes code resilient, not an adversarial gauntlet.

Tasks:
1. Set up **GitHub Actions CI** in `.github/workflows/ci.yml`: run pytest, ruff, black on every push and PR. This is the basic automated gate.

2. Create a pytest plugin or conftest fixture for **geom stress testing**: given a geom name, automatically run it against edge-case data — empty dataset, single point, NaN values, very large values, negative values, mixed types, 10000 points. Every registered geom should survive these without unhandled exceptions. Consider using Hypothesis for property-based testing where it adds value (invariants like "no NaN coordinates," "all primitives within viewport").

3. Create a **geom protocol structural check**: a test that discovers all registered geoms and verifies each one implements the full protocol (has validate, compile, default_scales with correct signatures). This catches incomplete contributions automatically.

4. Add a visual regression helper: a test utility that renders a geom's test cases to SVG and diffs against golden baselines, with clear failure output showing what changed. (The `--update-baselines` pytest flag already exists; make sure it works cleanly with the new geom architecture.)

5. Run tests, lint, format. Commit.

**Files owned**: `.github/` (new), `tests/conftest.py`, new test utilities in `tests/`. Do NOT touch `compiler/`, `render/`, `_api.py`, `__init__.py`, or `figure.py`.

## What waits for morning

**Track 5: Second wave of geoms.** After the human reviews Track 1 and the protocol is solid, spin up parallel subagents (Sonnet) for area, histogram, heatmap, ridgeline, etc. Each geom is one file, one test file — perfect parallelism.

**Human check.** Charlie tries the waterfall chart. Madeleine makes a plot for Bluesky. Note every friction point.

## Task dependencies

Set these up when creating the task list:
- **renderer-engineer's tasks** are ALL blocked by the lead's Track 1 step 1 (primitive types commit)
- Everything else can start immediately
- The lead should finish step 1 quickly so renderer-engineer isn't waiting long

## Coordination rules

- **Lead implements Track 1 directly** — this is not a coordination-only role.
- **All teammates use worktrees** for filesystem isolation.
- **File ownership is strict.** If a teammate needs a change in another teammate's files, they message that owner. They do NOT edit the file themselves.
- **Every task ends with**: `uv run pytest && uv run ruff check . && uv run black --check .`
- **Commit after each major task.** Atomic commits, descriptive messages.
- **Do NOT push to remote** — just commit locally. The human will review and push.
- When the lead commits primitive types, **message renderer-engineer immediately** to unblock.
- When json-engineer finishes, **message the lead** so re-exports can be added to `__init__.py`.

## Cost management

- **Opus** for correctness-critical work: renderer (must preserve golden baselines), refactor (AST manipulation needs precision)
- **Sonnet** for straightforward implementation: JSON path (wiring), research (reading/writing), CI (configuration)
- Teammates can spawn subagents for focused sub-tasks (test generation, web research)
