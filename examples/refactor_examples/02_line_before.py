"""matplotlib version: 18 lines for a line chart with styling."""

import matplotlib.pyplot as plt

years = [2019, 2020, 2021, 2022, 2023, 2024]
revenue = [85, 100, 120, 115, 140, 160]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years, revenue, "b-", linewidth=2, label="Revenue")
ax.set_title("Annual Revenue Growth")
ax.set_xlabel("Year")
ax.set_ylabel("Revenue ($M)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.savefig("revenue.png", dpi=300, bbox_inches="tight")
plt.show()
