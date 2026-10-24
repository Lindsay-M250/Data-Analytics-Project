# Data-Analytics-Project
Project C: Are EU regions converging?  Question: Is the income and employment gap between rich and poor regions closing, and which regions don’t follow the pattern?
# Data-Analytics-Project

**Project C: Are EU regions converging?**

> Is the income and employment gap between rich and poor regions closing, and which regions don't follow the pattern?

Final project for Data Analytics (MDE-CO-02, Fall 2026), Constructor University. Thirty years of EU cohesion funding: we test whether NUTS2 regions are converging on income and employment, and identify which groups of regions behave alike and which do not follow the overall pattern.

## Team

- Lindsay
- Bongolethu
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
| `data/nama_10r_2gdp.json` | Unfiltered GDP table from the Eurostat API (all units) |
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
| Population on 1 January | `demo_r_d2jan` | NUTS2 | 1990-2025 | **not downloaded yet** |

- **Download date:** 17 October 2026. Eurostat revises its tables, so if a file is downloaded again, change the date here and say which file.
- **Format:** the TSV files are wide (one column per year). Each value can carry a flag, for example `45.1 b`.
- **Flags:** `b` = break in time series, `p` = provisional, `u` = low reliability, `e` = estimated, `d` = definition differs. We keep them when converting the files, because they matter for what we trust.

### What we know about the data so far

- The GDP table has 285 NUTS2 regions with euro-per-head values. 41 are outside the EU (Turkey 26, Norway 6, Serbia 4, Albania 3, Montenegro 1, North Macedonia 1). The EU27 has 244.
- The number of regions with a GDP value changes between years (255 to 285), so we cannot compare the same regions over time without checking.
- The sector table is at NUTS3 level (5-character codes) and has to be summed to NUTS2 (first 4 characters) before joining. Values are amounts, so summing is valid. Rates and per-head figures must be recomputed from totals, never summed.

## Codebook

Ten fields explained in our own words. Each person fills in the fields of their own table, and we check each other's.

| Field | Appears in | What it means (own words) |
|---|---|---|
| `freq` | all tables | |
| `unit` | all tables | |
| `geo` | all tables | |
| `TIME_PERIOD` (year columns) | all tables | |
| `value` | all tables | |
| flag (letter after a value) | all tables | |
| `sex` | employment, unemployment | |
| `age` | employment, unemployment | |
| `isced11` | unemployment | |
| `nace_r2` | sector GVA | |

## Decision log

Every choice about the data is made by the whole group and written here with the reason.

| # | Decision | Options | Our choice | Why | Status |
|---|---|---|---|---|---|
| 1 | Time window | e.g. 2000-2024 (where all tables overlap) | | | open |
| 2 | GDP unit | euro per head, PPS per head, or both as a check | | | open |
| 3 | Employment measure | age group (15-64, 20-64, ...), sexes together or separate | | | open |
| 4 | Youth unemployment | ages 15-24 or 15-29 | | | open |
| 5 | Sector grouping | which of the 15 sector codes to keep, how to turn values into shares | | | open |
| 6 | Which countries | EU27 only (244 regions) or all 285 | | | open |
| 7 | Missing data | drop regions with gaps, or keep and work around | | | open |

## Processing log

One line every time we change or convert the data.

| Date | Who | What we did | Input | Output |
|---|---|---|---|---|
| 2026-10-17 | | Downloaded the unfiltered tables from Eurostat | Eurostat | `data/raw_data/` |
| | | | | |

## Limitations log

Add every limitation we find, and what would change our conclusion. This feeds the limitations section of the report.

- NUTS boundaries were redrawn in 2013, 2016 and 2021, so series have to be stitched together.
- GDP per head is distorted in commuter regions: output is counted where people work, population where they live.
- Euro and PPS give different answers; we must say which we used and why.
- Some regions have gaps in some years.
- Some values are flagged provisional or low reliability.
- The GDP table includes 41 non-EU regions.

## Work split

| Person | Table | Before the data freeze (until 6 Nov) | After the freeze (7 Nov onwards) |
|---|---|---|---|
| Rethabile | Population, plus joining all tables | Downloads the population table and writes its conversion code. Proposes the filters with the reason for each decision. Writes the script that joins all the tables, matches the regions and checks the region counts. Keeps the processing log | Works with Badusha on Question 3, helps with the limitations section, and re-runs the whole project from scratch to check it works |
| Lindsay | GDP | Codebook, conversion code for GDP, reviews Rethabile's proposal for the GDP unit and time window, counts regions per year, checks the joined result. Keeps AI_Usage.md and looks after the README | Question 1: is the gap between regions getting smaller? |
| Bongolethu | Employment | Codebook, conversion code for employment, reviews Rethabile's proposal for the age group and sex choice, checks the joined result. Keeps the decision log | Question 2: do poorer regions grow faster? |
| Winnie | Youth unemployment | Codebook, conversion code for youth unemployment, reviews Rethabile's proposal (15-24 vs 15-29), checks the joined result | Question 4: where do the two tests disagree? Puts the presentation together |
| Badusha | Sector GVA | Codebook, conversion code for the sector table including the NUTS3 to NUTS2 sum and the shares, reviews Rethabile's proposal on which sectors to keep, checks the joined result | Question 3: which regions behave alike? (with Rethabile) |

Everyone also writes the data and methods section of the report for their own table, the results section for their own question, and the slides for their own part. The first slide of the presentation says who did what.

## How to re-run everything

1. Clone the repository: `git clone https://github.com/Lindsay-M250/Data-Analytics-Project.git`
2. Open the folder in Positron.
3. Install the required Python packages (list to be added once the analysis uses them).
4. Open `report.qmd` and click **Render**, or run `quarto render report.qmd` in the terminal. This runs all the code from the raw files and creates `report.html`.

## Working rules

- Raw files in `data/raw_data/` are never edited.
- All cleaning and merging is done in code, not by hand.
- Every decision goes in the decision log, every data change in the processing log, every limitation in the limitations log.
- Every use of AI goes in `AI_Usage.md`.
- Run `git pull` before you start and `git push` when you finish, so nobody overwrites anyone's work.