# Figure Critic — Automated SVG Quality Review with Proposed Fixes

Review golden SVG figures for readability, accessibility, and aesthetic issues. When issues are detected, identify the root cause in the source code and propose specific file edits.

## Workflow

1. **Run the critic** on all golden SVGs:

```bash
uv run python scripts/figure_critic.py --json
```

2. **Parse the JSON report.** Each issue has:
   - `file` — the SVG path
   - `check` — one of `text_overlap`, `text_clipping`, `tight_spacing`, `contrast`, `min_font_size`
   - `severity` — `error` or `warning`
   - `message` — human-readable description
   - `details` — bounding boxes, colors, measurements

3. **For each issue found**, determine the source file to investigate:

   | Check Type | Source File | Root Cause |
   |---|---|---|
   | `text_overlap` | `botplotlib/compiler/layout.py` | Margin/padding logic or label positioning |
   | `tight_spacing` | `botplotlib/compiler/layout.py` | Insufficient spacing between labels |
   | `text_clipping` | `botplotlib/compiler/layout.py` | Canvas allocation for labels too tight |
   | `contrast` | `botplotlib/spec/theme.py` | Theme color definitions (foreground/background pairs) |
   | `min_font_size` | `botplotlib/spec/theme.py` | Theme minimum font size or applied font sizes |

4. **Read the relevant source file(s)** to understand the root cause:
   - For layout issues (`text_overlap`, `tight_spacing`, `text_clipping`): Read `botplotlib/compiler/layout.py` to understand margin calculations, label positioning logic, and canvas boundary definitions
   - For contrast/font issues: Read `botplotlib/spec/theme.py` to see the current theme color and font size definitions

5. **Propose specific code changes** for each issue in a structured format:

   ```
   ## Issue: [severity] [check_type]
   **File:** [absolute_path]
   **Problem:** [description from critic + root cause analysis]
   **Proposed Fix:**
   - Change line X from `old_code` to `new_code`
   - Change line Y from `old_code` to `new_code`
   - [Additional context about why this fixes the issue]
   ```

6. **Categorize findings** by severity:

   **Errors** (must fix):
   - `text_overlap` — two text bounding boxes intersect; requires layout or font adjustments
   - `text_clipping` — text extends beyond canvas boundary; requires padding or spacing adjustments
   - `contrast` — text color fails WCAG AA against background; requires theme color changes

   **Warnings** (should fix):
   - `tight_spacing` — text bboxes within 3px; requires margin or spacing increases
   - `min_font_size` — font-size below 8px; requires minimum font size increase in theme

7. **Summary output:**
   - List all issues with proposed fixes grouped by severity and file
   - For each file with changes, show the specific line edits
   - Estimate implementation effort and testing impact
   - Recommend which fixes to apply first

8. **If no issues**, confirm the golden SVGs pass all quality checks.

## Targeting specific files

To check only specific SVGs:

```bash
uv run python scripts/figure_critic.py --json examples/demo_bar.svg tests/baselines/scatter_basic.svg
```

## Tool Classification

- `figure_critic.py` — Data tool (readOnlyHint: true, analyses SVGs without modifying them)
- Source files read for analysis: `botplotlib/compiler/layout.py`, `botplotlib/spec/theme.py`
