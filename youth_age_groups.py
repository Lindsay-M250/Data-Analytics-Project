# youth_age_groups.py
# Winnie's part (Question 4): make TWO clean youth-unemployment files from the RAW Eurostat file:
#   data/clean/youth_15_24.csv   (ages 15-24)
#   data/clean/youth_15_29.csv   (ages 15-29)
# Everything below the "SETTINGS" block is copied from the team's "Cleaning code 2.py", so both files are
# cleaned with EXACTLY the same rules as the rest of the project. Only the age group differs.
#
# Run from the project folder (the one that contains data/ and report.qmd):
#     python youth_age_groups.py

import os
import re

import pandas as pd

# ---- SETTINGS ---------------------------------------------------------------------------
RAW_FILE = "data/raw_data/estat_lfst_r_lfu3rt.tsv"       # raw unemployment file (never edited)
OUT_DIR = "data/clean"
FIRST_YEAR, LAST_YEAR = 2000, 2024
AGE_GROUPS = {"youth_15_24": "Y15-24", "youth_15_29": "Y15-29"}   # output name -> Eurostat age code
EU27 = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
        "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]
# Old region codes that were only renamed (same copy as the team script)
RENAMES = {"SI01": "SI03", "SI02": "SI04", "NL31": "NL35", "NL33": "NL36"}
# -----------------------------------------------------------------------------------------

VALUE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]*)\s*$")


def read_raw(path, filters):
    """Read the wide Eurostat file and turn it into a long table: one row per region and year."""
    raw = pd.read_csv(path, sep="\t", dtype=str)
    raw.columns = [c.strip() for c in raw.columns]
    first = raw.columns[0]                                   # "freq,isced11,sex,age,unit,geo\TIME_PERIOD"
    dims = first.split("\\")[0].split(",")                   # the six label columns
    raw[dims] = raw[first].str.split(",", expand=True)       # split the first column into six columns
    raw = raw.drop(columns=[first])
    for col, wanted in filters.items():                      # keep only the rows we want
        raw = raw[raw[col] == wanted]
    long = raw.melt(id_vars=dims, var_name="year", value_name="cell")   # one column per year -> one row per year
    long["year"] = long["year"].astype(int)
    parsed = long["cell"].str.extract(VALUE_RE)              # split "45.1 b" into number and flag
    long["value"] = pd.to_numeric(parsed[0])
    long["flag"] = parsed[1].fillna("")                      # the flag letter is kept
    return long.drop(columns=["cell"])


def tidy(long, name, keep=("geo", "year")):
    """Region and year filters, rename old codes, duplicate check, tidy column names."""
    df = long
    df = df[df["geo"].str.len() == 4]                        # NUTS2 codes have 4 characters
    df = df[df["geo"].str[:2].isin(EU27)]                    # EU27 only
    df = df[~df["geo"].str.endswith(("ZZ", "XX"))]           # extra-regio is not a real region
    df = df[df["year"].between(FIRST_YEAR, LAST_YEAR)]
    df = df.dropna(subset=["value"])                         # ":" in the raw file = no value
    key = list(keep)
    df = df.assign(_renamed=df["geo"].isin(RENAMES.keys()),
                   geo=df["geo"].replace(RENAMES))
    n_overlap = int(df.duplicated(key).sum())
    if n_overlap:                                            # new code wins over the old code
        df = df.sort_values("_renamed").drop_duplicates(key, keep="first")
    assert int(df.duplicated(key).sum()) == 0, f"{name}: a region-year appears twice - a filter is missing"
    df = df.rename(columns={"value": "youth_unemp", "flag": "youth_unemp_flag"})
    return df[key + ["youth_unemp", "youth_unemp_flag"]].sort_values(key).reset_index(drop=True)


os.makedirs(OUT_DIR, exist_ok=True)
for name, age in AGE_GROUPS.items():
    # filters: percent, both sexes, all education levels, ONE age group
    long = read_raw(RAW_FILE, {"unit": "PC", "sex": "T", "age": age, "isced11": "TOTAL"})
    table = tidy(long, name)
    table.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: {len(table):,} rows | {table['geo'].nunique()} regions | "
          f"years {table['year'].min()}-{table['year'].max()}")
