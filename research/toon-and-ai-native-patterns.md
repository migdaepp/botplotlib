# TOON Format and AI-Native Workflow Patterns

> Research spike for botplotlib. Track 7. February 2026.

---

## Summary

This document examines three external areas of inquiry: (1) TOON format, a token-efficient alternative to JSON designed for LLM prompts; (2) marimo, a reactive Python notebook built for the AI-native era; and (3) a broader scan of design patterns from other cyborg-native tools. The goal is to identify concrete ideas botplotlib should adopt, adapt, or reject.

Bottom line: TOON is not a good fit for botplotlib's primary use cases, though a narrow application exists for portable artifact mode. marimo's design is highly relevant — several of its patterns validate what botplotlib is already doing and one (structured tool exposure via MCP) is worth adopting directly. The broader landscape confirms that botplotlib's proposal/execution split is aligned with the direction the field is moving.

---

## 1. TOON Format

### What it is

**Token-Oriented Object Notation (TOON)** is a compact, human-readable serialization format designed specifically for LLM input. It targets the same data model as JSON — objects, arrays, primitives — but restructures the encoding to eliminate the repetition that makes JSON expensive inside LLM context windows.

The core mechanism: for uniform arrays of objects, TOON declares column names once as a header and then provides values as comma-separated rows, combining YAML-style indentation for nesting with CSV-style compression for tabular data.

**Example.** A record array that in JSON reads:

```json
{
  "hikes": [
    {"id": 1, "name": "Blue Lake Trail", "distanceKm": 7.5, "elevationGain": 320},
    {"id": 2, "name": "Ridge Overlook", "distanceKm": 9.2, "elevationGain": 540},
    {"id": 3, "name": "Wildflower Loop", "distanceKm": 5.1, "elevationGain": 180}
  ]
}
```

becomes in TOON:

```
hikes[3]{id,name,distanceKm,elevationGain}:
  1,Blue Lake Trail,7.5,320
  2,Ridge Overlook,9.2,540
  3,Wildflower Loop,5.1,180
```

Nested config objects use YAML-style indentation. The format is lossless and round-trips deterministically to/from JSON.

### Token efficiency claims

Published benchmarks from the TOON repository (4 LLMs, 209 retrieval questions):

| Format | Accuracy | Avg tokens | Efficiency (acc%/1K tokens) |
|---|---|---|---|
| TOON | 73.9% | 2,744 | 26.9 |
| JSON (compact) | 70.7% | 3,081 | 22.9 |
| JSON (pretty) | 69.7% | ~4,500 | ~15.3 |

For large uniform arrays, TOON achieves 30–62% token reduction over equivalent JSON. A 500-row e-commerce order dataset: 4,617 tokens (TOON) vs 11,842 tokens (JSON) — a 61% reduction.

These gains are real for large, structurally uniform arrays. They diminish quickly for deeply nested or schema-irregular data.

### Applicability to botplotlib

botplotlib's LLM interactions fall into three distinct modes, and TOON's fit differs across them:

**Mode 1 — Python API generation (the dominant mode for Claude Code / Codex)**

An LLM generates a Python call like:

```python
bpl.scatter(df, x="year", y="temp", color="region", title="Temperature Trend", theme="substack")
```

This is approximately 35–45 tokens. Data is already in a Python variable (`df`) — it never enters the token stream. TOON is not relevant here. This mode is where botplotlib's token efficiency advantage is greatest: a matplotlib-equivalent is 100–150 tokens; botplotlib is 35–45 tokens.

**Mode 2 — PlotSpec JSON exchange (agent-to-agent spec passing)**

An agent generates or exchanges a PlotSpec JSON without embedded data. The spec alone — layers, labels, legend, size, theme — is 30–60 tokens in compact JSON. This is already extremely compact. TOON would offer no meaningful improvement.

**Mode 3 — Portable artifact mode (spec with embedded data)**

When a PlotSpec includes inline data — for true portability, diff-ability, or transmission between agents that don't share a data environment — the data section dominates the token count. botplotlib's columnar DataSpec (`data.columns: {col_name: [values...]}`) is already a reasonably compact form, but JSON still incurs overhead from repeated brackets and numeric formatting.

Empirical estimates for a 3-column scatter plot:

| Rows | Compact JSON | Hypothetical TOON | Reduction |
|---|---|---|---|
| 5 | 268 chars (~67 tokens) | ~220 chars (~55 tokens) | ~18% |
| 25 | 628 chars (~157 tokens) | ~520 chars (~130 tokens) | ~17% |
| 100 | 1,978 chars (~494 tokens) | ~1,560 chars (~390 tokens) | ~21% |
| 500 | 9,178 chars (~2,294 tokens) | ~7,100 chars (~1,775 tokens) | ~23% |

The savings grow with row count but plateau around 20–25% for columnar data (because botplotlib's DataSpec is already columnar — the JSON key overhead is `"col_name":` once per column, not once per row). This is meaningfully less than TOON's headline 40–62% figure, which applies to row-oriented JSON where every key repeats.

### Trade-offs and constraints

**Against TOON adoption:**

1. **LLM familiarity.** All major LLMs are trained extensively on JSON. TOON requires prompt-level instruction before an LLM can generate it reliably. This adds complexity and context tokens, partially eroding the savings.

2. **Tooling ecosystem.** JSON has parsers in every language; TOON has TypeScript SDK only (as of the benchmark publication). Adding a Python parser to botplotlib would require maintaining a non-trivial dependency or rolling our own.

3. **The wrong bottleneck.** For botplotlib's primary use cases, data is never in the token stream — it's in a DataFrame variable. TOON savings only appear in Mode 3 (portable artifact with embedded data), which is the least common interaction pattern.

4. **botplotlib's columnar format already helps.** DataSpec stores data columnar (`{col: [values]}`), not row-oriented (`[{col: val, ...}]`). This means the "key repetition" problem that TOON most aggressively addresses is already partially solved.

5. **Complexity is a token cost too.** If a spec format is harder to generate correctly, an LLM needs more reasoning tokens to get it right. TOON's syntax is clean, but any deviation from JSON adds a new failure mode.

**For TOON adoption:**

1. The portable artifact use case (Mode 3) is real. When Charlie sends a PlotSpec to Madeleine across systems that don't share data context, or when a spec is archived in a repo with embedded data, TOON encoding of the `data.columns` section would reduce file size by ~20%.

2. TOON's token efficiency compounds with context size. At 500+ rows embedded in a spec, 500 fewer tokens is non-trivial if the LLM must reason about the data.

### Recommendation

**Do not add TOON as a primary serialization format.** The complexity cost is not justified for botplotlib's dominant use cases (Modes 1 and 2), where data is already out of the token stream.

**Consider a narrow opt-in for Mode 3.** A `spec.to_toon()` method (or a `bpl.dump_toon(spec)` utility) could be offered for users who explicitly want compact portable artifacts with embedded data. This would be clearly documented as an optimization for the archive/transmission use case, not as the default. Implementation would be ~100 lines of Python; no external dependency needed if we hand-roll the encoder (TOON's grammar is simple).

**The more important token efficiency work is already done.** botplotlib's Python API is 35–45 tokens for a complete plot. matplotlib is 100–150 tokens. That 3–4x gap is far more impactful than the 20% savings TOON might offer on the data section of a portable spec.

---

## 2. marimo

### What it is

**marimo** is a reactive Python notebook designed from the ground up for reproducibility, shareability, and AI-native workflows. It is described as "the first AI-native notebook environment." Its creators identify four fundamental problems with Jupyter notebooks that informed its redesign:

1. **Hidden state** — cell execution order creates implicit state that is impossible to audit
2. **JSON format** — `.ipynb` files are JSON with base64 blobs, hostile to version control and LLM generation
3. **No reactivity** — running one cell does not update dependent cells; users run cells manually and out of sync
4. **No structure** — a notebook is a REPL, not a program; there is no reliable execution order

### Design principles

**Notebooks as dataflow graphs.** marimo represents a notebook as a directed acyclic graph (DAG) where edges are variable dependencies, not cell positions. Running a cell automatically re-executes all downstream cells. Deleting a cell scrubs its variables from memory. The graph is built from static analysis of variable definitions and references — not from runtime tracing.

Two simple constraints make the whole system work: no cycles between cells, no variable redefinitions across cells. These constraints seem restrictive but eliminate hidden state entirely.

**Stored as pure Python files.** marimo notebooks are `.py` files, not JSON blobs. Every cell is a function decorated with `@app.cell`. This makes them:
- Fully git-diff-able
- Importable as modules
- Runnable as scripts via topological sort
- Deployable as web apps without modification

**Three modes from one representation.** The same dataflow graph runs as:
- An interactive reactive notebook
- An executable script (cells topologically sorted, run sequentially)
- A web application (cells become UI components; no callbacks needed)

**AI integration through structure.** The `--mcp` flag turns any marimo notebook into an MCP server, exposing read-only tools for AI systems:
- `get_active_notebooks` — enumerate running notebooks
- `get_cell_runtime_data` — inspect cell outputs, execution time, error state
- `get_tables_and_variables` — expose the data environment (DataFrames, scalars, etc.)
- `get_notebook_errors` — surface compilation and runtime errors

A critical architectural detail: marimo uses a "snapshot-based synchronization" pattern. Each MCP call gets a consistent snapshot of the notebook state without freezing the reactive engine. This is a clean solution to the concurrency problem of exposing a live reactive system to external tool consumers.

**LLM context injection.** marimo passes runtime variable state to AI assistants during code generation. When an LLM is asked to write a cell, it knows what DataFrames are in memory, what columns they have, and what errors are present. This is the same principle as botplotlib's "accept any data format" — the system handles context; the LLM handles intent.

### What botplotlib already does right (validated by marimo's approach)

marimo's design choices independently validate several botplotlib principles:

1. **Proposal/execution split.** marimo separates "what the notebook describes" (the dataflow graph, defined by pure Python functions) from "how it executes" (the reactive engine). botplotlib separates PlotSpec (the proposal) from the compiler (the deterministic executor). Both designs keep the LLM's job focused on declaration, not execution mechanics.

2. **Pure-Python-as-IR.** marimo stores notebooks as `.py` files because Python is a better interchange format than JSON blobs with binary payloads. botplotlib's PlotSpec is JSON-serializable Pydantic — a structured format that is diffable, versionable, and directly generatable by LLMs. Both projects make the same bet: structured, diff-able representations outperform opaque blobs.

3. **Structural constraints enable guarantees.** marimo's "no cycles, no redefinitions" constraints seem restrictive but unlock reproducibility guarantees. botplotlib's Pydantic model and WCAG structural gates seem restrictive but guarantee accessibility and layout correctness. Constraints are design features, not limitations.

4. **Agent integration via tools, not prompts.** marimo's MCP integration exposes tools with "clear schemas that AI systems can understand," not free-form text interfaces. botplotlib's tool classification (read-only data tools, action tools, orchestration tools) follows the same philosophy.

### What botplotlib should learn from marimo

**MCP server exposure.** marimo demonstrates that exposing a library's runtime state through MCP is a clean pattern for AI-native integration. botplotlib could expose an MCP interface that allows Claude Code or other agents to:
- Inspect the current PlotSpec being built
- Query what themes are available and their contrast properties
- Check what geoms are registered (once the geom registry exists)
- Get compiler error messages in structured form

This is a natural extension of the "PlotSpec as portable artifact" principle: if the spec can be generated by any agent, the agent should be able to inspect the compilation pipeline's current state.

**Snapshot-based tool exposure.** The marimo pattern of "consistent snapshot per tool call, without freezing the underlying engine" is directly applicable to a botplotlib MCP server. When an agent calls `get_compiled_plot`, it should get a snapshot of the current compiled geometry — not trigger a new compilation.

**Documentation stored as executable structure.** botplotlib's tutorial is a marimo notebook (`tutorial.py`). marimo's own documentation is written as marimo notebooks. The lesson: executable documentation is better documentation. When the tutorial breaks (because a renderer API changed), the notebook fails to run. The breakage is structural and immediately visible. This is the same instinct that drives botplotlib's golden SVG baseline tests.

### What to avoid

**Reactive execution for plotting.** marimo's cell reactivity is powerful for exploratory analysis but would add unnecessary complexity to botplotlib's pipeline. The PlotSpec is already declarative — there is nothing to react to. The compiler is deterministic. Adding reactivity to botplotlib would be solving a problem that the proposal/execution split already solves.

**Notebook-first design.** marimo is optimized for interactive exploration. botplotlib is optimized for programmatic generation by agents. These are complementary, not competing — botplotlib should remain library-first and let marimo (and Jupyter, and other environments) handle the interactive notebook layer.

---

## 3. Other Cyborg-Native Projects

### Vega-Lite: the declarative visualization precedent

**Vega-Lite** is the closest prior art to botplotlib's PlotSpec. It defines visualizations as JSON grammars (mark, encoding, transform, config) that compile deterministically into rendered output. Its design principles are directly aligned with botplotlib's:

- Declarative specification separates intent from implementation
- A compiler handles layout, scale inference, and rendering
- The spec is a portable artifact, diffable and versionable

Vega-Lite demonstrates that JSON-native visualization APIs can be both expressive and concise enough for LLM generation. However, recent research shows LLMs struggle to generate correct Vega-Lite more than they struggle with matplotlib Python: "Gemini [was] rendered almost useless for creating charts via Vega-Lite scripts." This is instructive for botplotlib. The gap between Vega-Lite (spec-first) and matplotlib (imperative Python) in LLM generation quality suggests that a Python-first API with spec-as-IR is the right design: LLMs generate Python; the system produces the spec.

This is exactly what botplotlib does — and it confirms that the "two paths in" architecture (Python API for humans+LLMs, JSON spec for agent-to-agent) is the right one.

### Observable Plot: conciseness-first

**Observable Plot** is a JavaScript visualization library that prioritizes API conciseness. A scatter plot is:

```javascript
Plot.dot(penguins, {x: "culmen_length_mm", y: "culmen_depth_mm", stroke: "species"}).plot()
```

Plot's design philosophy is "one mark, one line." It achieves this by aggressive use of defaults and inference — scales are inferred from data types, axes are automatic, legends are auto-generated. This maps closely to botplotlib's "beautiful defaults" principle: the first render should usually be the final render.

Observable Plot does not have a declarative JSON spec as an intermediate representation; it is purely imperative. This makes it harder to use in agent-to-agent workflows. botplotlib's PlotSpec addresses this gap.

### dbt: SQL as a portable, diffable artifact

**dbt** (data build tool) is a useful analogy for PlotSpec's role in botplotlib. dbt transforms SQL into a system of modular, version-controlled, testable data transformations. The SQL model is the "spec"; the dbt runner is the "compiler"; the materialized data is the "rendered output."

dbt's design choices that botplotlib has independently replicated:
- The artifact (SQL / PlotSpec) is the source of truth
- The executor is deterministic and enforces structural rules
- Version control is a first-class affordance
- Tests are part of the model, not an afterthought

The lesson: declarative, portable artifacts that are diffable, versionable, and machine-generatable are a recurring pattern across cyborg-native tools. botplotlib is in good company.

### Dagster: proposal/execution in data pipelines

**Dagster** is a data orchestration platform built around the "software-defined asset" concept: you declare what data assets should exist (the proposal) and Dagster manages the execution of the transformations that create them (the executor). Its "declarative automation" feature decides when to trigger runs based on asset dependency state, not on imperative scheduling code.

The structural parallel to botplotlib is direct: PlotSpec = software-defined asset declaration; compiler = Dagster asset materialization; SVG output = the materialized asset. Both systems keep the LLM (or the human) focused on declaration and let the deterministic executor handle timing, ordering, and validation.

### marimo's MCP pattern: a broader signal

The most important pattern emerging across the field is the one marimo exemplifies: **expose structured tool schemas over MCP rather than free-form API documentation.** When a system exposes itself as an MCP server with typed tools, AI agents can discover, compose, and use those tools without reading prose documentation. The schema is the documentation.

This pattern is appearing across the ecosystem:
- marimo: `--mcp` flag exposes notebook inspection tools
- Dagster: planning to expose asset graph tools via structured APIs
- VS Code: MCP support for IDE state inspection
- Claude Code: MCP-native by design

botplotlib should treat MCP-server exposure as a first-class deliverable alongside its Python API, not as an optional integration. The geom registry (when it exists) should be MCP-queryable. The compiler error surface should be MCP-readable. The theme system should be MCP-inspectable.

---

## Consolidated Recommendations

### 1. Do not adopt TOON as default serialization

**Rationale:** botplotlib's primary token efficiency gains come from the Python API being 35–45 tokens vs matplotlib's 100–150 tokens. TOON's 20–25% reduction on the data section of portable specs is real but secondary. The complexity cost of teaching LLMs a new format, maintaining a non-standard parser, and managing the "when to use TOON vs JSON" decision surface outweighs the benefit.

**What to do instead:** Keep PlotSpec JSON as the canonical serialization. Ensure `model_dump_json()` produces compact (not pretty-printed) output by default. The columnar DataSpec already provides a mild form of key-deduplication.

### 2. Optional: add `to_toon()` for portable artifact mode (low priority)

**Rationale:** There is a legitimate use case for compact portable specs — archiving a plot as a self-contained artifact that includes data, storing specs in a repo, or transmitting between agents that don't share a data environment. For 100+ rows of data, TOON would reduce the data section by ~20%.

**What to do:** A `bpl.dump_toon(spec)` function that encodes the columnar DataSpec as TOON arrays and the spec fields as YAML-style key-values. Roughly 100 lines of Python, no dependencies. Clearly scoped as an optimization utility, not a primary format. Parser (`bpl.load_toon(toon_str)`) required alongside encoder.

**Priority:** Low. Build the geom registry and MCP server first.

### 3. Expose botplotlib as an MCP server (medium priority)

**Rationale:** marimo demonstrates this pattern cleanly. An MCP server that exposes botplotlib's state enables AI agents to inspect the compilation pipeline, query available themes/geoms, and get structured error feedback. This is the natural extension of the "PlotSpec as portable artifact" principle.

**Concrete tools to expose:**

```
read_spec(spec_id)          → PlotSpec JSON               [readOnlyHint: true]
list_themes()               → list of theme names + descriptions [readOnlyHint: true]
list_geoms()                → list of registered geoms + schemas [readOnlyHint: true]
compile_spec(spec)          → CompileResult (errors | compiled geometry summary) [readOnlyHint: false]
get_contrast_report(spec)   → WCAG contrast check results  [readOnlyHint: true]
```

Use marimo's snapshot-based synchronization pattern: each MCP call gets a consistent, stable response. No reactive state threading.

**Priority:** Medium. Natural after the geom registry exists.

### 4. Validate and document the "two paths in" architecture

**Rationale:** Research on LLM visualization generation confirms that LLMs generate Python more reliably than JSON visualization grammars (Vega-Lite, etc.). botplotlib's "Python API for humans and LLMs; JSON spec for agent-to-agent" is the correct design. AGENTS.md already describes this architecture; it should be explicitly framed as a response to the empirical finding that LLMs struggle with spec-first formats like Vega-Lite.

**What to do:** Add a note to AGENTS.md's "Why AI-Native?" section citing the empirical challenge LLMs face with Vega-Lite, and explicitly grounding the "two paths in" architecture in this finding.

### 5. Learn from marimo's executable documentation pattern

**Rationale:** botplotlib already has a marimo tutorial (`tutorial.py`). marimo demonstrates that executable documentation is structurally superior to prose documentation — when the library changes, the tutorial breaks in a visible, structural way. This is the same principle as golden SVG baseline tests.

**What to do:** Extend the tutorial to cover the geom extension pattern (once it exists), theme customization, and the MCP interface. Keep it as a marimo notebook. Consider adding a CI step that runs `marimo export html tutorial.py` to verify the tutorial executes without error on every commit.

### 6. Note for the future: TOON as a data input format

**Rationale:** `normalize_data()` currently accepts dict, list[dict], Polars, Pandas, Arrow, and generators. TOON is designed as a data serialization format, not a data container format, so direct ingestion would require parsing. However, if an agent wants to pass data in TOON format (because it received data from a TOON source), botplotlib should accept it.

**What to do:** This would be Step 8 in the dispatch order of `normalize_data()`: detect a string input that begins with TOON syntax, parse it, and continue. This is a one-function change. Do not implement until there is a concrete user request for it.

---

## Token Efficiency Analysis: PlotSpec vs. Alternatives

For reference, measured token estimates for producing a 25-row scatter plot across interaction modes:

| Approach | Tokens to generate the plot | Notes |
|---|---|---|
| botplotlib Python API (Mode 1) | ~35–45 | Data in a Python variable; LLM writes one line |
| botplotlib PlotSpec JSON (Mode 2) | ~40–60 | No data embedded; LLM writes spec JSON |
| matplotlib Python equivalent | ~120–150 | LLM writes imperative styling code |
| Vega-Lite JSON equivalent | ~80–120 | JSON spec; LLMs often generate incorrect syntax |
| botplotlib PlotSpec + data (Mode 3) | ~150–500 | Depends on row count; data embedded |
| botplotlib PlotSpec + data, TOON (Mode 3) | ~120–400 | ~20% reduction on data section |

The biggest single efficiency gain in the botplotlib ecosystem is the Python API relative to matplotlib — a 3–4x reduction. TOON addresses the smallest part of the problem (data section of portable specs). Continued investment in the Python API, good defaults, and the MCP interface will have more impact than TOON adoption.

---

## References

- TOON format repository: https://github.com/toon-format/toon
- TOON vs JSON benchmarks: https://www.tensorlake.ai/blog/toon-vs-json
- TOON token reduction analysis: https://blog.logrocket.com/reduce-tokens-with-toon/
- Towards AI: TOON token economy analysis: https://towardsai.net/p/machine-learning/toon-vs-json-deconstructing-the-token-economy-of-data-serialization-in-large-language-model-architectures
- marimo documentation: https://docs.marimo.io/
- marimo: Python notebooks as dataflow graphs: https://marimo.io/blog/dataflow
- marimo: Turning notebooks into AI-accessible systems: https://marimo.io/blog/beyond-chatbots
- VegaChat: LLM-Based Chart Generation: https://arxiv.org/html/2601.15385
- Are LLMs ready for Visualization?: https://arxiv.org/html/2403.06158v1
- Vega-Lite grammar of graphics: https://vega.github.io/vega-lite/
- Observable Plot: https://github.com/observablehq/plot
- Dagster declarative automation: https://dagster.io/
