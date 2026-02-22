"""matplotlib version: 15 lines of imperative code."""

import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [2.3, 4.1, 3.5, 6.2, 5.8, 7.1, 8.3, 7.9]

plt.figure(figsize=(10, 6))
plt.scatter(x, y, color="steelblue", label="measurements")
plt.title("Experiment Results")
plt.xlabel("Trial Number")
plt.ylabel("Measurement (cm)")
plt.legend()
plt.grid(True)
plt.savefig("experiment.png", dpi=300, bbox_inches="tight")
plt.show()
