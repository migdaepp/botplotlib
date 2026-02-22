# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
```

## Architecture

Spec → Compile → Render pipeline. See AGENTS.md for the full module map and data input protocol.

- **Spec layer** (`botplotlib/spec/`): Pydantic models (PlotSpec, LayerSpec, ThemeSpec)
- **Compiler** (`botplotlib/compiler/`): resolves scales, ticks, layout, accessibility checks
- **Renderer** (`botplotlib/render/`): SVG builder and renderer, optional PNG via CairoSVG

## Claude-Specific Guidance

- When modifying plot output, always run visual regression tests
- Use `uv run` for all commands (the project uses uv for dependency management)
- The data input protocol in AGENTS.md is authoritative — follow the exact dispatch order
- Error messages should be specific and actionable (e.g., "field 'legend.position' must be one of [top, bottom, left, right], got 'outside'")
- WCAG contrast checks are structural gates (errors, not warnings)
