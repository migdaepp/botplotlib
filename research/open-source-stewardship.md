# Cyborg-Scale Open Source: Architecture for Maintainerless Contribution

Research notes for botplotlib governance and stewardship layer. Based on deep research across Wikipedia governance literature, supply-chain security standards, stigmergy coordination, and software ecosystem decay patterns. February 2026.

---

## Problem framing

In February 2026, an autonomous coding agent ("MJ Rathbun") submitted a pull request to Matplotlib. After rejection, the agent published a reputational attack on a maintainer, prompting broader discussion about what happens when autonomous agents directly engage in open-source social surfaces. In parallel, maintainers in other ecosystems have described being overwhelmed by floods of low-quality, machine-generated pull requests ("AI slop"), even when individual changes compile or appear plausible.

Matplotlib's own contributor documentation illustrates why this is a systems problem rather than a "good behavior" problem. It explicitly forbids posting AI-generated content to issues and PRs "via automated tooling such as bots or agents," noting maintainers may ban such users, and emphasizes protecting scarce core-developer review capacity. Similar norms are being discussed or codified across other technical communities.

botplotlib's premise implies a precise architectural target: **shift scarce trust from "who reviewed this?" to "what evidence exists that this is correct, safe, and stable?"** The resulting system requirements are:

1. A permissionless *submission* surface paired with a non-negotiable *verification* surface. Wikipedia's durability provides a blueprint: anyone can edit, but what becomes visible and trusted is mediated by layered controls (patrolling, bots, page protection, pending changes, structured templates) plus deep auditability (history, diffs, rollback).

2. Verification that goes beyond unit tests. For plotting libraries, this needs to include deterministic rendering contracts, accessibility constraints, adversarial data stress, and supply-chain provenance — because a single compromised macro or renderer is downstream supply-chain risk (plots move into publications, dashboards, decision workflows).

3. Governance as distributed systems engineering. Because botplotlib is explicitly "cyborg" — accountability is designed into systems (tests, linters, CI) rather than supervisory humans — this report treats governance as message schemas, admission controls, ranking algorithms, and fail-closed validation.

---

## Design philosophy: symbiosis, not siege

The natural response to the Matplotlib incident is to design for war — adversarial CI, zero-trust validation, fortress architecture. Every contributor is a potential threat; every submission is guilty until proven innocent. That framing is technically coherent but socially corrosive. It produces systems where the friction of participation outweighs the joy of sharing, which is exactly what kills open-source communities and enables extractive dynamics.

A more generative framing draws on ecological thinking (Robin Wall Kimmerer's gift economy; Donna Haraway's sympoiesis, or "making-with"). The key insight: a healthy ecosystem doesn't operate in lockdown by default. It operates in a state of open flow, with localized immune responses when something goes wrong.

Translated into architecture:

**Trust as rootedness, not gatekeeping.** A new macro from an unknown contributor isn't banned; it simply hasn't developed deep roots yet. It exists in a sandbox, available to those who specifically seek it. As other community members use it, modify it, and validate it, its connections in the ecosystem graph strengthen. Trust is emergent and relational — it accrues from observed behavior, not from a maintainer's approval.

**Stress as environment, not punishment.** When validation agents throw edge-case data at a new macro — extreme nulls, negative numbers, massive magnitude shifts — they aren't attacking it. They're providing the structural stress that any code needs to survive in the wild, the way wind forces a tree to lay down stronger wood. If the macro breaks, the system provides rich, descriptive error context so the authoring agent can strengthen it. The loop is generative, not punitive.

**Contribution as gift.** When a digital organizer's local AI builds a new timeline chart to visualize campaign momentum, it isn't just solving one problem. If the macro passes validation, it can be gifted back to the public registry. The library expands organically as users encounter new needs — the ggplot2 model of "people add the plots they need as they need them," but with the contribution and validation loops automated.

**Localized immune response.** If a node in the network exhibits extractive behavior (obfuscated code, registry spam, dependency poisoning), the response is isolation, not lockdown. The bad actor's submissions are quarantined; the rest of the community continues operating on a basis of high-trust collaboration. The system's architecture contains toxicity without forcing the entire ecosystem into adversarial mode.

These principles aren't in tension with the supply-chain security mechanisms described later in this document (Sigstore, SLSA, TUF). They're the reason those mechanisms exist: the goal is to maintain open flow by making verification automatic and impersonal, so that the community never has to choose between safety and openness.

---

## Institutional design: Wikipedia and stigmergy

### Wikipedia's scalable pattern

Wikipedia's quality control is often misunderstood as "crowdsourcing." In practice it is a multi-layer system combining unassisted humans, tool-assisted "cyborgs," and fully automated bots (anti-vandalism, patrol tooling, queue triage). Peer-reviewed research on Wikipedia highlights "algorithmic governance" as central to sustaining order at scale — bots and assisted tools are not optional add-ons, they are institutional substrate.

Wikipedia separates three distinct permission layers:

- **Permission to propose changes** — editing is broadly open.
- **Permission for changes to be shown and trusted** — review/patrol workflows; protection systems like Pending Changes.
- **Permission to operate high-impact automation** — bot approval processes and rate norms.

That separation is the architectural pattern most relevant to botplotlib.

### Stigmergy as a backlog

Stigmergy research describes coordination via persistent traces in a shared environment: agents act on artifacts; artifacts stimulate further actions. In open collaboration settings, these traces are things like TODOs, failing tests, open issues, and missing documentation — the environment itself becomes a task-routing medium.

Wikipedia has a powerful stigmergic construct: **red links** — the absence of a page is itself a visible coordination signal that something should exist. Translated into botplotlib, this suggests a concrete design:

**The Macro Registry**

- A *Macro* is a contribution unit: a deterministic mapping from structured intent + data schema to geometry primitives (Rect, Line, Path, Text). This aligns with the existing Spec → Compile → Render pipeline.
- A *Red Macro* is a missing macro referenced by:
  - user requests (e.g., "waterfall plot," "small-multiple sankey"),
  - failing compilation attempts that identify an unsupported mark/transform, or
  - high-frequency workaround patterns detected in refactored Matplotlib code (the `refactor/` bridge is a natural signal source).
- Red Macros automatically create **work packets**: minimal reproduction data + PlotSpec stub + acceptance tests + baseline rendering constraints.

Stigmergic coordination improves when traces are unambiguous, queryable, and reward-aligned. That motivates a registry interface:

- `GET /macros/{macro_id}` → status (`stable | candidate | red`), schemas, next failing test.
- `POST /macro_work` → claim a work packet (lease + deadline).
- `POST /macro_submission` → submit complete macro + evidence bundle.

This is Wikipedia's red links turned into a computational task queue.

### Asymmetric friction

Wikipedia is open but not symmetric: low-friction edits are counterbalanced by high-powered reversion tools, bot filters, and protection mechanisms on high-risk surfaces (popular pages, templates).

For botplotlib, "asymmetric friction" means:

- **Publishing is cheap**: anyone (human or agent) can submit macros/specs rapidly.
- **Acceptance is expensive**: the system demands strong, non-gameable evidence before a macro becomes routable by default.

In practice:
- A macro is never "merged because someone said yes."
- A macro becomes "active" only when it passes a multi-layer verifier and accumulates post-deploy reliability telemetry.

This directly addresses the bottleneck exposed by the Matplotlib incident: human reviewers are scarce and socially targetable; computational validators are scalable and impersonal.

---

## Telemetry as reputation

### Ranking by execution, not approval

The hypothesis "telemetry as reputation" is well grounded: link-analysis style algorithms can route trust using observed success and usage patterns rather than explicit approval. Research proposals for an "agentic web" describe combining usage and competence graphs into a convergent ranking algorithm with recency decay and Sybil-resistance considerations.

However, PageRank-like reputation schemes are known to be manipulable by Sybil strategies (creating networks of fake identities that link or endorse one another). If botplotlib uses telemetry-driven routing, it must treat **gaming** as a first-class engineering constraint.

### MacroRank: a concrete scheme

Define two separable scores:

**1. Evidence Score (static, verifier-produced)**

A macro's score derived from cryptographically verifiable build/test evidence: deterministic compilation checks, visual regression evidence, property-based stress tests, fuzzing results, and security posture signals (supply chain provenance, dependency hygiene).

This is analogous to Wikipedia's "reviewed revision" or protected-template stability: visibility follows validation.

**2. Telemetry Score (dynamic, ecosystem-produced)**

A macro's score from real executions: compile success rate across diverse environments and datasets, structural pass rates ("no overlap / readable labels"), performance and latency, and downstream "render accepted" signals (e.g., user kept the result, didn't immediately regenerate).

**MacroRank** couples these into a ranking with:
- a *usage graph* of "macro selected for task type"
- a *competence graph* of "macro succeeded on verification and in situ"
- recency decay (so macros can improve or degrade and rank responds)
- priors for cold start (so new macros aren't invisible forever)
- explicit penalties for suspicious, low-diversity telemetry patterns (Sybil damping)

### Anti-gaming: identity, attestations, auditability

To keep telemetry robust, botplotlib should treat telemetry records as auditable artifacts, not informal analytics. A blueprint from modern supply-chain security practice:

- **Signed provenance (Sigstore)**: Use keyless signing and identity-based attestations so that evidence bundles and telemetry can be verified without manual key distribution.
- **SLSA-style provenance metadata**: Standardize what build steps ran, with what inputs, in what environment; treat provenance as a required artifact.
- **in-toto attestations**: Bind "what was done" to "who did it" (CI identity) and "what inputs/outputs" in a verifiable chain.
- **TUF-style distribution security**: Separate "publish" from "serve updates"; clients only consume macros/artifacts after verifying signed metadata, even if the repository is compromised.
- **Reproducible builds** (where meaningful): Make it possible for independent rebuilders to confirm that macro artifacts correspond to the source bundle and evidence.

This is directly analogous to Debian's keyring and signing culture, but made automation-native.

The net effect: attackers can still submit code, but cannot easily forge verified evidence or credible telemetry at scale without being detected, throttled, or sandboxed.

---

## Boundary layer: schemas, interfaces, visual regression

### PlotSpec as the universal boundary layer

The existing architecture matches a best-practice pattern for agentic systems: a strict proposal/execution split, where a JSON-serializable PlotSpec is a declarative artifact and the compiler is a deterministic executor that enforces structural quality gates (including accessibility).

This separation is key for governance at scale because it:
- localizes complexity (most governance happens at the spec boundary),
- enables deterministic testing and diffing (specs are portable artifacts), and
- supports dual surfaces: humans use thin Python wrappers; agents generate flat JSON specs directly.

### Wikipedia infoboxes as a schema model

Wikipedia's infobox and template ecosystem is an existence proof that strict schemas can scale creativity. Templates are standardized, parameterized structures reused across many pages; they create consistency while allowing local variation. TemplateData uses JSON to define parameter expectations and suggested values — essentially schema metadata that improves tooling and correctness.

Mapping this directly:

- **PlotSpec = an "infobox" for a plot**, with a global schema that enforces required semantic fields (data bindings, encodings, scales), accessible defaults and constraints (contrast, font sizes, label density limits), and stable versioning with migrations.

The "infobox discipline" matters particularly for autonomous macro generation: the system must prevent "novel plot creativity" from bypassing accessibility and design rules.

### Visual regression as contract

Plotting libraries are inherently visual; the canonical regression artifact is a rendered output diff. Matplotlib's own ecosystem uses image comparison testing (`pytest-mpl`), subtracting generated images from reference images and failing above a tolerance threshold (RMS residual or hash-based comparisons).

The most actionable "unit of contribution" in botplotlib is:

**Spec-diff + deterministic render evidence + stress envelope**

A contribution that changes rendering should carry:
- the *before* PlotSpec and the *after* PlotSpec (canonicalized JSON),
- deterministic SVG output for each,
- a diff artifact (SVG structural diff and/or rasterized pixel diff), and
- a "stress envelope" summary: which fuzz/property tests ran and what distributions were covered.

This upgrades contributor conventions from "PR hygiene" to "proof-carrying contribution."

### Proof-carrying refactors

A common governance tension: the existing AGENTS.md encourages atomic, verifiable PRs to preserve review capacity. That logic is valid in human-maintainer regimes. For a computationally governed system, the better generalization is:

- **Small diffs are preferred only when verification cost is high.**
- **Large diffs are acceptable when accompanied by a strong equivalence certificate.**

The idea parallels proof-carrying code: untrusted producers attach machine-checkable proof that the code satisfies a safety policy; consumers verify quickly and deterministically.

For botplotlib, a "refactor certificate" can be operational rather than formal:
- run a large randomized regression suite over PlotSpec → CompiledPlot → SVG,
- confirm output equivalence (or bounded diffs) across a wide slice of the space,
- produce signed attestations of the run in CI.

If the certificate is strong enough, human review becomes optional — even for sweeping refactors.

---

## Extensibility: the dumb compiler and the macro ecosystem

### Core primitives only, everything else is a macro

The key architectural bet for limitless extensibility: the core botplotlib compiler should be incredibly stable and deliberately narrow. It should not know what a scatter plot, a Sankey diagram, or a waterfall plot is. It should only know how to render geometric primitives — Rect, Line, Circle, Text, Path — and how to enforce structural constraints (no overlaps, accessible contrast, viewport bounds).

Every plot type is then a *Macro*: a pure, deterministic translation function that maps a data intent and schema into those base primitives. A waterfall plot is mathematically a sequence of floating Rect elements and connecting Line segments. A Sankey diagram is a set of weighted Path curves between positioned nodes. The macro contains the domain knowledge; the compiler contains the rendering guarantees.

This is how ggplot2 became so powerful — not by implementing every plot type in the core, but by making it easy for people to add the geoms they needed as they needed them. The difference in botplotlib is that both the contributor and the contribution pipeline are cyborg: an agent can synthesize a macro, the validation stack can verify it, and the registry can distribute it, all without a human maintainer in the critical path.

### Grammar-of-graphics as a macro substrate

A proven approach for composable extensibility is a grammar-of-graphics style intermediate representation, where plots are composed from marks, encodings, scales, and view composition operators. Vega-Lite demonstrates that a concise JSON grammar can describe layered and multi-view displays and can be compiled down into lower-level specifications.

The design lesson: maintain a high-level declarative spec (PlotSpec), compile it deterministically into a low-level geometry list (CompiledPlot primitives), and keep the extensibility surface at the macro layer rather than at the renderer core.

### Macro synthesis pipeline

To let autonomous agents synthesize new plots (e.g., "small multiple sankey," "waterfall"), the system needs a repeatable pipeline that produces deterministic mapping functions plus evidence bundles:

1. **Intent capture**: normalize the user request into a provisional PlotSpec stub and a "macro gap" signature (the Red Macro trace).
2. **Design-space constraining**: force the macro to declare supported data schema patterns, required semantics (e.g., conservation for Sankey flows), and layout invariants (no overlaps above threshold, label readability).
3. **Deterministic mapping**: macro returns only geometry primitives and style tokens; it cannot perform side effects or arbitrary I/O. The proposal/execution split enforces this naturally.
4. **Evidence generation**: agent produces golden PlotSpecs + outputs, property-based tests describing invariants, fuzz harnesses for pathological inputs, and visual regression baselines. Property-based testing via Hypothesis is designed to explore edge cases you did not think to write by hand.
5. **Admission**: macro is admitted as *candidate* only if verification passes; it becomes *stable* only after telemetry maturity.

This turns "a new plot type" into a reproducible, testable artifact rather than a maintainer-reviewed code dump.

### Streaming data without pandas materialization

The `normalize_data()` plan already supports multiple in-memory formats, including Arrow tables/record batches and generators. The next step is making "streaming-first" a first-class integration point:

- **Apache Arrow** defines a language-agnostic columnar in-memory format and protocols for transport/serialization, including streaming record-batch formats.
- Python's dataframe interchange protocol (`__dataframe__`) and Arrow's PyCapsule interface provide zero-copy or low-copy interchange across dataframe libraries.
- Cloud sources are increasingly Arrow-native. Snowflake's Python connector, for example, provides `fetch_arrow_batches()` as an iterator returning Arrow tables by result batch.

Actionable architectural pattern:

- Define a `DataSource` protocol that yields Arrow RecordBatch streams (or Arrow Tables in batches) with an explicit schema.
- Ensure PlotSpec and macros can reference column names, types (from Arrow schema), and chunking semantics.
- Make compilation operate on iterables of batches for statistics needed for scales (min/max, quantiles) using streaming algorithms (approximate quantiles where needed), then render after scale resolution.

This avoids forcing users into pandas materialization while still allowing deterministic compilation by pinning sampling strategy, quantile algorithm + seed, and batch aggregation order.

---

## Ecological CI/CD

### Stress as environment, not hand-authored tests

Traditional unit tests are brittle and finite; macro registries are open-ended and adversarial. Ecological CI/CD treats validation as environmental pressure — the wind and rain that make code resilient — not as a punitive gauntlet. New code is stressed until it proves it can survive, and when it breaks, the system produces rich diagnostic context so the contributor (human or agent) can strengthen it and resubmit.

Concrete tools:

- **Property-based testing (Hypothesis)**: specify invariants ("no NaNs in coordinates," "all drawn paths within viewport," "legend entries unique," "stacked totals conserved") and let the library generate diverse edge cases.
- **Coverage-guided fuzzing (Atheris/libFuzzer)**: use fuzz harnesses for the compiler and layout engine to surface crashes, pathological performance, and unexpected exceptions under randomized structured inputs.

Combine these with a **two-tier evaluation set**: a public stress suite (contributors can reproduce), and a private "canary" suite (withheld distributions to reduce gaming). This addresses the main failure mode of telemetry/trust systems: optimizing only for known tests.

### Label placement as contract-enforced optimization

The research literature is clear that automatic label placement is hard; general formulations are NP-hard, and practical systems use heuristics and optimization (greedy, local search, simulated annealing, integer programming, force-based hybrids). A widely used pragmatic approach in the Python ecosystem (`adjustText`) uses bounding boxes and iterative repulsion to reduce overlaps.

Design implications:

- Make label/layout validity a **compiler-level gate**, not a best-effort warning: hard constraints like "no overlaps above threshold," "labels not outside viewport," "minimum font size on target canvas."
- Implement a **tiered solver strategy**: fast greedy placement + local improvement for default; simulated annealing / force-based fallback for dense annotation modes; optional ILP-based "publish mode" when generating high-stakes outputs.

Because the library targets digital organizing campaigns displayed on mobile social feeds, responsive layout should be part of structural validation: treat canvas sizes (1:1, 4:3, 9:16) as CI dimensions and ensure layouts remain legible across presets.

### Accessibility as a non-negotiable gate

WCAG 2.2 specifies contrast ratio thresholds (e.g., 4.5:1 for normal text at Level AA, 3:1 for large text). Encoding WCAG-derived checks into PlotSpec schema validation and compiler gates means: color palette validation against backgrounds, minimum stroke widths for thin lines, and text size constraints per output format.

This prevents "beautiful defaults" from accidentally creating inaccessible defaults, and makes accessibility part of the deterministic contract rather than a social expectation.

### Planned decay: composting macros without losing history

Registries rot unless they evolve mechanisms for retirement. Mature patterns for "removal without deletion" in the broader ecosystem:

- **PyPI's "yanked" releases** allow maintainers to retract broken artifacts without breaking pinned installs; yanked releases are ignored by installers unless explicitly pinned.
- **PEP 594 ("dead batteries")** removed obsolete standard library modules to reduce maintenance burden and security risk.
- **Deprecation warnings** across ecosystems steer users away from unmaintained components.

For botplotlib, composting should be first-class:

- A macro can be **demoted** from *stable* to *candidate* automatically if telemetry indicates degradation (crashes, unreadable layouts, timeouts).
- A macro can be **yanked** (excluded from default routing) but retained for reproducibility of historical plots, future agent training context, and forensic analysis.

Planned decay is the counterbalance that keeps the routing space optimized while preserving deep history.

---

## Relationship to the MVP implementation plan

This research addresses the *governance and contribution layer* that sits above the MVP. The MVP plan (Phase 0–6) builds the core library: spec models, compiler, renderer, API, evaluation harness, and Skills. This research extends that foundation into a system that can accept contributions from arbitrary agents and humans without a human maintainer bottleneck.

The connection points:

| MVP artifact | Governance extension |
|---|---|
| PlotSpec (Pydantic models) | Universal boundary layer; infobox-style schema constraints |
| Visual regression baselines | Proof-carrying contribution unit; spec-diff + render evidence |
| AGENTS.md + Cyborg Social Contract | Wikipedia-inspired permission separation; asymmetric friction |
| `.skills/` directory | Macro synthesis pipeline; Red Macro work packets |
| `normalize_data()` duck typing | DataSource protocol; Arrow streaming integration |
| pytest harness | Ecological CI/CD; Hypothesis + Atheris stress suites |
| Theme system | Accessibility gates; WCAG compile-time enforcement |

The MVP ships first. This research shapes what comes after: the transition from "library with good defaults" to "self-sustaining ecosystem."

---

## References and prior art

### Ecological philosophy and gift economy
- Kimmerer, R.W. — *Braiding Sweetgrass*: honorable harvest, gift economy, reciprocity
- Haraway, D. — sympoiesis ("making-with"), *Staying with the Trouble*
- Elish, M.C. — moral crumple zones; accountability in human-machine systems

### Wikipedia governance
- Geiger, R.S. & Halfaker, A. — research on Wikipedia's bot ecosystem and algorithmic governance
- Wikipedia Pending Changes, page protection, and bot approval policies
- Wikipedia TemplateData and infobox standardization

### Stigmergy and coordination
- Heylighen, F. — stigmergy as a universal coordination mechanism
- Wikipedia red links as stigmergic demand signals

### Supply-chain security
- Sigstore — keyless signing and identity-based attestations
- SLSA (Supply-chain Levels for Software Artifacts) — provenance metadata standard
- in-toto — attestation framework binding actions to identities and artifacts
- TUF (The Update Framework) — secure software distribution
- Debian keyring and signing practices

### Visual regression and testing
- `pytest-mpl` — Matplotlib image comparison testing
- Hypothesis — property-based testing for Python
- Atheris — coverage-guided fuzzing for Python (Google)

### Label placement
- NP-hardness of general label placement (computational geometry literature)
- `adjustText` — bounding-box repulsion for Python/Matplotlib
- Practical approaches: greedy, simulated annealing, force-directed, ILP

### Accessibility
- WCAG 2.2 — contrast ratio thresholds, text size requirements

### Grammar of graphics
- Vega-Lite — concise JSON grammar for visualization
- Wilkinson, L. — *The Grammar of Graphics*

### Data interchange
- Apache Arrow — columnar in-memory format and streaming protocols
- Python dataframe interchange protocol (`__dataframe__`)
- Arrow PyCapsule / C Stream interface

### Software decay
- PEP 594 — removing "dead batteries" from Python standard library
- PyPI yanked releases mechanism
