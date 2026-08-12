# Study summary

**Age-stratified hospital care, comorbidity, and discharge outcomes in adults with malignant glioma in Germany: a nationwide analysis of administrative data.**

This document is a detailed overview of the study for readers of the analysis code. It states
what the analysis establishes, what it does not, and the key quantitative results. Full
methods and figures are in the published article; the code here regenerates every number from
a DatenBrowser export.

## Background and aim

Malignant gliomas (ICD-10-GM C71) are the most common malignant primary brain tumours and
predominantly affect older adults. Population-level data on how hospital care is distributed
across the adult age range in Germany are limited. The aim was to describe, descriptively,
age-stratified patterns of in-hospital mortality, discharge disposition, comorbidity, and
procedure coding in adults hospitalised with C71.

C71 is a **topographic** code: it identifies malignant neoplasms of the brain by site, not by
integrated histomolecular diagnosis. It is used here as an **administrative proxy** for
malignant glioma, and the cohort may include a minority of non-glioma malignant brain
tumours.

## Data source and cohorts

Aggregate, anonymised §21 KHEntgG inpatient data from the InEK DatenBrowser, annual DRG
dataset for the **2023 data year**. Two cohorts, with different denominators that are **not
comparable at the episode level**:

- **Principal-diagnosis cohort** — episodes with C71 as the principal (main) diagnosis, adults
  ≥18 years, **n = 18,621**. Used for sex, in-hospital mortality, and discharge disposition.
- **C71-coded population** — episodes with C71 as principal *or* secondary diagnosis,
  **n = 23,594**. The denominator to which the comorbidity and procedure tabulations are keyed.

The unit of observation is the discharge episode, not the patient. Cells with fewer than five
cases are suppressed in the source and are shown as `<5` (counts) or `<0.X` (percentages, an
upper bound).

## Statistical approach

Percentages recomputed from raw counts; proportions with 95% Wilson confidence intervals;
age-band association by Pearson chi-square; monotone trend by the Cochran-Armitage test using
age-band midpoint scores, with rank-score and alternative open-band-score sensitivity
analyses. Benjamini-Hochberg FDR was applied within each outcome family (disposition,
comorbidity, procedures). Effect sizes are reported to complement significance testing at
large n: absolute risk differences (Newcombe CIs), odds ratios per decade of age
(grouped-binomial logistic trend), and Cramér's V for the global contingency tests. Overall
comorbidity burden is summarised by a **Charlson-weighted comorbidity point score** per
episode (a weighted sum of comorbidity indicators using Charlson weights, not a patient-level
Charlson index), with a Poisson trend and a quasi-Poisson (overdispersion-adjusted) interval.
Analyses are descriptive; the aggregate data support no individual-level adjustment,
multivariable modelling, or causal inference.

## Key results

**Age and sex.** The modal band by count was 65–74 years (24.5%), partly reflecting its
greater (10-year) width; expressed per year of age, episode density was highest around 60–64
years. 41.8% of episodes were in patients aged ≥65 and 17.3% in those aged ≥75. Because bands
are of unequal width, absolute counts index hospital workload, not age-specific risk or
incidence. Males predominated overall (57.5%); the male fraction was nonlinear across age,
rising into early middle age and attenuating to the lowest proportion in the oldest band
(50.6%; Cramér's V = 0.06).

**Mortality and discharge.** In-hospital mortality was 6.8% overall and rose from 3.0% (18–29
years) to 13.2% (≥80 years); risk difference 10.2 percentage points (95% CI 8.1–12.2), odds
ratio 1.32 per decade (1.26–1.37). Discharge home fell from 89.7% to 54.9% (risk difference
−34.8 pp; OR 0.72 per decade). Non-home discharge increased with age: nursing-home transfer OR
1.94, hospice transfer OR 1.26, inter-hospital transfer OR 1.27 per decade. The overall
age-by-disposition association was strong in significance but modest in standardised magnitude
(Cramér's V = 0.11). Among episodes in patients aged ≥65 (n = 7,792), 9.3% ended in death,
5.0% in nursing-home transfer, 4.2% in hospice transfer, and 11.9% in inter-hospital transfer;
among those aged ≥75 (n = 3,227), the corresponding proportions were 11.7%, 7.5%, 4.9%, and
13.2%.

**Comorbidity.** Coded comorbidity accumulated with age: diabetes 0.7%→22.7%, renal failure
below threshold→14.3%, dementia 0.5%→9.9%, heart failure below threshold→9.8%, cerebrovascular
disease 0.6%→8.9% (all FDR-adjusted trend p < 0.001). The Charlson-weighted comorbidity point
score rose from 0.13 (youngest) to 0.95 (oldest); overall mean 0.47; Poisson rate ratio 1.46
per decade (quasi-Poisson 95% CI 1.33–1.59, accounting for overdispersion).

**Procedures.** Native cranial CT coding rose from 33.2% to 59.5% with age (MRI showed no
gradient); microsurgical-technique coding fell from 28.2% to 22.0% and stereotactic-biopsy
coding rose from 3.4% to 7.8%; external ventricular drainage fell from 2.9% to 0.6%; inpatient
high-voltage radiotherapy coding rose from 4.6% to 14.5%. The export has no direct
tumour-resection denominator, so these coding patterns are compatible with, but do not
establish, less frequent resection and more frequent biopsy in older age bands.

## What the analysis does not establish

The data are aggregate, cross-sectional, and episode-level. They cannot support patient-level
rates, survival estimates, causal claims, or age-specific incidence; comorbidity and mortality
are measured in overlapping but non-identical cohorts and cannot be linked at the episode
level; C71 does not identify histology, molecular subtype, or WHO grade; readmissions and
selection into the inpatient cohort may accentuate the observed gradients; suppressed cells
were treated as zero only in the comorbidity-point sum. Reporting follows the RECORD extension
of STROBE (checklist in the supplement generated by the pipeline).
