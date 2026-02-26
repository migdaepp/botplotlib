# Contributing

We follow a cyborg social contract:

1. **All contributions are cyborg** — we reject the human/machine binary
2. **Quality gates are structural** — CI/tests/linters apply equally regardless of origin
3. **No moral crumple zones** — fix the system, don't blame the nearest human
4. **Trust is active capital** — earned through contribution quality, staked through vouching, lost through defection — never granted by biological status
5. **Provenance is transparent but not punitive** — metadata for learning, not gatekeeping
6. **The project is the cyborg** — the library itself is the human-machine hybrid

Read [GOVERNANCE.md](https://github.com/migdaepp/botplotlib/blob/main/GOVERNANCE.md) for the full system: risk taxonomy, review gates, reputation escrow, and circuit breakers. It is very overengineered but it was fun to write.

## Understanding the Review Process

Every PR goes through a review gate that depends on two things: **your contributor tier** (how much trust you've built) and the **risk level** of the paths you're changing.

### Risk levels

| Level | Example paths | What it means |
|-------|--------------|---------------|
| **Low** | `docs/`, `examples/`, `*.md` | Highly reversible, low blast radius |
| **Moderate** | `tests/`, `botplotlib/geoms/`, `scripts/` | Detectable in CI, moderate impact |
| **High** | `botplotlib/compiler/`, `render/`, `spec/`, `_api.py` | Core pipeline — changes affect all output |
| **Critical** | `.github/`, `GOVERNANCE.md`, `CODEOWNERS`, `pyproject.toml` | Privilege boundary — changes alter who can do what |

Higher risk = more approvals required. Even maintainers can't self-approve critical-risk changes. Nobody is above the sandwich law.

### How to level up

1. Start with `good-first-issue` labeled issues
2. Ship clean PRs — run the gate checklist before submitting
3. Respond to review feedback promptly
4. Review others' work (builds your Review Quality signal)
5. Contribute across domains — breadth unlocks domain trust in multiple areas

See [GOVERNANCE.md](https://github.com/migdaepp/botplotlib/blob/main/GOVERNANCE.md) for full promotion rubrics, domain trust, and the active capital model.

<p align="center">
  <img src="../images/all-cyborgs-here.png" alt="we are all cyborgs here my friends" width="700">
</p>

## Build / test / lint

```bash
uv run pytest                           # all tests
uv run pytest tests/test_foo.py::test_name  # single test
uv run pytest --update-baselines        # regenerate golden SVGs
uv run ruff check .                     # lint
uv run black --check .                  # format check
```

## PR conventions

- **Spec-diff for rendering changes**: if a PR changes plot output, include before/after spec diffs
- **Visual regression evidence**: PRs that change rendering must include baseline comparisons
- **Tests travel with code**: new geoms, features, or bug fixes include tests in the same PR

## License

[CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) — this is what the cool bots are using.
