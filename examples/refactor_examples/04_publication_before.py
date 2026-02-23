"""matplotlib version: 25 lines to get publication-ready output."""

import matplotlib.pyplot as plt

# Data
temp_anomaly = [0.08, 0.12, 0.18, 0.25, 0.32, 0.40, 0.52, 0.65, 0.78, 0.90, 1.02]
years = [1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020]

# Create figure
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(years, temp_anomaly, "r-", linewidth=1.8, label="Temperature anomaly")

# Styling for publication
ax.set_title("Global Temperature Anomaly", fontsize=14, fontweight="bold")
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Temperature Anomaly (C)", fontsize=12)
ax.tick_params(labelsize=10)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, linestyle="--")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(1968, 2022)
ax.set_ylim(0, 1.1)

fig.tight_layout()
fig.savefig("temperature.pdf", dpi=300, bbox_inches="tight")
plt.show()
