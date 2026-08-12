#!/usr/bin/env python3
"""Run the full analysis pipeline on an InEK DatenBrowser export.

Place a single C71 age-stratified export (.xlsx) in data/ (see data/README.md),
then run from the repository root:

    python RUN_ALL.py

Outputs are written to derived_data/ (tidy CSV/JSON), figures/ (PNG/PDF), and
tables.docx / supplement.docx. No input or derived data are distributed with
this repository; everything is regenerated locally from your own export.
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
os.makedirs("derived_data", exist_ok=True)
os.makedirs("figures", exist_ok=True)

STEPS = [
    "01_extract_analyse.py",     # extraction + core statistics
    "08_charlson_index.py",      # Charlson-weighted comorbidity point score
    "13_suppression.py",         # map privacy-suppressed cells (<5)
    "12_effects_sensitivity.py", # effect sizes, score sensitivity, dispersion
    "02_figures.py",             # Figures 1-3
    "14_cohort_figure.py",       # Figure S1 (cohort derivation)
    "06_tables.py",              # Tables 1-2
    "07_supplement.py",          # Supplement (S1-S6, RECORD checklist)
]

for s in STEPS:
    print(f"\n=== {s} ===")
    r = subprocess.run([sys.executable, os.path.join("scripts", s)])
    if r.returncode != 0:
        sys.exit(f"step {s} failed")

print("\nDone. See derived_data/, figures/, tables.docx, and supplement.docx.")
