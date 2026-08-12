# inek-c71-age-2026

Analysis code for a nationwide, age-stratified study of hospital care, comorbidity, and
discharge outcomes in adults with malignant brain neoplasm (ICD-10-GM **C71**) in Germany,
using aggregate administrative data from the InEK DatenBrowser (§21 KHEntgG).

The repository contains the full analysis pipeline and a detailed study summary
([`SUMMARY.md`](SUMMARY.md)). It does **not** contain the source data, any derived data
tables, or the manuscript. The InEK data are publicly available but may not be redistributed;
all reported numbers, figures, and tables can be regenerated from your own DatenBrowser export
by running the pipeline (see below and [`data/README.md`](data/README.md)).

## Data source

Institute for the Hospital Remuneration System (InEK GmbH), **InEK DatenBrowser**,
https://datenbrowser.inek.org — aggregate, anonymised nationwide inpatient billing data
reported under §21 KHEntgG. This study used the annual DRG dataset for the **2023 data year**
("Datenlieferung DRG 2023 gruppiert nach 2024"). The browser releases only aggregate counts
and suppresses cells with fewer than five cases.

## Requirements

- Python 3.10+
- Packages in [`requirements.txt`](requirements.txt): `numpy`, `openpyxl`, `matplotlib`,
  `python-docx`

```bash
pip install -r requirements.txt
```

## Reproducing the analysis

1. Obtain a C71 age-stratified export from the InEK DatenBrowser and place the single `.xlsx`
   in `data/`. The exact queries and the expected worksheet layout are documented in
   [`data/README.md`](data/README.md).
2. From the repository root, run:

   ```bash
   python RUN_ALL.py
   ```

This regenerates, under your working copy:

- `derived_data/` — tidy CSV/JSON (counts, proportions, trend tests, effect sizes,
  Charlson-weighted comorbidity point score, suppression map);
- `figures/` — Figures 1–3 and Figure S1 (PNG + PDF);
- `tables.docx` — Tables 1–2;
- `supplement.docx` — Supplementary material (Tables S1–S6, RECORD checklist).

None of these outputs are committed; `.gitignore` excludes `data/`, `derived_data/`,
`figures/`, and generated documents.

## Repository layout

```
inek-c71-age-2026/
├── README.md              This file
├── SUMMARY.md             Detailed study overview (aims, methods, key results, limitations)
├── LICENSE                MIT
├── CITATION.cff           How to cite the analysis code
├── requirements.txt
├── study_meta.json        Reporting year and data basis (single source of truth)
├── RUN_ALL.py             Pipeline orchestrator
├── data/
│   └── README.md          How to obtain the InEK export (no data included)
└── scripts/
    ├── 01_extract_analyse.py     Extraction + core statistics (chi-square, Cochran-Armitage, Wilson CIs, FDR)
    ├── 08_charlson_index.py      Charlson-weighted comorbidity point score (Poisson trend)
    ├── 13_suppression.py         Map privacy-suppressed (<5) cells
    ├── 12_effects_sensitivity.py Risk differences, odds ratios per decade, Cramér's V, score sensitivity, dispersion
    ├── 02_figures.py             Figures 1–3
    ├── 14_cohort_figure.py       Figure S1 (cohort derivation)
    ├── 06_tables.py              Tables 1–2
    └── 07_supplement.py          Supplement (S1–S6, RECORD checklist)
```

## Statistical methods (brief)

Proportions with 95% Wilson confidence intervals; age-band association by Pearson chi-square;
monotone trend by the Cochran-Armitage test (age-band midpoint scores, with rank- and
alternative-score sensitivity analyses); Benjamini-Hochberg FDR within each outcome family;
effect sizes as risk differences (Newcombe CIs), odds ratios per decade (grouped-binomial
logistic trend), and Cramér's V; a Charlson-weighted comorbidity point score summarised by a
Poisson trend with a quasi-Poisson (overdispersion-adjusted) interval. All statistics are
implemented in pure Python/NumPy and are reproducible from a single export.

## Licence and citation

Code released under the MIT Licence ([`LICENSE`](LICENSE)). If you use it, please cite the
associated article and this repository ([`CITATION.cff`](CITATION.cff)). On acceptance the
repository will be archived on Zenodo and assigned a citable DOI.
