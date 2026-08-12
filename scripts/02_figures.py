#!/usr/bin/env python3
"""
Publication figures for the C71 age study.
Tufte-inspired: minimal spines, no embedded titles, point estimates with
95% Wilson confidence intervals, restrained palette, vector + 300 dpi output.
"""
import json
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

STATS = "derived_data/statistics.json"
FIGDIR = "figures"
d = json.load(open(STATS))

BANDS = ["18-29", "30-39", "40-49", "50-54", "55-59", "60-64",
         "65-74", "75-79", ">=80"]
XLAB = ["18-29", "30-39", "40-49", "50-54", "55-59", "60-64",
        "65-74", "75-79", "≥80"]
X = list(range(len(BANDS)))

ACCENT = "#34618a"      # muted blue accent
DARK = "#2c3e50"        # near-black slate
GREY = "#8a8f96"        # muted grey
LGREY = "#c8ccd1"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 8,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#333333",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "text.color": "#000000",
    "axes.labelcolor": "#000000",
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def panel_label(ax, s):
    ax.text(-0.16, 1.04, s, transform=ax.transAxes, fontsize=9,
            fontweight="regular", va="bottom", ha="left")


def save(fig, name):
    fig.savefig(f"{FIGDIR}/{name}.pdf")
    fig.savefig(f"{FIGDIR}/{name}.png")
    plt.close(fig)


def pct(v):
    return [100 * x for x in v]


# ===========================================================================
# Figure 1 — cohort age and sex structure
# ===========================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))

n_by = [d["meta"]["principal_by_band"][b] for b in BANDS]
ax1.bar(X, n_by, width=0.68, color=GREY, edgecolor="none")
ax1.set_ylabel("Discharge episodes (n)")
ax1.set_xticks(X)
ax1.set_xticklabels(XLAB, rotation=45, ha="right")
ax1.set_xlabel("Age band (years)")
ax1.yaxis.set_major_locator(MultipleLocator(1000))
ax1.set_ylim(0, max(n_by) * 1.12)
panel_label(ax1, "a")

sm = d["sex_male"]
p = pct(sm["prop"])
lo = [100 * x for x in sm["ci_low"]]
hi = [100 * x for x in sm["ci_high"]]
err = [[pi - loi for pi, loi in zip(p, lo)], [hii - pi for hii, pi in zip(hi, p)]]
ax2.axhline(50, color=LGREY, lw=0.6, zorder=0)
ax2.errorbar(X, p, yerr=err, fmt="o", ms=4, mfc="white", mec=ACCENT,
             ecolor=ACCENT, elinewidth=0.7, capsize=2, color=ACCENT)
ax2.set_ylabel("Male proportion (%)")
ax2.set_xticks(X)
ax2.set_xticklabels(XLAB, rotation=45, ha="right")
ax2.set_xlabel("Age band (years)")
ax2.set_ylim(45, 68)
panel_label(ax2, "b")

fig.subplots_adjust(wspace=0.32, bottom=0.22)
save(fig, "Fig1")

# ===========================================================================
# Figure 2 — discharge disposition by age (principal cohort)
# ===========================================================================
fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.9))


def ci_panel(ax, key, ylab, ymax, colour):
    s = d[key]
    p = pct(s["prop"])
    lo = [100 * x for x in s["ci_low"]]
    hi = [100 * x for x in s["ci_high"]]
    err = [[a - b for a, b in zip(p, lo)], [a - b for a, b in zip(hi, p)]]
    ax.errorbar(X, p, yerr=err, fmt="o", ms=3.6, mfc="white", mec=colour,
                ecolor=colour, elinewidth=0.7, capsize=2, color=colour)
    ax.set_ylabel(ylab)
    ax.set_xticks(X)
    ax.set_xticklabels(XLAB, rotation=45, ha="right", fontsize=7)
    ax.set_ylim(0, ymax)
    ax.set_xlabel("Age band (years)", fontsize=7.5)


ci_panel(axes[0], "disp_death", "In-hospital mortality (%)", 17, ACCENT)
panel_label(axes[0], "a")
ci_panel(axes[1], "disp_home", "Discharged home (%)", 100, DARK)
panel_label(axes[1], "b")

# panel c: stacked disposition composition
ax = axes[2]
comp_keys = ["death", "hospice", "nursing", "transfer", "other", "home"]
comp_lab = ["Death", "Hospice", "Nursing home", "Other hospital",
            "Other", "Home"]
comp_col = ["#2c3e50", "#5d6d7e", "#8a8f96", "#b0b5bb", "#d3d6d9", "#eef0f2"]
import csv
rows = {r["age_band"]: r for r in csv.DictReader(
    open("derived_data/principal_cohort_by_age.csv"))}
bottoms = [0.0] * len(BANDS)
for k, lab, col in zip(comp_keys, comp_lab, comp_col):
    vals = []
    for b in BANDS:
        r = rows[b]
        n = int(r["n_principal"])
        key = {"nursing": "nursing_home", "transfer": "transfer_hospital",
               "other": "other_residual"}.get(k, k)
        vals.append(100 * int(r[key]) / n)
    ax.bar(X, vals, bottom=bottoms, width=0.72, color=col, edgecolor="white",
           linewidth=0.3, label=lab)
    bottoms = [a + b for a, b in zip(bottoms, vals)]
ax.set_ylabel("Disposition (% of episodes)")
ax.set_xticks(X)
ax.set_xticklabels(XLAB, rotation=45, ha="right", fontsize=7)
ax.set_ylim(0, 100)
ax.set_xlabel("Age band (years)", fontsize=7.5)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=3,
          frameon=False, fontsize=6.2, handlelength=1.1, columnspacing=1.0,
          handletextpad=0.4)
panel_label(ax, "c")

fig.subplots_adjust(wspace=0.42, bottom=0.24, top=0.86)
save(fig, "Fig2")

# ===========================================================================
# Figure 3 — comorbidity and treatment gradients (C71-coded population)
# ===========================================================================
fig, (axc, axp) = plt.subplots(1, 2, figsize=(8.4, 3.2))

# graded greys + accent for emphasis; distinct markers; direct end-labels
def line_panel(ax, items, ylab, ymax, xlim_right):
    styles = [("o", "-"), ("s", "-"), ("^", "-"), ("D", "-"), ("v", "-"), ("<", "-")]
    cols = [ACCENT, "#2c3e50", "#5a6470", "#7f8792", "#a3a9b0", "#c4c8cd"]
    ends = []
    for (name, src, disp), (mk, ls), col in zip(items, styles, cols):
        s = d[src][disp]
        y = pct(s["prop"])
        ax.plot(X, y, ls, marker=mk, ms=3.2, lw=0.9, color=col, mfc="white",
                mec=col, mew=0.8)
        ends.append([y[-1], name, col])
    # declutter labels: keep off the axis (floor) and enforce vertical spacing
    ends.sort(key=lambda e: e[0])
    min_gap = ymax * 0.066
    floor = ymax * 0.045
    if ends[0][0] < floor:
        ends[0][0] = floor
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i - 1][0] < min_gap:
            ends[i][0] = ends[i - 1][0] + min_gap
    for ly, name, col in ends:
        ax.text(X[-1] + 0.22, ly, name, fontsize=6.4, va="center",
                ha="left", color=col)
    ax.set_ylabel(ylab)
    ax.set_xticks(X)
    ax.set_xticklabels(XLAB, rotation=45, ha="right", fontsize=7)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.3, xlim_right)
    ax.set_xlabel("Age band (years)", fontsize=7.5)


comorbid_items = [
    ("Diabetes mellitus", "comorbidity", "Diabetes mellitus"),
    ("Renal failure / CKD", "comorbidity", "Renal failure / chronic kidney disease"),
    ("Dementia", "comorbidity", "Dementia"),
    ("Heart failure", "comorbidity", "Heart failure"),
    ("Cerebrovascular disease", "comorbidity", "Cerebrovascular disease"),
]
line_panel(axc, comorbid_items, "Prevalence (% of episodes)", 26, xlim_right=13.6)
panel_label(axc, "a")

proc_items = [
    ("Cranial CT", "procedures", "Native cranial CT (3-200)"),
    ("Cranial MRI", "procedures", "Native cranial MRI (3-800)"),
    ("Radiotherapy", "procedures", "Inpatient high-voltage radiotherapy (8-522.x)"),
    ("Microsurgery", "procedures", "Microsurgical technique (5-984)"),
    ("Stereotactic biopsy", "procedures", "Stereotactic biopsy, supratentorial (1-511.0x)"),
    ("Ventricular drain", "procedures", "External ventricular drain (5-022.00)"),
]
line_panel(axp, proc_items, "Coding frequency (% of episodes)", 65, xlim_right=12.4)
panel_label(axp, "b")

fig.subplots_adjust(wspace=0.5, bottom=0.22, left=0.08, right=0.98)
save(fig, "Fig3")

print("Figures written to", FIGDIR)
