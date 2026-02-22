# Visual Regression Skill

Render plots and compare against golden SVG baselines to detect visual regressions.

## Trigger

After any change to rendering code (svg_renderer, svg_builder, compiler, theme).

## Steps

1. **Render**: Compile and render all baseline specs to SVG.
2. **Compare**: Diff each rendered SVG against the golden file in `tests/baselines/`.
3. **Report**: If differences are found, report which baselines changed and what changed.
4. **Update** (if intentional): Run `uv run pytest --update-baselines` or `uv run python scripts/update_baselines.py` to regenerate golden files.

## Commands

```bash
# Run visual regression tests
uv run pytest tests/ -k baseline

# Update baselines (destructive — overwrites golden files)
uv run pytest --update-baselines
uv run python scripts/update_baselines.py
```

## Tool Classification

- `render_snapshots` — Action tool (renders current specs)
- `update_baselines` — Orchestration tool (destructiveHint: true)

## Constraints

- Never update baselines without reviewing the diff first
- All baseline changes must be accompanied by an explanation
- PRs that change rendering must include before/after comparisons
