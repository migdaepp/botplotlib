# Theme Authoring Skill

Create and validate custom themes with accessibility checks.

## Trigger

User wants to create a custom theme or modify an existing one.

## Steps

1. **Define theme**: Create a `ThemeSpec` with the user's desired colors, fonts, and sizing.
2. **Validate accessibility**: Run WCAG contrast checks:
   - Text color vs background: 4.5:1 for normal text, 3.0:1 for large text
   - Palette colors vs background: 3.0:1 minimum
3. **Test rendering**: Render a sample plot with the theme to verify visual quality.
4. **Register** (optional): Add to `THEME_REGISTRY` if it's a built-in preset.

## Example

```python
from botplotlib.spec.theme import ThemeSpec

my_theme = ThemeSpec(
    background_color="#1a1a2e",
    text_color="#e0e0e0",
    palette=["#e94560", "#0f3460", "#533483", "#16213e", ...],
    font_family="Fira Code, monospace",
)

# Validate accessibility
from botplotlib.compiler.accessibility import validate_theme_accessibility
validate_theme_accessibility(
    text_color=my_theme.text_color,
    background_color=my_theme.background_color,
    palette=my_theme.palette,
)
```

## Constraints

- All themes MUST pass WCAG AA contrast (structural gate, not advisory)
- A `ContrastError` is an error, not a warning — fix the theme, don't suppress it
- Dark themes need light text and palette colors adjusted accordingly
