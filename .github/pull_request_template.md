## Description

<!-- What does this PR do and why? -->

## Risk Level

<!-- Highest risk level of paths touched by this PR. See GOVERNANCE.md for the risk taxonomy. -->

- [ ] **Low** (docs, examples, most `*.md`)
- [ ] **Moderate** (tests, geoms, scripts)
- [ ] **High** (compiler, render, spec, `_api.py`, `figure.py`)
- [ ] **Critical** (`.github/`, `GOVERNANCE.md`, `CODEOWNERS`, `pyproject.toml`)

## Quality Gate Checklist

- [ ] `uv run pytest` — all tests pass
- [ ] `uv run ruff check .` — no lint errors
- [ ] `uv run black --check .` — formatting clean

## Rendering Changes (if applicable)

<!-- Only check these if your PR changes plot output. -->

- [ ] Baselines regenerated (`uv run python scripts/update_baselines.py`)
- [ ] SVGs in `tests/baselines/` visually inspected

## Contributor Capability Card (optional)

<!-- Voluntary process disclosure. What tools or models were used?
     This is for learning, not gatekeeping. See GOVERNANCE.md capability attestation. -->

<!--
Example:
- Commits signed: yes
- AI assistance: Claude Code (Opus 4)
- Autonomy level: semi-autonomous (human reviewed diffs)
- Tests written by: human + AI pair
-->
