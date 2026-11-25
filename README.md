# Data-Analytics-Project

**Project C: Are EU regions converging?**

> Between 2000 and 2024, did EU27 NUTS2 regions converge in GDP per head (PPS) and employment rate (ages 20-64), and which groups of regions did not follow the pattern?

Final project for Data Analytics (MDE-CO-02, Fall 2026), Constructor University. Thirty years of EU cohesion funding: we test whether NUTS2 regions are converging on income and employment, and identify which groups of regions behave alike and which do not follow the overall pattern.

## Team

- Lindsay
- Bhongolethu
- Winnie
- Rethabile
- Badusha

## What we submit

- **Report** (`report.qmd`, rendered to `report.html`): descriptions, tables, figures and code. Submitted at least two days before the day we present.
- **Presentation:** 10 minutes plus 5 minutes of Q&A. The first slide states who did what (see the work split below).
- **AI use declared** in `AI_Usage.md`: the prompt, the model and its configuration, and the computational effort or cost where we can measure it.

## How it is graded

| Component | Weight |
|---|---|
| Data preparation and reproducibility (documented steps, re-runnable pipeline) | 15% |
| Method choice and execution | 20% |
| Interpretation of results (what the output says, not a restatement of numbers) | 30% |
| Limitations and what would change the conclusion | 20% |
| Communication (clear to a non-technical reader) | 15% |

## Research questions

1. Is the spread between regions narrowing year on year?
2. Do poorer regions grow faster than richer ones?
3. Which groups of regions behave alike, and is that geography or industrial structure?
4. Where do the two convergence tests disagree, and which one do we believe?

## Repository structure

| Path | What it is |
|---|---|
| `README.md` | This file: overview, data, decisions, logs, how to re-run |
| `data/raw_data/` | Unfiltered Eurostat downloads (TSV), exactly as downloaded. **Never edit these.** |
| `clean_data.py` | Cleaning script: reads `data/raw_data/`, writes the cleaned tables to `data/clean/` |
| `data/clean/` | Cleaned tables (one CSV per topic), created by `clean_data.py`. Also `coverage.csv` (how many regions are complete) and `region_code_renames.csv` |
| `Archive/` | First cleaning notebook and its output files (`Project_*_EU27.csv`). Kept for reference only; nothing reads them any more |
| `report.qmd` | Analysis: code, graphs, interpretation and conclusions |
| `report.html` | Rendered report (created by rendering `report.qmd`) |
| `AI_Usage.md` | Log of AI prompts, model/configuration and computational effort |

## Data

All data comes from Eurostat (open data). Every table was downloaded **unfiltered**, so every filter is a documented decision of ours (see the decision log).

| Table | Eurostat code | Level | Years | File |
|---|---|---|---|---|
| GDP (several units, e.g. euro and PPS per head) | `nama_10r_2gdp` | NUTS2 | 2000-2024 | `data/raw_data/estat_nama_10r_2gdp.tsv` |
| Employment rate (by sex and age group) | `lfst_r_lfe2emprt` | NUTS2 | 1999-2025 | `data/raw_data/estat_lfst_r_lfe2emprt.tsv` |
| Unemployment rate (by sex, age group, education) | `lfst_r_lfu3rt` | NUTS2 | 1999-2025 | `data/raw_data/estat_lfst_r_lfu3rt.tsv` |
| Gross value added by sector | `nama_10r_3gva` | NUTS3 | 2000-2024 | `data/raw_data/estat_nama_10r_3gva.tsv` |
| Population on 1 January | `demo_r_d2jan` | NUTS2 | 1990-2025 | `data/raw_data/estat_demo_r_d2jan.tsv` |

- **Download date:** 17 October 2026. Eurostat revises its tables, so if a file is downloaded again, change the date here and say which file.
- **Format:** the TSV files are wide (one column per year). Each value can carry a flag, for example `45.1 b`.
- **Flags:** `b` = break in time series, `p` = provisional, `u` = low reliability, `e` = estimated, `d` = definition differs. We keep them when converting the files, because they matter for what we trust.

- **Youth unemployment files:** `clean_data.py` writes `data/clean/youth_15_24.csv` (ages 15-24, the main measure) and `data/clean/youth_15_29.csv` (ages 15-29, the check). Both use the same filters (percent, both sexes, all education levels) and region rules; only the age group differs.

### What we know about the data so far

- The GDP table has 285 NUTS2 regions with euro-per-head values. 41 are outside the EU (Turkey 26, Norway 6, Serbia 4, Albania 3, Montenegro 1, North Macedonia 1). The EU27 has 244.
- The number of regions with a GDP value changes between years (255 to 285), so we cannot compare the same regions over time without checking.
- The sector table is at NUTS3 level (5-character codes) and has to be summed to NUTS2 (first 4 characters) before joining. Values are amounts, so summing is valid. Rates and per-head figures must be recomputed from totals, never summed.

## Codebook

The ten fields of the raw Eurostat files, and what they mean (draft in plain words: each person can edit the fields of their own table).

| Field | Appears in | What it means (own words) |
|---|---|---|
| `freq` | all tables | How often the value is measured. Always `A` = annual |
| `unit` | all tables | What the number is measured in, for example `PPS_EU27_2020_HAB` (PPS per head), `EUR_HAB` (euro per head), `PC` (percent), `NR` (number of people), `CP_MEUR` (million euro, current prices) |
| `geo` | all tables | The region code. Four characters (for example `AT11`) = a NUTS2 region; the first two letters are the country |
| `TIME_PERIOD` (year columns) | all tables | The year of the value. In the raw files there is one column per year; in our cleaned files the column is called `year` |
| `value` | all tables | The number itself, for example GDP per head or an employment rate. `:` in the raw file means missing |
| flag (letter after a value) | all tables | A letter after the number that says how far to trust it: `b` break in series, `p` provisional, `u` low reliability, `e` estimated, `d` definition differs. Kept in the column `<name>_flag` of the cleaned files |
| `sex` | employment, unemployment | `T` = total (both sexes), `F` = female, `M` = male. We use `T` |
| `age` | employment, unemployment | The age group of the rate, for example `Y20-64` (employment) and `Y15-24` (youth unemployment). `TOTAL` in population = all ages |
| `isced11` | unemployment | The education level of the people counted. We use `TOTAL` (all levels) |
| `nace_r2` | sector GVA | The industry. We use the six broad groups A, B-E, F, G-J, K-N and O-U, and `TOTAL` |

Fields we create in `clean_data.py`: `gdp_pps` and `gdp_eur` (GDP per head in PPS and in euro), `gva_meur` (gross value added in million euro), `gva_pc` (gross value added per head: total x 1,000,000 / population), `share_pct` (sector value as a percentage of total gross value added).

## Decision log

Every choice about the data is made by the whole group and written here with the reason. "Proposed" means a first draft that anyone can change at the group meeting.

| # | Decision | Options | Our choice | Why | Status |
|---|---|---|---|---|---|
| 1 | Time window | 2000-2024, or stop at 2023 | 2000-2024 | All tables overlap in these years. The 2024 GDP values are provisional, so we flag them and check that results hold without 2024 | agreed |
| 2 | GDP unit | Euro per head, PPS per head, or both | PPS per head (`PPS_EU27_2020_HAB`) as the main measure, euro per head (`EUR_HAB`) as a robustness check | PPS adjusts for price differences between countries, so it compares living standards better. The briefing says we must state which we used and why | agreed |
| 3 | Employment measure | Ages 15-64, 20-64, or others; both sexes or separate | Ages 20-64, both sexes (`Y20-64`, `T`) | 20-64 is the age group of the EU employment target, so it is the standard measure for comparing regions | agreed |
| 4 | Youth unemployment | Ages 15-24 or 15-29 | Ages 15-24, both sexes, all education levels (`Y15-24`, `T`, `TOTAL`), with 15-29 as a check | 15-24 is the standard headline definition of youth unemployment, so our numbers can be compared with other sources | agreed |
| 5 | Sector grouping | 15 sector codes, some inside others | The six broad sectors that do not overlap: A, B-E, F, G-J, K-N, O-U. Shares of total gross value added (`TOTAL`) | These six add up to the total, so shares are consistent. The overlapping codes (for example C inside B-E) would count the same value twice | agreed |
| 6 | Which countries | EU27 only (244 regions) or all 285 | EU27 only (244 regions) | Our question is about EU regions and EU cohesion funding. Turkey, Norway, Serbia, Albania, Montenegro and North Macedonia are not EU members | agreed |
| 7 | Missing data | Drop regions with gaps, or keep and work around | Keep regions with a GDP value in both 2000 and 2024 and list how many we lose and which | Convergence tests compare the start and end of the period, so a region needs both | agreed |
| 8 | Old region codes | Recode all, recode renames only, or leave as they are | Recode pure renames only (Slovenia SI01/SI02, the Netherlands NL31/NL33, nine Greek codes in population). Splits and merges are left as gaps | A rename is the same area, so the history can be joined safely. A split would need population weights or invented values | proposed |
| 9 | Eurostat flags | Keep or drop | Keep, in a column next to each value | Flags such as `b` (break in series) and `p` (provisional) matter for what we trust | proposed |
| 10 | One cleaning script | Rethabile's notebook or `clean_data.py` | `clean_data.py`, which includes all of his calculations | It starts from the raw files in the repo and produces the same values as his notebook, plus flags and region renames | proposed |

### Big city regions (commuter check, Question 1)

GDP per head is distorted in commuter regions, because output is counted where people work and population where they live. For the robustness check we removed these ten regions:

| Code | Region |
|---|---|
| AT13 | Vienna |
| BE10 | Brussels |
| DE60 | Hamburg |
| DE30 | Berlin |
| CZ01 | Prague |
| SK01 | Bratislava |
| FR10 | Île-de-France (Paris) |
| HU11 | Budapest |
| PL91 | Warsaw area |
| RO32 | Bucharest-Ilfov |

Why: these are the capital and large city regions with the biggest commuter inflows. The list is our own choice, not based on a formal commuter measure. Everyone should use the same list when they check commuter effects. Result for Question 1: removing them makes the fall in spread slightly larger (sample A −34%, B −28%, against −31% and −26% with them).

## Limitations log

Add every limitation we find, and what would change our conclusion. This feeds the limitations section of the report.

- NUTS boundaries were redrawn in 2013, 2016 and 2021, so series have to be stitched together.
- GDP per head is distorted in commuter regions: output is counted where people work, population where they live.
- Euro and PPS give different answers; we must say which we used and why.
- Some regions have gaps in some years.
- Some values are flagged provisional or low reliability.
- The GDP table includes 41 non-EU regions.
- Different coverage by indicator - sample is not identical
- GVA is in current prices, GDP PPS is in PPS
- GVA per capita depends on population merge
- Sector data was incomplete for some region-years
- Extra-regio ZZ regions are not real regions
- NUTS-2 boundaries changed over time
- Region splits and merges are not recoded (Hungary HU10, Lithuania LT00, Croatia HR04, Ireland IE01/IE02, Portugal PT16-18), so those regions have gaps in employment, youth unemployment and population.
- NL31 -> NL35 and NL33 -> NL36 are treated as the same regions, although a few municipalities moved between them.
- Only 224 of 244 regions have a GDP value in every year; the others are Romania (8), Belgium (11) and one French region.
- Only 90 of 248 regions have youth unemployment in all 25 years.
- GVA per head loses 388 region-years where no population value exists.

- Youth unemployment: only 123 of 248 regions (ages 15-24) and 151 of 251 regions (ages 15-29) have a value in both 2000 and 2024, so the catching-up test covers about half of the regions.
- About 20% of the 15-24 values (11% of the 15-29 values) are flagged `u` (low reliability).
- The youth spread line jumps for data reasons: Eurostat flags 218 values in 2005 as a break in the series, and from 2020 none of the 20 German regions that had a value in 2019 has one.
- The youth spread test depends on the end year: in 2019 the spread was back at its 2000 level.
- The youth catching-up slope may be too strong because of noisy starting values (not tested).
- We did not test whether the 15-24 and 15-29 slopes differ significantly.
- The sub-periods used in Question 4 (2008 and 2013) are our own choice.

## Work split

| Person | Table | Before the data freeze (until 6 Nov) | After the freeze (7 Nov onwards) |
|---|---|---|---|
| Rethabile | Population, plus joining all tables | Downloads the population table and writes its conversion code. Reviews and adjusts the proposed filters, keeping a reason for each decision. Writes the script that joins all the tables, matches the regions and checks the region counts. Keeps the processing log | Works with Badusha on Question 3, helps with the limitations section, and re-runs the whole project from scratch to check it works |
| Lindsay | GDP | Codebook, conversion code for GDP, reviews Rethabile's proposal for the GDP unit and time window, counts regions per year, checks the joined result. Keeps AI_Usage.md and looks after the README | Question 1: is the gap between regions getting smaller? |
| Bhongolethu | Employment | Codebook, conversion code for employment, reviews Rethabile's proposal for the age group and sex choice, checks the joined result. Keeps the decision log | Question 2: do poorer regions grow faster? |
| Winnie | Youth unemployment | Codebook, conversion code for youth unemployment, reviews Rethabile's proposal (15-24 vs 15-29), checks the joined result | Question 4: where do the two tests disagree? Puts the presentation together |
| Badusha | Sector GVA | Codebook, conversion code for the sector table including the NUTS3 to NUTS2 sum and the shares, reviews Rethabile's proposal on which sectors to keep, checks the joined result | Question 3: which regions behave alike? (with Rethabile) |

Everyone also writes the data and methods section of the report for their own table, the results section for their own question, and the slides for their own part. The first slide of the presentation says who did what.

## How to re-run everything

1. Clone the repository: `git clone https://github.com/Lindsay-M250/Data-Analytics-Project.git`
2. Open the folder in Positron.
3. Use Python 3.13 (newer versions may lack ready-made packages) and install the packages: `pandas numpy matplotlib scipy scikit-learn pyyaml nbformat nbclient ipykernel`. With uv: `uv venv --python 3.13 .venv313`, then `uv pip install --python .\.venv313\Scripts\python.exe pandas numpy matplotlib scipy scikit-learn pyyaml nbformat nbclient ipykernel`.
4. Run `python clean_data.py` in the project folder. This reads `data/raw_data/` and writes `data/clean/`.
5. Run `quarto render report.qmd` (or click **Render** in Positron). This runs all the analysis code on the cleaned tables and creates `report.html`.

## Working rules

- Raw files in `data/raw_data/` are never edited.
- All cleaning and merging is done in code, not by hand.
- Every decision goes in the decision log, every data change in the processing log, every limitation in the limitations log.
- Every use of AI goes in `AI_Usage.md`.
- Run `git pull` before you start and `git push` when you finish, so nobody overwrites anyone's work.