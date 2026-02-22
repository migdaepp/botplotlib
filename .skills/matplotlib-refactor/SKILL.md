# Matplotlib Refactor Skill

Convert matplotlib scripts to botplotlib PlotSpec.

## Trigger

User has a matplotlib script they want to convert to botplotlib.

## Steps

1. **Read source**: Accept a `.py` file path or inline code string.
2. **Parse**: Use `from_matplotlib()` to extract plot type, data, and labels via AST analysis.
3. **Review**: Show the user the extracted `PlotSpec` for confirmation.
4. **Render**: Optionally render the spec to verify equivalent output.
5. **Output**: Provide the equivalent botplotlib code.

## Supported Patterns

| Matplotlib | botplotlib |
|---|---|
| `plt.scatter(x, y)` | `bpl.scatter(data, x="x", y="y")` |
| `plt.plot(x, y)` | `bpl.line(data, x="x", y="y")` |
| `plt.bar(x, y)` | `bpl.bar(data, x="x", y="y")` |
| `ax.scatter(x, y)` | `bpl.scatter(data, x="x", y="y")` |
| `ax.plot(x, y)` | `bpl.line(data, x="x", y="y")` |
| `ax.bar(x, y)` | `bpl.bar(data, x="x", y="y")` |
| `plt.title("...")` | `title="..."` parameter |
| `plt.xlabel("...")` | `x_label="..."` parameter |

## Example

```python
from botplotlib.refactor import from_matplotlib

# From a file
spec = from_matplotlib("old_script.py")

# From inline code
spec = from_matplotlib('''
import matplotlib.pyplot as plt
plt.scatter([1,2,3], [4,5,6])
plt.title("My Plot")
plt.show()
''')

# Render the converted spec
import botplotlib as bpl
fig = bpl.render(spec)
fig.save_svg("migrated.svg")
```

## Limitations

- Only handles simple matplotlib patterns (direct data, not DataFrame column access)
- Does not convert styling (colors, markers, line styles) — uses botplotlib defaults
- Complex multi-axes figures are not supported in MVP
