"""matplotlib version: 16 lines for a styled bar chart."""

import matplotlib.pyplot as plt

languages = ["Python", "JavaScript", "Rust", "Go", "TypeScript"]
popularity = [92, 88, 45, 62, 78]

plt.figure(figsize=(8, 5))
plt.bar(languages, popularity, color="#2196F3", edgecolor="white", linewidth=0.5)
plt.title("Programming Language Popularity")
plt.xlabel("Language")
plt.ylabel("Popularity Score")
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig("languages.png", dpi=300)
plt.show()
