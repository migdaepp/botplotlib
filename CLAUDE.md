# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. However this is meant to be an interoperable repo so the source of truth is [AGENTS.md](AGENTS.md) -- make sure you read it at the start of each session. Claude.md should be kept as simple as possible with agents.md as the main source of truth.

## Project Overview

**botplotlib** is a Python library (MIT licensed) that produces beautiful plots with a simple, AI-native API. No matplotlib dependency. See [AGENTS.md](AGENTS.md) for full architecture, data protocol, and contributor guide.

## Repository

- GitHub: https://github.com/migdaepp/botplotlib
- License: MIT

## Build / Test / Lint

```bash
uv run pytest                           # all tests
uv run pytest tests/test_foo.py::test_name  # single test
uv run pytest --update-baselines        # regenerate golden SVGs
uv run ruff check .                     # lint
uv run black --check .                  # format check
cd docs && uv run --group docs mkdocs serve   # docs dev server
```

## AI-Native Design Principles

All development decisions should be evaluated against these principles (detailed rationale in AGENTS.md, research context in `research/agent-architecture.pdf`):

1. **Token efficiency** — minimize the tokens needed to produce a correct plot. Fewer tokens = fewer failure points for LLMs.
2. **Proposal / execution split** — PlotSpec is a declarative proposal; the compiler is a deterministic executor. LLMs should never reason about pixels, font metrics, or contrast ratios.
3. **Structural quality gates** — WCAG contrast checks are compiler errors, not warnings. Accessibility is enforced by the system, not by review.
4. **Beautiful defaults** — themes must produce publication-ready output with zero configuration. Visual iteration is possible but expensive; good defaults mean the first render is usually final.
5. **Accept any data format** — `normalize_data()` handles the common cases so agents don't have to convert.
6. **PlotSpec as portable artifact** — the spec is JSON-serializable, agent-exchangeable, diffable, and versionable.
7. **Refactor as paradigm bridge** — `from_matplotlib.py` translates imperative code into declarative specs.

## Claude-Specific Guidance

- When modifying plot output, always run visual regression tests
- Use `uv run` for all commands (the project uses uv for dependency management)
- The data input protocol in AGENTS.md is authoritative — follow the exact dispatch order
- Error messages should be specific and actionable (e.g., "field 'legend.position' must be one of [top, bottom, left, right], got 'outside'")
- WCAG contrast checks are structural gates (errors, not warnings)
