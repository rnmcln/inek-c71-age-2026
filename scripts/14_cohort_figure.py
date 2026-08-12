#!/usr/bin/env python3
"""Draw Supplementary Figure S1: cohort derivation and the two denominators."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

meta = json.load(open("study_meta.json"))
YEAR = meta["study_year"]

fig, ax = plt.subplots(figsize=(7.2, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

def box(x, y, w, h, text, fc="#eef2fb"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                linewidth=1.1, edgecolor="#33415c", facecolor=fc))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, wrap=True)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=1.1, color="#33415c"))

box(2.6, 8.4, 4.8, 1.2,
    f"InEK DatenBrowser §21 export\n(malignant brain neoplasm, ICD-10 C71)\n{YEAR} data year", fc="#dfe7f5")
arrow(5.0, 8.4, 3.4, 6.5)
arrow(5.0, 8.4, 6.6, 6.5)

box(0.6, 5.1, 4.0, 1.4,
    "Principal-diagnosis cohort\nC71 as principal (main) diagnosis\nn = 18,621 episodes")
box(5.4, 5.1, 4.0, 1.4,
    "C71-coded population\nC71 as principal OR secondary diagnosis\nn = 23,594 episodes")

arrow(2.6, 5.1, 2.6, 3.6)
arrow(7.4, 5.1, 7.4, 3.6)

box(0.6, 2.2, 4.0, 1.4,
    "Analyses:\nsex, in-hospital mortality,\ndischarge disposition", fc="#eaf3ec")
box(5.4, 2.2, 4.0, 1.4,
    "Analyses:\ncomorbidity (Charlson),\nprocedure coding", fc="#eaf3ec")

ax.text(5.0, 0.9,
        "Different denominators; the two cohorts cannot be linked at the episode level\n"
        "and their results are not directly comparable.",
        ha="center", va="center", fontsize=8.5, style="italic", color="#33415c")

plt.tight_layout()
fig.savefig("figures/FigS1_cohort.png", dpi=200, bbox_inches="tight")
fig.savefig("figures/FigS1_cohort.pdf", bbox_inches="tight")
print("saved figures/FigS1_cohort.png/.pdf")
