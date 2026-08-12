#!/usr/bin/env python3
"""Effect sizes, trend-score sensitivity, and Poisson dispersion diagnostics.

Adds, without altering the primary analysis:
  (1) Effect sizes for the principal-cohort binary outcomes: absolute risk
      difference (oldest vs youngest band) with a Newcombe 95% CI, and an odds
      ratio per decade of age from a grouped-binomial logistic trend model with
      a Wald 95% CI.
  (2) Cramer's V for the two global chi-square contingency tests (sex x age,
      disposition x age), as a sample-size-independent measure of association
      strength.
  (3) A Cochran-Armitage score-sensitivity analysis: trend p-values recomputed
      under integer rank scores and under alternative open-band scores, to show
      the trend conclusions do not depend on the midpoint scoring.
  (4) A dispersion diagnostic for the Charlson comorbidity-point Poisson trend
      model (Pearson dispersion statistic) and a quasi-Poisson 95% CI for the
      rate ratio per decade, alongside the ordinary Poisson CI.

Reads the derived CSV/JSON produced by 01 and 08; writes effects_sensitivity.json.
Pure Python + NumPy; no scipy/statsmodels dependency.
"""
import csv, json, math
import numpy as np

DD = "derived_data"
BANDS = ["18-29", "30-39", "40-49", "50-54", "55-59", "60-64", "65-74", "75-79", ">=80"]
MID = [23.5, 34.5, 44.5, 52.0, 57.0, 62.0, 69.5, 77.0, 85.0]   # primary scores
RANK = [1, 2, 3, 4, 5, 6, 7, 8, 9]                              # integer ranks
MID_80 = [23.5, 34.5, 44.5, 52.0, 57.0, 62.0, 69.5, 77.0, 82.5]  # oldest band -> 82.5
MID_90 = [23.5, 34.5, 44.5, 52.0, 57.0, 62.0, 69.5, 77.0, 90.0]  # oldest band -> 90


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def two_sided_p(z):
    return 2 * (1 - norm_cdf(abs(z)))


def wilson_bounds(k, n, z=1.959963984540054):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (centre - half, centre + half)


def newcombe_rd_ci(k1, n1, k2, n2, z=1.959963984540054):
    """Newcombe method 10 CI for the difference p2 - p1 (oldest - youngest)."""
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson_bounds(k1, n1, z)
    l2, u2 = wilson_bounds(k2, n2, z)
    d = p2 - p1
    lower = d - z * math.sqrt(l2 * (1 - l2) / n2 + u1 * (1 - u1) / n1)
    upper = d + z * math.sqrt(u2 * (1 - u2) / n2 + l1 * (1 - l1) / n1)
    return d, lower, upper


def cochran_armitage(events, totals, scores):
    ri = np.array(events, float); ni = np.array(totals, float); xi = np.array(scores, float)
    N = ni.sum(); R = ri.sum(); p = R / N
    T = np.sum(xi * (ri - ni * p))
    var = p * (1 - p) * (np.sum(ni * xi ** 2) - (np.sum(ni * xi)) ** 2 / N)
    if var <= 0:
        return float("nan"), float("nan")
    z = T / math.sqrt(var)
    return z, two_sided_p(z)


def logistic_trend(events, totals, scores):
    """Grouped-binomial logistic regression logit(p)=b0+b1*score by IRLS.
    Returns b1 (per year), SE(b1). Scores in years -> OR per decade = exp(10 b1)."""
    e = np.array(events, float); n = np.array(totals, float); x = np.array(scores, float)
    b0, b1 = 0.0, 0.0
    for _ in range(100):
        eta = b0 + b1 * x
        p = 1.0 / (1.0 + np.exp(-eta))
        w = n * p * (1 - p)
        # gradient of log-likelihood
        g0 = np.sum(e - n * p)
        g1 = np.sum(x * (e - n * p))
        # negative Hessian (information)
        h00 = np.sum(w); h01 = np.sum(x * w); h11 = np.sum(x * x * w)
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-300:
            break
        db0 = (h11 * g0 - h01 * g1) / det
        db1 = (-h01 * g0 + h00 * g1) / det
        b0 += db0; b1 += db1
        if abs(db0) < 1e-12 and abs(db1) < 1e-12:
            break
    # covariance = inverse information at the solution
    eta = b0 + b1 * x
    p = 1.0 / (1.0 + np.exp(-eta))
    w = n * p * (1 - p)
    h00 = np.sum(w); h01 = np.sum(x * w); h11 = np.sum(x * x * w)
    det = h00 * h11 - h01 * h01
    var_b1 = h00 / det
    return b1, math.sqrt(var_b1)


def cramers_v(chi2, N, r, c):
    return math.sqrt(chi2 / (N * (min(r, c) - 1)))


# ---------------------------------------------------------------------------
# Load principal-cohort counts and derived statistics
# ---------------------------------------------------------------------------
stats = json.load(open(f"{DD}/statistics.json"))
prin = {r["age_band"]: r for r in csv.DictReader(open(f"{DD}/principal_cohort_by_age.csv"))}
n_by = [int(prin[b]["n_principal"]) for b in BANDS]

OUTCOMES = {
    "In-hospital mortality": "death",
    "Discharged home": "home",
    "Transfer to nursing home": "nursing_home",
    "Transfer to hospice care": "hospice",
    "Transfer to another hospital": "transfer_hospital",
}

def bh_fdr(pvals):
    p = np.asarray(pvals, float); m = len(p); order = np.argsort(p)
    ranked = p[order] * m / (np.arange(m) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adj = np.empty(m); adj[order] = np.clip(ranked, 0, 1)
    return adj

out = {"effect_sizes": {}, "ca_sensitivity": {}, "cramers_v": {},
       "disposition_fdr": {}, "poisson_dispersion": {}}

# --- BH-FDR across the discharge-disposition trend-test family (consistency
#     with the comorbidity and procedure families, which are FDR-adjusted in 01) ---
_disp_keys = ["disp_death", "disp_home", "disp_nursing", "disp_hospice", "disp_transfer"]
_disp_p = [stats[k]["p_trend"] for k in _disp_keys]
_disp_adj = bh_fdr(_disp_p)
for k, pa in zip(_disp_keys, _disp_adj):
    out["disposition_fdr"][stats[k]["label"]] = {"p_trend": stats[k]["p_trend"],
                                                 "p_trend_fdr": float(pa)}
out["disposition_fdr"]["_max_fdr"] = float(max(_disp_adj))

# --- effect sizes: risk difference (oldest-youngest) + OR per decade ---
for label, col in OUTCOMES.items():
    e = [int(prin[b][col]) for b in BANDS]
    rd, lo, hi = newcombe_rd_ci(e[0], n_by[0], e[-1], n_by[-1])
    b1, se = logistic_trend(e, n_by, MID)
    or_dec = math.exp(10 * b1)
    or_lo = math.exp(10 * (b1 - 1.959963984540054 * se))
    or_hi = math.exp(10 * (b1 + 1.959963984540054 * se))
    out["effect_sizes"][label] = {
        "p_youngest": e[0] / n_by[0], "p_oldest": e[-1] / n_by[-1],
        "risk_diff": rd, "rd_ci": [lo, hi],
        "or_per_decade": or_dec, "or_ci": [or_lo, or_hi],
    }

# male proportion effect size (declining trend)
male = [int(prin[b]["male"]) for b in BANDS]
rd, lo, hi = newcombe_rd_ci(male[0], n_by[0], male[-1], n_by[-1])
b1, se = logistic_trend(male, n_by, MID)
out["effect_sizes"]["Male proportion"] = {
    "p_youngest": male[0] / n_by[0], "p_oldest": male[-1] / n_by[-1],
    "risk_diff": rd, "rd_ci": [lo, hi],
    "or_per_decade": math.exp(10 * b1),
    "or_ci": [math.exp(10 * (b1 - 1.96 * se)), math.exp(10 * (b1 + 1.96 * se))],
}

# --- Cramer's V for the two global contingency tests ---
sg = stats["sex_global"]; dg = stats["disposition_global"]
N_prin = sum(n_by)
out["cramers_v"]["sex_by_age"] = {
    "chi2": sg["chi2"], "dof": sg["dof"], "V": cramers_v(sg["chi2"], N_prin, 2, 9)}
out["cramers_v"]["disposition_by_age"] = {
    "chi2": dg["chi2"], "dof": dg["dof"], "V": cramers_v(dg["chi2"], N_prin, 6, 9)}

# --- Cochran-Armitage score sensitivity (all principal + comorbidity + procedure) ---
def sens_row(events, totals):
    res = {}
    for tag, sc in [("midpoint", MID), ("rank", RANK), ("oldest_82.5", MID_80), ("oldest_90", MID_90)]:
        z, p = cochran_armitage(events, totals, sc)
        res[tag] = {"z": z, "p": p}
    return res

for label, col in OUTCOMES.items():
    e = [int(prin[b][col]) for b in BANDS]
    out["ca_sensitivity"][label] = sens_row(e, n_by)
out["ca_sensitivity"]["Male proportion"] = sens_row(male, n_by)

# comorbidity + procedures use union denominators
union = stats["meta"]["union_by_band"]
un = [int(union[b]) for b in BANDS]
for name, st in stats["comorbidity"].items():
    out["ca_sensitivity"]["Comorbidity: " + name] = sens_row(st["events"], un)
for name, st in stats["procedures"].items():
    out["ca_sensitivity"]["Procedure: " + name] = sens_row(st["events"], un)

# --- Poisson dispersion diagnostic + quasi-Poisson RR CI for Charlson points ---
cci = json.load(open(f"{DD}/charlson_index.json"))
ch_csv = list(csv.DictReader(open(f"{DD}/charlson_index_by_age.csv")))
pts = [float(r["comorbidity_points"]) for r in ch_csv]
Nun = [float(r["n_union"]) for r in ch_csv]
b1 = cci["poisson_slope_per_year"]
# refit intercept-consistent mu and compute Pearson dispersion
logN = [math.log(n) for n in Nun]
# recover b0 from the fitted slope by matching total (as in script 08)
# fit b0,b1 jointly again for mu
y = [round(p) for p in pts]; x = MID
bb0, bb1 = math.log(sum(y) / sum(Nun)), 0.0
for _ in range(100):
    g0 = g1 = h00 = h01 = h11 = 0.0
    for i in range(9):
        mu = math.exp(bb0 + bb1 * x[i] + logN[i])
        g0 += y[i] - mu; g1 += x[i] * (y[i] - mu)
        h00 -= mu; h01 -= x[i] * mu; h11 -= x[i] * x[i] * mu
    det = h00 * h11 - h01 * h01
    db0 = (h11 * g0 - h01 * g1) / det; db1 = (-h01 * g0 + h00 * g1) / det
    bb0 -= db0; bb1 -= db1
    if abs(db0) < 1e-12 and abs(db1) < 1e-12:
        break
mu = [math.exp(bb0 + bb1 * x[i] + logN[i]) for i in range(9)]
pearson = sum((y[i] - mu[i]) ** 2 / mu[i] for i in range(9))
dof = 9 - 2
dispersion = pearson / dof
# information for SE(b1)
info00 = sum(mu); info01 = sum(x[i] * mu[i] for i in range(9)); info11 = sum(x[i] ** 2 * mu[i] for i in range(9))
detI = info00 * info11 - info01 * info01
se_b1 = math.sqrt(info00 / detI)
se_b1_qp = se_b1 * math.sqrt(dispersion)     # quasi-Poisson scaled SE
z = 1.959963984540054
rr = math.exp(10 * bb1)
out["poisson_dispersion"] = {
    "rr_per_decade": rr,
    "poisson_ci": [math.exp(10 * (bb1 - z * se_b1)), math.exp(10 * (bb1 + z * se_b1))],
    "pearson_chi2": pearson, "dof": dof, "dispersion": dispersion,
    "quasipoisson_ci": [math.exp(10 * (bb1 - z * se_b1_qp)), math.exp(10 * (bb1 + z * se_b1_qp))],
    "quasipoisson_p": two_sided_p(bb1 / se_b1_qp),
}

# --- flag effect sizes whose youngest band is privacy-suppressed ---
import os
_supp_path = f"{DD}/suppressed_cells.json"
if os.path.exists(_supp_path):
    _supp = json.load(open(_supp_path))
    _map = {"Transfer to nursing home": "nursing_home", "Transfer to hospice care": "hospice",
            "Transfer to another hospital": "transfer_hospital", "In-hospital mortality": "death",
            "Discharged home": "home"}
    for lab, key in _map.items():
        if lab in out["effect_sizes"] and _supp["disposition"].get(key, {}).get("18-29"):
            out["effect_sizes"][lab]["youngest_suppressed"] = True

# --- older-age absolute service burden (>=65 and >=75), principal cohort ---
older = {}
for thr, bands_incl in {">=65": ["65-74", "75-79", ">=80"], ">=75": ["75-79", ">=80"]}.items():
    N = sum(n_by[BANDS.index(b)] for b in bands_incl)
    row = {"n_episodes": N, "pct_of_cohort": 100 * N / sum(n_by)}
    for lab, col in {"death": "death", "hospice": "hospice", "nursing_home": "nursing_home",
                     "transfer_hospital": "transfer_hospital", "home": "home"}.items():
        c = sum(int(prin[b][col]) for b in bands_incl)
        row[lab] = {"n": c, "pct_of_group": 100 * c / N}
    older[thr] = row
out["older_age_burden"] = older

# --- episodes per year of age-band width (workload density), principal cohort ---
WIDTH = {"18-29": 12, "30-39": 10, "40-49": 10, "50-54": 5, "55-59": 5,
         "60-64": 5, "65-74": 10, "75-79": 5, ">=80": None}
out["per_year_width"] = {b: (n_by[BANDS.index(b)] / WIDTH[b] if WIDTH[b] else None) for b in BANDS}

json.dump(out, open(f"{DD}/effects_sensitivity.json", "w"), indent=2)

# ---------------------------------------------------------------------------
# Console report
# ---------------------------------------------------------------------------
print("EFFECT SIZES (oldest vs youngest band; OR per decade of age)")
for k, v in out["effect_sizes"].items():
    print(f"  {k:<32} {100*v['p_youngest']:5.1f}% -> {100*v['p_oldest']:5.1f}%  "
          f"RD {100*v['risk_diff']:+5.1f} pp (95% CI {100*v['rd_ci'][0]:+.1f} to {100*v['rd_ci'][1]:+.1f}); "
          f"OR/decade {v['or_per_decade']:.2f} ({v['or_ci'][0]:.2f}-{v['or_ci'][1]:.2f})")
print("\nCRAMER'S V (global associations)")
for k, v in out["cramers_v"].items():
    print(f"  {k:<22} chi2={v['chi2']:.1f} df={v['dof']} V={v['V']:.3f}")
print("\nCA SCORE SENSITIVITY (p-values; sign of z in parentheses) — first rows")
shown = 0
for k, v in out["ca_sensitivity"].items():
    def f(p):
        return "<0.001" if p < 0.001 else f"{p:.3f}"
    print(f"  {k:<40} mid {f(v['midpoint']['p'])}  rank {f(v['rank']['p'])}  "
          f"80->82.5 {f(v['oldest_82.5']['p'])}  80->90 {f(v['oldest_90']['p'])}")
    shown += 1
print("\nPOISSON DISPERSION (Charlson comorbidity-point trend)")
d = out["poisson_dispersion"]
print(f"  RR/decade = {d['rr_per_decade']:.2f}")
print(f"  Poisson 95% CI       {d['poisson_ci'][0]:.3f}-{d['poisson_ci'][1]:.3f}")
print(f"  Pearson chi2 = {d['pearson_chi2']:.1f} on {d['dof']} df; dispersion = {d['dispersion']:.2f}")
print(f"  quasi-Poisson 95% CI {d['quasipoisson_ci'][0]:.3f}-{d['quasipoisson_ci'][1]:.3f}  p={d['quasipoisson_p']:.2g}")
