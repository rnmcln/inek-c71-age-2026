# Obtaining the input data

The source data are **not distributed** with this repository. They are publicly available from
the InEK DatenBrowser but may not be redistributed; the pipeline regenerates all results from
your own export.

## Primary source

InEK GmbH, **InEK DatenBrowser** — https://datenbrowser.inek.org
Aggregate, anonymised nationwide §21 KHEntgG inpatient data. Registration and login are
required. The browser aggregates only cells with **five or more** cases; smaller cells are
suppressed (blank).

This study used the annual DRG dataset for the **2023 data year**:
**"Datenlieferung DRG 2023 gruppiert nach 2024"** (left-hand menu → *Datenjahr 2023*).

## Queries used

Cohort is defined by the topographic diagnosis **C71** (all subcodes C71.0–C71.9). Two
diagnosis positions are needed:

1. **Principal-diagnosis cohort** — C71.0–C71.9 as **Hauptdiagnose** (principal diagnosis).
   Restricted to adults (age bands 18–29 … 80+). This yields the sex, in-hospital mortality
   (Entlassungsgrund 07 = Tod), and discharge-disposition tabulations. (For reference, the
   all-ages C71 principal-diagnosis count in 2023 is 23,498; the adult subset is 18,621.)
2. **C71-coded population** — C71.0–C71.9 as principal **or** secondary diagnosis
   (n = 23,594, adults). This is the denominator for the comorbidity (Charlson categories) and
   procedure (OPS) tabulations.

Codes should be verified per data year (code identifiers are year-specific): ICD-10-GM at
https://www.icd-code.de and OPS at https://www.icd-code.de/ops/code/OPS.html.

## Expected workbook layout

Place a single `.xlsx` in this `data/` folder. The pipeline (`scripts/01`, `08`, `13`) reads a
workbook with six worksheets, matching the DatenBrowser export used in the study:

| Worksheet | Contents |
|---|---|
| `Overview` | Case counts, sex, and discharge disposition by age band and diagnosis position (main-diagnosis and total columns) |
| `Discharge` | Sex-by-disposition cross-tabulation |
| `Charlson Comordity Index` | Charlson comorbidity-category counts by age band (C71-coded population) |
| `Diagnoses` | Secondary-diagnosis frequency table |
| `Übersicht-Prozeduren` | Procedure (OPS) frequency table, by code and age band |
| `Prozeduren` | Detailed procedure table |

The extraction scripts address specific rows/columns of this layout (age-band columns and
category/disposition/procedure rows). If your export differs in structure, align the worksheet
names and cell positions in `scripts/01_extract_analyse.py`, `scripts/08_charlson_index.py`,
and `scripts/13_suppression.py` to your workbook, or rebuild the workbook to match the layout
above. Age bands are, in order: 18–29, 30–39, 40–49, 50–54, 55–59, 60–64, 65–74, 75–79, 80+.

## Analysed codes

- **Comorbidity (Charlson categories):** other solid tumour (non-C71), malignant haematological
  disease, diabetes mellitus, dementia, heart failure, cerebrovascular disease, chronic
  pulmonary disease, peripheral arterial occlusive disease, connective tissue disease, renal
  failure / chronic kidney disease. Secondary neoplasms of the brain / other nervous system
  (C79.3, C79.4) are excluded from the tumour comorbidity in a primary brain-tumour cohort.
- **Procedures (OPS):** 3-200 native cranial CT; 3-800 native cranial MRI; 5-984 microsurgical
  technique; 5-989 fluorescence-guided surgery; 5-022.00 external ventricular drain; 5-988.x
  intraoperative navigation; 1-511.00/1-511.01 supratentorial stereotactic biopsy; 8-522.x
  inpatient high-voltage radiotherapy.
