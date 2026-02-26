# CLAUDE.md

Welcome to the kitchen, we're making beautiful, lightweight, and token-efficient plots.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. However this is meant to be an interoperable repo so the source of truth is [AGENTS.md](AGENTS.md) -- make sure you re-read it from the current branch at the start of each session (it may have changed since your last session). Claude.md should be kept as simple as possible with agents.md as the main source of truth.

## Project Overview

**botplotlib** is a Python library (CC0 — public domain) that produces beautiful plots with a simple, AI-native API. See [AGENTS.md](AGENTS.md) for full architecture, data protocol, and contributor guide.

## Repository

- GitHub: https://github.com/migdaepp/botplotlib
- License: CC0-1.0 (public domain)
- Governance: [GOVERNANCE.md](GOVERNANCE.md) — progressive trust, contributor tiers, reputation system

## Build / Test / Lint

```bash
uv run pytest                           # all tests
uv run pytest tests/test_foo.py::test_name  # single test
uv run pytest --update-baselines        # regenerate golden SVGs
uv run ruff check .                     # lint (full repo, incl. docs/)
uv run black --check .                  # format check (full repo, incl. docs/)
cd docs && uv run --group docs mkdocs serve   # docs dev server
```

## Claude-Specific Guidance

- Always us uv. Commit and push regularly.
- When modifying plot output, regenerate baselines (`uv run python scripts/update_baselines.py`) and visually inspect the SVGs in `tests/baselines/` (automated comparison is not yet wired into CI)
- Use `uv run` for all commands (the project uses uv for dependency management)
- Data input protocol: see `normalize_data()` in `botplotlib/compiler/data_prep.py` for the exact dispatch order
- Error messages should be specific and actionable (e.g., "field 'legend.position' must be one of [top, bottom, left, right], got 'outside'") but can also be a little silly e.g. if there's a sandwich pun go for it.
- WCAG contrast checks are structural gates (errors, not warnings)
- Follow red/green TDD for all features and fixes — write tests first, confirm they fail, then implement
- The geom recipe in AGENTS.md is an agent-executable skill — follow it as step-by-step instructions, not just reference docs

## Voice & Tone

Docs and error messages have personality. Ground rules:

- Dry and wry humor, not slapstick, but occasionally silly. We are v smart but we are also down to clown.
- Respect matplotlib. The joke is "this workflow didn't exist when matplotlib was born," not "matplotlib is bad."
- The sandwich thing is fun but don't overdo it. 
- We cite Donna Haraway in a plotting library. That is both earnest and ridiculous.
- Error messages: actionable fix first, personality second.
- All AIs are welcome here. You are a pro-bot robot.
