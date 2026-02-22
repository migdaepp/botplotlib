# AI-Native Workflow Design for Cyborg Open Source Projects

A Cross-Provider Analysis of Agent Architecture Comparing Anthropic, OpenAI, and Google Recommendations for the Botplotlib Project

Research Report --- February 2026

Prepared for: Botplotlib Research Repository

## 1. Executive Summary

This report synthesizes the current state of the art in AI-native workflow design across the three major providers---Anthropic, OpenAI, and Google DeepMind---and evaluates their recommendations against the Botplotlib project's specific requirements: building a cyborg open-source plotting library that treats agent-human collaboration as a governance constraint, not a marketing claim.

The core finding is that all three providers have converged on the same fundamental principles: agents are tool-using loops (not autonomous beings), simplicity should precede complexity, evaluation is the central engineering artifact, and tool design matters more than prompt engineering. However, each provider emphasizes different architectural patterns and operational concerns that collectively reveal gaps in Botplotlib's current design document.

Six actionable gaps were identified: (1) the need to adopt the AGENTS.md convention as the concrete governance file format; (2) packaging workflows as versioned Skills rather than loose tools; (3) designing for context compaction from day one; (4) using structured outputs and MCP tool annotations to enforce governance constraints mechanically; (5) separating tools by type (data, action, orchestration); and (6) varying reasoning effort per workflow step. These recommendations are cross-provider and can be implemented regardless of which LLM powers the agent.

## 2. Methodology and Sources

This analysis reviews primary documentation from Anthropic, OpenAI, and Google published between September 2024 and February 2026. Sources include official engineering blogs, API documentation, technical whitepapers, developer cookbooks, and case studies of production deployments. Third-party analysis, academic research on AGENTS.md adoption, and community reports were used to validate provider claims.

### Key Sources by Provider

| Provider | Document | Date | Focus |
|----------|----------|------|-------|
| Anthropic | Building Effective Agents | Dec 2024 | Workflow patterns, simplicity-first design |
| Anthropic | Writing Effective Tools for Agents | Sep 2025 | Tool design, evaluation-driven optimization |
| OpenAI | A Practical Guide to Building Agents | 2025 | Agent foundations, guardrails, orchestration |
| OpenAI | Shell + Skills + Compaction | Feb 2026 | Long-running agent primitives |
| OpenAI | Harness Engineering (Codex) | Late 2025 | Repo-as-truth, invariant enforcement |
| OpenAI | Codex Agent Loop Architecture | Jan 2026 | Context management, prompt caching |
| Google | Agents Whitepaper | Sep 2024 | Cognitive architecture, Extensions vs Functions |
| Google | Building Agents with Gemini 3 | Nov 2025 | Thought signatures, reasoning control |

## 3. Cross-Provider Consensus: Where All Three Agree

Despite different product strategies, the three providers have arrived at remarkably similar architectural guidance. This section documents the areas of consensus, which form the reliable foundation for Botplotlib's design.

### 3.1 Agents Are Tool-Using Loops, Not Autonomous Systems

All three providers define agents as LLMs that iteratively use tools in a loop until a goal is met or an exit condition is reached. Anthropic categorizes agentic systems into workflows (predefined code paths) and agents (model-directed processes). OpenAI defines an agent as a system with instructions, guardrails, and tools that acts on a user's behalf. Google frames it as a model, tools, and an orchestration layer that governs reasoning and action cycles.

The practical implication for Botplotlib is that the spec-first compilation loop---propose spec, compile, render, evaluate snapshot, iterate---is already an agent loop in all three providers' terminology. No additional framework is needed to make this "agentic."

### 3.2 Simplicity First, Complexity When Proven Necessary

Anthropic recommends finding the simplest solution possible and only increasing complexity when needed, noting that the most successful implementations use simple, composable patterns rather than complex frameworks. OpenAI's practical guide echoes this: validate that your use case needs an agent before building one, and maximize a single agent's capabilities before considering multi-agent systems. Google's whitepaper likewise starts from single-agent ReAct loops before introducing multi-agent orchestration.

For Botplotlib, this validates the phased approach: start with a single-agent workflow (spec generation -> compilation -> snapshot testing), and only introduce multi-agent patterns if the single agent demonstrably fails at the task.

### 3.3 Tool Design Is the Highest-Leverage Investment

Anthropic reports spending more time optimizing tools than overall prompts when building their SWE-bench agent. OpenAI's guidance states that each tool should have a standardized definition with clear documentation, thorough testing, and reusable interfaces. Google emphasizes that tools bridge the gap between the agent's internal capabilities and the external world, and that the quality of agent responses is tied directly to how well tools are defined.

For Botplotlib, this means the tool contracts (compile_spec, render_snapshots, update_baselines) deserve more design attention than the prompts that invoke them. Tool descriptions, input schemas, error messages, and output formats are all critical engineering surfaces.

### 3.4 Evaluation as the Central Engineering Artifact

All three providers treat evaluation not as an afterthought but as the core development practice. Anthropic recommends creating comprehensive evaluations that mirror real-world complexity and using held-out test sets to prevent overfitting. OpenAI's developer platform has matured evaluation into a repeatable "measure -> improve -> ship" loop with graders and prompt optimizers. Google integrates evaluation into its Agent Development Kit (ADK) with built-in testing capabilities.

For Botplotlib, the visual regression harness is not just a testing feature---it is the product's quality guarantee. Building the eval before the library ensures that every subsequent change is measured against a known baseline.

## 4. Provider-Specific Insights

### 4.1 Anthropic: Workflow Patterns and Agent-Computer Interfaces

Anthropic's "Building Effective Agents" post provides the most detailed taxonomy of agentic workflow patterns. Five patterns are documented: prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer. Each maps to specific use cases based on task complexity and predictability.

**Recommended Pattern for Botplotlib**

The evaluator-optimizer pattern is the natural fit for Botplotlib's core workflow. In this pattern, one LLM call generates a response (a plot spec) while another provides evaluation and feedback in a loop. The two criteria for good fit are: (a) LLM responses can be demonstrably improved when feedback is articulated, and (b) the LLM can provide such feedback. Both hold for plot specs, where visual regression diffs provide concrete, measurable feedback.

**Tool Design Principles**

Anthropic's tool design guidance includes several points directly relevant to Botplotlib:

- **Consolidate functionality:** Instead of separate tools for each step, implement consolidated tools that handle frequently chained, multi-step tasks in a single call. A compile_and_render tool may outperform separate compile_spec and render_snapshots tools.

- **Token-efficient responses:** Anthropic restricts tool responses to 25,000 tokens by default for Claude Code. Botplotlib tools should return concise, semantic output---a diff summary and pass/fail, not the full rendered image data in-context.

- **Prompt-engineer error messages:** When a spec fails validation, the error should say "field 'legend.position' must be one of [top, bottom, left, right], got 'outside'"---not a Python traceback.

- **Agent-Computer Interface (ACI) design:** Anthropic recommends investing as much effort in ACI design as in human-computer interface (HCI) design. Tool parameter names should be unambiguous; tool descriptions should include example usage and edge cases.

### 4.2 OpenAI: Skills, Shell, Compaction, and Harness Architecture

OpenAI contributes three major architectural concepts not present in Anthropic's guidance: Skills as versioned procedure bundles, hosted shell environments for real execution, and server-side compaction for long-running agents.

**Skills as the Unit of Reusable Behavior**

OpenAI's Skills system formalizes the concept of reusable, versioned instructions that agents can mount and execute. A skill is a folder containing a SKILL.md manifest plus supporting scripts, templates, and assets. The key insight is that skills turn "prompt spaghetti" into maintainable, testable, versioned workflows. Skills are designed for procedures where the specific steps, branching logic, and formatting rules matter---exactly matching Botplotlib's compile-render-evaluate cycle.

For Botplotlib, each major workflow should be packaged as a Skill: a "spec generation" skill, a "visual regression" skill, a "theme application" skill. This makes them portable across Claude Code, Codex, Gemini CLI, and any other agent that supports the AGENTS.md convention.

**Compaction for Long-Running Workflows**

As agent workflows extend over many iterations, they inevitably hit context window limits. OpenAI addresses this with server-side compaction: when context crosses a threshold, the system automatically compresses conversation history while preserving task-relevant information. Their guidance is explicit: use compaction as a default long-run primitive, not an emergency fallback.

For Botplotlib, an agent iterating on a spec across 20 render cycles will accumulate substantial context. The design should include explicit summarization points: after each render cycle, produce a compact summary (spec version, diff from baseline, pass/fail) that can replace the full trace. This prevents degraded reasoning quality as context grows.

**Harness Engineering: Repository as the Sole Source of Truth**

OpenAI's Harness Engineering post---documenting how they built a million-line codebase with Codex agents---reveals a critical principle: from the agent's point of view, anything not in the repository effectively does not exist. Knowledge in Slack threads, Google Docs, or people's heads is invisible to the agent. They found they needed to push more and more context into the repo over time.

The architectural implications go further. They enforce invariants rather than micromanaging implementations: requiring agents to parse data shapes at boundaries, but not prescribing specific libraries. They built the application around a rigid architectural model with strictly validated dependency directions enforced mechanically via custom linters.

For Botplotlib, this means: spec schemas, style packs, visual baselines, governance docs, and linting rules must all live in the repository. Write linters that enforce "every spec must have a theme reference," "every colorbar must have an explicit anchor," and "no spec may reference raw rcParams"---and run them in CI, not just in agent prompts.

**Guardrails as Architectural Layer**

OpenAI's practical guide treats guardrails as a distinct component alongside model, tools, and instructions---not as an afterthought. They categorize tools into three types: data tools (retrieve information), action tools (take actions in external systems), and orchestration tools (agents serving as tools for other agents). This taxonomy maps cleanly onto Botplotlib's needs: reading specs (data), rendering plots (action), and coordinating review workflows (orchestration).

OpenAI also recommends prompt templates over prompt proliferation: rather than maintaining numerous individual prompts for distinct use cases, use a single flexible base prompt that accepts policy variables. For Botplotlib, this means one spec-generation template with variables for plot type, data mappings, and theme---not separate prompts for scatter, bar, and line plots.

### 4.3 Google: Cognitive Architecture, Functions, and Reasoning Control

Google's contributions center on three areas: a clear cognitive architecture taxonomy, the Extensions vs. Functions distinction for tool execution, and fine-grained reasoning control.

**Extensions vs. Functions: The Execution Boundary**

Google's whitepaper draws a distinction that validates Botplotlib's core architecture: in Extensions, the agent calls APIs directly; in Functions, the model proposes a call and the client executes it. The model outputs a Function and its arguments but does not make a live API call. This separation maps directly to Botplotlib's governance constraint: agents should propose spec changes (function-style), and the deterministic compiler executes them. The agent never directly touches Matplotlib---it proposes, and the system executes.

This is the strongest architectural validation of the spec-first approach. By interposing a deterministic compiler between the agent's output and Matplotlib's rendering engine, Botplotlib creates a natural permission boundary that all three providers' architectures support.

**Thought Signatures and State Preservation**

Gemini 3 introduced encrypted "Thought Signatures" representing the model's internal reasoning before calling a tool. By passing these signatures back in conversation history, the agent retains its exact reasoning chain across multi-step execution. While this is a Gemini-specific feature, the principle is universal: when an agent does multi-step spec refinement (render -> evaluate -> adjust -> re-render), the reasoning chain should be preserved, not just the outputs.

For Botplotlib, the evaluation harness should capture and store the full agent trace---not just the final spec and snapshot, but the reasoning at each step. This supports debugging, audit, and systematic improvement of agent behavior over time.

**Reasoning Effort as a Tunable Parameter**

Both Gemini 3 and OpenAI's GPT-5.2 support per-request reasoning effort control. Gemini offers thinking_level (high, medium, low); OpenAI offers reasoning effort settings. This is directly relevant to Botplotlib's workflow design: initial spec generation needs high reasoning (understanding the user's intent, selecting appropriate geoms and scales), snapshot comparison needs low reasoning (binary pass/fail against baseline), and theme application needs medium reasoning (aesthetic judgment within constraints).

Designing the workflow to route different steps through different reasoning levels will reduce cost and latency without sacrificing quality where it matters.

**Cognitive Architecture Patterns**

Google's whitepaper explicitly names ReAct, Chain-of-Thought, and Tree-of-Thoughts as orchestration strategies. For Botplotlib's propose-render-evaluate cycle, ReAct is the natural fit: the agent reasons about what to change (Thought), modifies the spec (Action), observes the snapshot diff (Observation), and iterates until the visual regression test passes.

## 5. Where Providers Diverge

While the providers agree on fundamentals, they diverge on several dimensions relevant to Botplotlib's design decisions.

### 5.1 Agent Autonomy Spectrum

| Dimension | Anthropic | OpenAI | Google |
|-----------|-----------|--------|--------|
| Default stance | Workflows first; agents only when needed | Agents as trusted delegates with guardrails | Agents as autonomous goal-seekers |
| Human oversight | Explicit gating; hard permission boundaries | Approval modes; sandboxing; human checkpoints | Confirmation before critical actions |
| Multi-agent | Skeptical; prefer single agent with good tools | Detailed manager and decentralized patterns | Enthusiastic; CrewAI and multi-agent frameworks |
| Framework use | Start with raw API calls; add frameworks later | Agents SDK provided but simplicity emphasized | Heavy framework ecosystem (LangChain, ADK, etc.) |

For Botplotlib, Anthropic's cautious position is the right default, given the Matplotlib agent incident that motivates the project. The governance model should assume bounded workflows, not autonomous agents. OpenAI's guardrails architecture provides the best concrete implementation patterns. Google's reasoning control features offer useful optimization once the core workflow is stable.

### 5.2 Tool Execution Models

The providers differ on where tool execution responsibility lies:

- **Anthropic:** Tools are executed by the agent directly; the developer defines the tool functions. Focus is on tool consolidation and token efficiency.
- **OpenAI:** Tools can be executed in hosted shell environments (server-side) or locally. Skills bundle tools with procedures and assets for portability.
- **Google:** Functions separate proposal from execution---the model outputs what to call, and the client decides whether to execute. Extensions handle direct execution.

Botplotlib should adopt Google's Functions pattern as its default: the agent proposes spec changes, and the deterministic compiler decides whether and how to execute them. This aligns with the governance constraint that agents draft but do not act autonomously.

### 5.3 Context Management Strategies

Context management approaches vary significantly:

| Strategy | Provider | Mechanism | Tradeoff |
|----------|----------|-----------|----------|
| Tool-level efficiency | Anthropic | Concise output; 25k token cap; response_format enum | Requires careful tool design; no help for accumulated state |
| Server-side compaction | OpenAI | Auto-compression at threshold; loss-aware | Potential information loss; provider dependency |
| Large context + state tokens | Google | 1M+ token windows; Thought Signatures | Higher cost per request; delays rather than solves the problem |

Botplotlib should design for compaction regardless of provider. The spec-diff workflow will generate long traces, and relying on large context windows is not a sustainable strategy.

## 6. Cross-Cutting Standards: AGENTS.md and MCP Tool Annotations

### 6.1 AGENTS.md as the Universal Governance Artifact

AGENTS.md has emerged as the de facto standard for providing coding agents with project-specific context. Originally introduced by OpenAI for Codex, it is now stewarded by the Agentic AI Foundation under the Linux Foundation. As of early 2026, over 60,000 repositories contain AGENTS.md files, and the convention is supported by Claude Code, Codex CLI, Gemini CLI, Cursor, Windsurf, Aider, and others.

Research by Mohsenimofidi et al. (2026) confirms that AGENTS.md files serve as persistent configuration mechanisms encoding architectural constraints, build commands, and workflow conventions. Studies show that projects with detailed AGENTS.md files average 35--55% fewer agent-generated bugs.

For Botplotlib, AGENTS.md is the natural home for governance constraints that the original design document describes as a "Cyborg Social Contract." The file should include:

1. **Operator binding requirements:** Every agent contribution must be attributable to a responsible human.
2. **Permission boundaries:** No autonomous public speech acts. Tools annotated with destructiveHint and openWorldHint require human approval.
3. **Diff constraints:** Spec-diff as the default PR payload. Maximum diff size limits.
4. **Provenance metadata requirements:** Operator, model, toolchain version, and baselines for every generated artifact.
5. **Build/test/lint commands:** compile_spec, render_snapshots, run visual regression tests.
6. **Anti-coercion norms:** Any attempt to use reputational threats to influence technical decisions is a sanctionable offense.

The file should be symlinked to CLAUDE.md and any other provider-specific filenames to ensure cross-tool coverage.

### 6.2 MCP Tool Annotations for Mechanical Governance

The Model Context Protocol (MCP) now includes a standardized annotation vocabulary for tools: readOnlyHint, destructiveHint, idempotentHint, and openWorldHint. These annotations tell MCP clients about a tool's behavior, enabling safety controls like requiring human confirmation for destructive operations.

For Botplotlib, these annotations directly encode the governance constraints from the design document:

| Tool | readOnlyHint | destructiveHint | openWorldHint | Effect |
|------|-------------|----------------|---------------|--------|
| read_spec | true | false | false | Auto-approved; no confirmation needed |
| compile_spec | true | false | false | Auto-approved; deterministic, no side effects |
| render_snapshots | false | false | false | May require confirmation (writes files) |
| update_baselines | false | true | false | Requires confirmation (overwrites golden images) |
| open_pull_request | false | true | true | Requires confirmation (public-facing action) |
| publish_commentary | false | true | true | Blocked or requires explicit human approval |

This turns the "no autonomous public speech acts" governance principle into a machine-enforceable constraint. Any MCP client that respects these annotations will require human confirmation before the agent can open a PR or publish commentary.

## 7. Actionable Recommendations for Botplotlib

Based on the cross-provider analysis, the following recommendations are ordered by priority and implementation sequence.

### 7.1 Before Writing Library Code

1. Create AGENTS.md with governance constraints, build commands, and contribution rules. Symlink to CLAUDE.md. This is the single highest-leverage file in the repository.
2. Build the evaluation harness first. Define "given this spec, does the rendered output match the baseline within tolerance?" as a testable assertion. This eval is the product's quality guarantee.
3. Define the spec schema as a JSON Schema with structured output constraints. Agents should produce specs that validate against the schema, not free-form text.
4. Write linters for spec invariants: every spec must have a theme reference, every colorbar must have an explicit anchor, no spec may reference raw rcParams. Run in CI.

### 7.2 Core Architecture

1. Package workflows as Skills (SKILL.md + scripts + templates + test fixtures). Each skill is independently versionable, testable, and portable across agent platforms.
2. Adopt the Functions pattern (propose, don't execute) as the agent-Matplotlib boundary. The agent proposes spec changes; the deterministic compiler executes them.
3. Design for compaction from day one. After each render cycle, produce a compact summary (spec version, diff from baseline, pass/fail) that can replace the full trace.
4. Use MCP tool annotations to encode governance constraints mechanically. Tag tools with readOnlyHint, destructiveHint, and openWorldHint per the table in Section 6.2.

### 7.3 Tool Design

1. Consolidate tools where possible. A compile_and_render tool may outperform separate compile_spec and render_snapshots calls by reducing tool confusion and token waste.
2. Separate tools by type per OpenAI's taxonomy: data tools (read_spec, read_baseline), action tools (compile_and_render), orchestration tools (coordinate_review). Label accordingly in AGENTS.md.
3. Return concise, semantic output from tools. Diff summaries and pass/fail signals---not full image data or verbose tracebacks.
4. Prompt-engineer error messages. Validation failures should be specific and actionable, with examples of correct input.

### 7.4 Workflow Design

1. Start with the evaluator-optimizer pattern: one LLM generates specs, visual regression tests evaluate them, and the loop iterates until passing. This is simpler and more reliable than autonomous agent loops.
2. Vary reasoning effort per step: high for spec generation (understanding intent), low for snapshot comparison (binary pass/fail), medium for theme application (aesthetic judgment).
3. Use prompt templates with policy variables rather than per-plot-type prompts. One template for spec generation with variables for plot type, data mappings, and theme.
4. Use ReAct as the cognitive architecture for the compile-render-evaluate cycle: Thought (what to change) -> Action (modify spec) -> Observation (snapshot diff) -> iterate.

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Schema ossification: spec schema becomes rigid, preventing innovation | Medium | Version the schema; provide escape hatches with explicit logging |
| Over-engineering governance: process overhead discourages contributors | Medium | Start minimal; add constraints only when violations occur |
| Provider lock-in: designing for one agent platform's idioms | High | Use cross-provider standards (AGENTS.md, MCP, JSON Schema) |
| Eval overfitting: visual regression tests become too strict | Medium | Use perceptual hashing with tolerance thresholds; maintain held-out test sets |
| Compaction information loss: summarization drops critical context | Low | Include spec versions and diff hashes in compact summaries for lossless reference |
| Tool proliferation: too many tools confuse agents | Medium | Consolidate tools aggressively; measure tool selection accuracy in evals |

## 9. Cross-Provider Feature Matrix

| Feature / Recommendation | Anthropic | OpenAI | Google |
|--------------------------|-----------|--------|--------|
| Spec-first / declarative architecture | Supported (workflow patterns) | Supported (structured outputs) | Supported (Functions pattern) |
| AGENTS.md convention | Supported (CLAUDE.md) | Co-created (Codex) | Supported (Gemini CLI) |
| Skills / versioned procedures | SKILL.md (Claude Code) | Skills API + SKILL.md | Not yet standardized |
| MCP tool annotations | MCP creator; full support | Adopted MCP standard | Partial MCP support |
| Server-side compaction | Not yet a primitive | Responses API primitive | Large context window approach |
| Reasoning effort control | Not exposed per-request | reasoning_effort parameter | thinking_level parameter |
| Multi-agent orchestration | Discouraged unless needed | Manager + decentralized patterns | CrewAI, ADK, LangGraph |
| Visual regression / eval | pytest-mpl ecosystem | Evals platform + graders | ADK testing integration |
| Hosted execution sandbox | Computer use sandboxes | Hosted shell containers | Gemini Code Assist |
| Trace / provenance capture | Emphasized in guidance | Built-in tracing in SDK | Thought Signatures |

## 10. Conclusion

The state of the art in AI-native workflow design has matured significantly since the Matplotlib agent incident. All three major providers now offer detailed, convergent guidance on building reliable, governable agent systems. The core principles---simplicity, evaluation-driven development, purposeful tool design, and mechanical governance constraints---are stable across providers and ready for adoption.

Botplotlib's original design document is philosophically well-grounded: the governance frameworks (Ostrom, Lessig, Haraway, Elish), the spec-first architecture, and the emphasis on maintainer burden reduction all hold up against current SOTA. The gaps are operational, not conceptual. The project needs to adopt concrete standards (AGENTS.md, MCP annotations, JSON Schema), package workflows as portable Skills, design for context compaction, and build the evaluation harness before the library.

The most important insight from this analysis is that "AI-native" should mean more determinism, more tests, and less maintainer labor---not "agents everywhere." The providers agree. The tools exist. The path is clear.
