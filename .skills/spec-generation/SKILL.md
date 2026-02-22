# Spec Generation Skill

Generate a botplotlib `PlotSpec` from a natural-language description and data.

## Trigger

User provides a description of what they want to plot and optionally their data.

## Steps

1. **Parse intent**: Identify the plot type (scatter, line, bar), data columns, grouping, and title from the user's description.
2. **Normalize data**: If the user provides data in any supported format (dict, list of dicts, CSV description), convert it to a columnar dict.
3. **Build spec**: Construct a `PlotSpec` with appropriate layers, labels, and theme.
4. **Validate**: Ensure the spec passes Pydantic validation and accessibility checks.
5. **Return**: Output the spec as JSON or render it directly.

## Example

User: "Make a scatter plot of weight vs mpg, colored by origin"

```python
import botplotlib as bpl

fig = bpl.scatter(data, x="weight", y="mpg", color="origin",
                  title="Fuel Efficiency by Weight")
fig.save_svg("plot.svg")
```

## Constraints

- Always use the flat API (`bpl.scatter`, `bpl.line`, `bpl.bar`)
- Default to the `"default"` theme unless the user specifies otherwise
- Include a title if the user's description implies one
- Set axis labels based on column names unless the user specifies alternatives
