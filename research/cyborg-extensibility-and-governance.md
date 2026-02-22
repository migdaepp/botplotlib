# Cyborg Extensibility and Governance

> How botplotlib should grow: making it easy for cyborg teams to add the plots they need, without human bottlenecks or architectural collapse.

## The Problem

The power of ggplot2 comes from its open-source ecosystem. People added `geom_sankey()`, `facet_wrap()`, and hundreds of other geoms as they needed them. The library grew organically because the extension mechanism was well-documented and the pattern was copyable.

botplotlib needs the same property: when Charlie needs a waterfall chart, his agent should be able to build one in a session and contribute it back. When a climate scientist needs a ridgeline plot, same thing. The library should expand as people use it.

But the traditional open-source model — submit a PR, wait for a human maintainer to review it — is a bottleneck that doesn't scale in a cyborg world. We need governance and extensibility mechanisms that work when the contributors are human+AI teams and the volume of contributions is potentially very high.

This document synthesizes ideas from conversations across multiple agents and humans, anchored in how Wikipedia actually works and in ecological models of community health.

## Architecture: Core Primitives + Macros

### The core compiler must be small and stable

The compiler should not know what a scatter plot, a sankey diagram, or a waterfall chart *is*. It should know how to render geometric primitives: `Rect`, `Line`, `Circle`, `Text`, `Path`, `Polyline`. These are the atoms. Everything else is a molecule.

**Current state:** The compiler (`compiler.py`) has hardcoded handlers for `scatter`, `line`, and `bar`. The `LayerSpec.geom` field is `Literal["scatter", "line", "bar"]`. The renderer (`svg_renderer.py`) similarly iterates over `compiled.points`, `compiled.lines`, `compiled.bars` as separate lists.

**Target state:** The compiler dispatches to a registered geom handler. Each geom is a function (or class) that takes `(layer, data, scales, layout, theme)` and returns a list of positioned geometric primitives. The renderer doesn't need to know about specific geom types — it just renders primitives.

### What is a Macro?

A **Macro** is a pure, deterministic translation function that maps data + intent into geometric primitives. A waterfall chart is mathematically just a sequence of floating `Rect` elements with computed baselines and connecting `Line` segments. A Sankey diagram is a set of `Path` elements with computed control points.

The Macro pattern means:
- New plot types don't require changes to the compiler core
- Each Macro is self-contained: one file, one geom, testable in isolation
- A cyborg team can add a new plot type in a single session
- The PlotSpec vocabulary grows (`geom: "waterfall"`) without the core changing

### The Geom Protocol

Every geom implements the same contract:

```
validate(layer, data) → None or raise
    Check that the data has the required columns, types, etc.

compile(layer, data, scales, theme, plot_area) → list[Primitive]
    Transform data into positioned geometric primitives.

default_scales(layer, data) → dict
    Declare what kind of scales this geom needs (linear y, categorical x, etc.)
```

This is the equivalent of ggplot2's `Geom` class. The contract is small enough that an agent can implement a new geom by copying an existing one and modifying the `compile()` method.

### Recipe for adding a new geom

This is the step-by-step that any Claude Code / Codex / Gemini session can follow:

1. Create `botplotlib/geoms/waterfall.py` (or whatever the geom is)
2. Implement `validate()`, `compile()`, and `default_scales()`
3. Register the geom name in the geom registry
4. Add `bpl.waterfall()` convenience function in `_api.py` (thin factory, ~10 lines)
5. Write tests with golden SVG baselines
6. Submit as a single atomic PR

The recipe must be documented in AGENTS.md so agents can find it. The pattern must be copyable — look at an existing geom, change the math, done.

## Governance: Learning from Wikipedia

Wikipedia is the most successful large-scale collaborative system in history. It works not because of good vibes but because of pragmatic institutional design: automated bots, strict schemas, and incentive structures that align individual needs with collective utility. The relevant mechanisms:

### Stigmergy: the Red Link pattern

Wikipedia doesn't have a central committee assigning articles. It uses **stigmergy** — indirect coordination through the environment. A "red link" (a link to a page that doesn't exist) signals exactly where the system needs work. Contributors find red links and fill them.

**For botplotlib:** When someone asks for a "waterfall chart" and no geom exists, the system should make this visible. Options:
- Log the missing geom request (with data schema and intent) to a public registry or issue tracker
- The agent can attempt a one-off rendering using raw primitives, then offer to formalize it as a proper geom
- Other cyborg teams browsing "most-wanted geoms" can pick up the work

This is coordination without a coordinator.

### Asymmetric friction: easy to contribute, cheap to revert

Wikipedia thrives because it's easier to fix a mistake than to vandalize the site. They optimized for the "undo" button, not for the "approval" button. The insight: **don't gate contributions on human approval; gate them on automated validation, and make rollback trivial.**

**For botplotlib:** New geom contributions should be validated by CI, not by a human maintainer reading every line:

- **Structural validation:** Does the geom implement the protocol? Do `validate()`, `compile()`, and `default_scales()` exist and have correct signatures?
- **Data stress testing:** Run the geom against edge cases — empty data, NaN values, single data points, extreme ranges, negative values. This isn't adversarial; it's the wind and rain that makes trees stronger. If the geom breaks, the CI provides descriptive error logs so the authoring agent can fix and resubmit.
- **Visual regression:** Render the geom's test cases and store golden baselines. Future changes are diffed against them.
- **Accessibility gate:** WCAG contrast checks apply to all geoms equally — this is a structural property of the compiler, not something individual geoms opt into.

If a contribution passes all automated gates, it can be merged without a human in the loop. If it breaks later (a downstream change causes a regression), rollback is a single revert commit.

### Strict schemas as consistency enforcement

Wikipedia enforces visual consistency across millions of pages using Templates and Infoboxes with strict parameter constraints. You can't invent a new layout for a city page; you must pass data into `Template:Infobox settlement`.

**For botplotlib:** This is already the architecture. The PlotSpec is the Infobox. The compiler is the rendering engine. No matter how novel a geom is, its output must be expressed as geometric primitives that the renderer already knows how to draw. This guarantees that themes, accessibility, and layout rules apply uniformly. A community-contributed Sankey diagram will automatically respect the user's chosen theme, WCAG contrast requirements, and collision avoidance — because those are properties of the compiler, not of individual geoms.

### Reputation through use, not through maintainer approval

Wikipedia articles gain prominence through incoming links and usage. Reliability is an emergent property, not an assigned label.

**For botplotlib:** When the geom ecosystem grows, users (and their agents) need to know which contributions are reliable. The mechanism: **telemetry as reputation.**

- When an agent pulls a geom and successfully compiles a plot, it can send a lightweight success signal back to the registry
- When a geom fails on real-world data, that's also logged
- Over time, robust geoms accumulate successful execution traces; fragile ones accumulate error traces
- An agent choosing between multiple implementations of the same chart type defaults to the one with the highest success rate for that data shape

Reputation is emergent and computed, not granted by a human authority.

## Community Health: Ecological Maintenance

A healthy ecosystem needs mechanisms for growth, maintenance, and graceful decay. Without these, the registry becomes a swamp of abandoned code. Note that this section draws on ideas from Robin Wall Kimmerer (braiding sweetgrass), micro

Because language creates reality, framing our architecture around "zero-trust" and adversarial arenas breeds a fortress mentality that stifles open-source joy and collaboration. To build a thriving, pro-community ecosystem, we must shift from defense to symbiosis. To do this we draw on ideas from mycorrhizal networks and Robin Wall Kimmerer (braiding sweetgrass), research on gift economies and commons management (elinor ostrom), and theoretical and empirical work on Wikipedia and online community (nancy baym).

### Composting

If a geom goes unused — zero execution pings, no updates, consistently bypassed in favor of a better fork — it should be **composted**: gracefully archived out of the active registry. Not deleted (the git history preserves it), but removed from the active search space so agents and users find the living, maintained geoms first.

Concrete rule of thumb: geoms with zero usage in 90 days and no maintainer activity get moved to an `archive/` directory with a note explaining why, and removed from the active geom registry.

### Immune response without fortress mentality

Bad actors will eventually show up. The response should be proportional and localized, not system-wide lockdown.

If a node in the network submits obfuscated code, embeds malicious payloads, or floods the registry with low-quality spam, the response is **isolation**: sever connections to that contributor, flag their submissions for manual review, and let the rest of the community continue operating on high-trust defaults.

The goal: a system where the default is open and frictionless, and the security response is localized to the specific threat. The communitarian majority should never have to adopt high-friction workflows because of a minority of bad actors.

## Aspirational: The Decentralized Registry

Long-term, the geom ecosystem doesn't need to live in one monolithic repo. Imagine:

- A user asks for a Sankey diagram
- Their agent searches a public geom registry
- If a high-reputation Sankey geom exists, it pulls it down and applies it
- If none exists, the agent synthesizes one locally, uses it, and — if the user is happy — publishes it back to the registry

The library expands in real time as users encounter new needs. The registry is the mycorrhizal network: nutrients (geoms) flow to where they're needed, trust builds through use, and the system self-organizes without central planning.
