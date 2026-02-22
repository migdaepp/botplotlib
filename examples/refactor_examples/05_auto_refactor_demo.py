"""Demonstrates the automatic refactoring tool.

Run this script to see the matplotlib-to-botplotlib conversion in action.
The refactor module reads matplotlib code via AST and produces the
equivalent botplotlib PlotSpec -- no matplotlib installation needed.
"""

from botplotlib.refactor.from_matplotlib import from_matplotlib, to_botplotlib_code

# --- The matplotlib script (as a string) -----------------------------------

MATPLOTLIB_SCRIPT = """
import matplotlib.pyplot as plt

years = [2020, 2021, 2022, 2023, 2024]
revenue = [100, 120, 115, 140, 160]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years, revenue, 'b-', label='Revenue')
ax.scatter(years, revenue, color='navy', label='Data points')
ax.set_title("Company Growth")
ax.set_xlabel("Year")
ax.set_ylabel("Revenue ($M)")
ax.legend()
ax.grid(True)
fig.savefig("growth.png", dpi=300)
plt.show()
"""

# --- Convert to PlotSpec ---------------------------------------------------

print("=" * 60)
print("MATPLOTLIB INPUT (16 lines)")
print("=" * 60)
print(MATPLOTLIB_SCRIPT)

spec = from_matplotlib(MATPLOTLIB_SCRIPT)

print("=" * 60)
print("PLOTSPEC OUTPUT (JSON)")
print("=" * 60)
print(spec.model_dump_json(indent=2))

print()
print("=" * 60)
print("BOTPLOTLIB EQUIVALENT CODE")
print("=" * 60)
print(to_botplotlib_code(MATPLOTLIB_SCRIPT))
