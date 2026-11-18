
import os
import re

import numpy as np
import pandas as pd

RAW_DIR = "data/raw_data"
OUT_DIR = "data/clean"

# ---- Decisions (edit here, then re-run) -------------------------------------------------
FIRST_YEAR, LAST_YEAR = 2000, 2024                       # period
YOUTH_AGE = "Y15-24"                                     # CHANGE 7: one setting; "Y15-29" is the alternative (keeps ~28 more regions)
EMP_AGE = "Y20-64"                                       # employment rate age group (main measure)
EMP_ALT_AGE = "Y15-64"                                   # robustness check for Question 2 -> data/clean/emp_15_64.csv
EU27 = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES", "FI", "FR", "HR", "HU",
        "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]
# CHANGE 4: old region codes that are only renamed (same area, new code). Splits and merges are NOT recoded:
# HU10, LT00, HR04, IE01/IE02 and PT16-18 are left as they are and listed in the limitations.
# For discussion: NL31->NL35 and NL33->NL36 are "near-renames" (a few municipalities moved), so the team
# must agree to treat them as the same region. If not, delete those two lines.
RENAMES = {
    "SI01": ("SI03", "rename"),       # NUTS 2013 -> 2016
    "SI02": ("SI04", "rename"),
    "NL31": ("NL35", "near-rename"),  # NUTS 2016 -> 2021; a few municipalities moved between NL35 and NL36
    "NL33": ("NL36", "near-rename"),
    "EL11": ("EL51", "rename"),       # Greece, NUTS 2010 -> 2013 (appear in the population table only)
    "EL12": ("EL52", "rename"),
    "EL13": ("EL53", "rename"),
    "EL14": ("EL61", "rename"),
    "EL21": ("EL54", "rename"),
    "EL22": ("EL62", "rename"),
    "EL23": ("EL63", "rename"),
    "EL24": ("EL64", "rename"),
    "EL25": ("EL65", "rename"),
}
# ------------------------------------------------------------------------------------------

VALUE_RE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]*)\s*$")


# CHANGE 1: everything below starts from the raw files in data/raw_data
def read_raw(path, filters):
    """Read one wide Eurostat TSV and return a long table: geo, year, value, flag (+ other columns).

    `filters` = {column: wanted value} applied BEFORE reshaping (keeps big files fast).
    """
    raw = pd.read_csv(path, sep="\t", dtype=str)
    raw.columns = [c.strip() for c in raw.columns]
    first = raw.columns[0]                                  # e.g. "freq,unit,sex,age,geo\TIME_PERIOD"
    dims = first.split("\\")[0].split(",")                  # e.g. ["freq","unit","sex","age","geo"]
    raw[dims] = raw[first].str.split(",", expand=True)
    raw = raw.drop(columns=[first])

    for col, wanted in filters.items():
        raw = raw[raw[col] == wanted]

    long = raw.melt(id_vars=dims, var_name="year", value_name="cell")
    long["year"] = long["year"].astype(int)
    parsed = long["cell"].str.extract(VALUE_RE)             # ":" (missing) does not match -> NaN
    long["value"] = pd.to_numeric(parsed[0])
    long["flag"] = parsed[1].fillna("")                     # CHANGE 2: the flag letter is kept, not thrown away
    return long.drop(columns=["cell"])


def tidy(long, name, keep=("geo", "year")):
    """Region and year filters, duplicate check, tidy column names."""
    df = long
    df = df[df["geo"].str.len() == 4]                       # NUTS2 codes have 4 characters
    df = df[df["geo"].str[:2].isin(EU27)]                   # EU27 only
    df = df[~df["geo"].str.endswith(("ZZ", "XX"))]          # extra-regio (ZZ); CHANGE 6: FRXX and HUXX (XX) are not regions
    df = df[df["year"].between(FIRST_YEAR, LAST_YEAR)]
    df = df.dropna(subset=["value"])                        # ":" in the raw file = no value
    key = list(keep)

    # CHANGE 4 + 5: old code -> new code, with a duplicate check.
    # If the new code already has a value in that year (this happens in the
    # population table for NL31/NL35 and NL33/NL36), the value under the new code is kept and the
    # old-code row is dropped. Any other duplicate is an error.
    df = df.assign(_renamed=df["geo"].isin(RENAMES.keys()),
                   geo=df["geo"].replace({old: new for old, (new, _) in RENAMES.items()}))
    clash = df[df.duplicated(key, keep=False)]
    assert (clash.groupby(key)["_renamed"].nunique() == 2).all() if len(clash) else True, \
        f"{name}: duplicate region-years that do not come from a renamed code - a filter is missing"
    n_overlap = int(df.duplicated(key).sum())
    if n_overlap:
        df = df.sort_values("_renamed").drop_duplicates(key, keep="first")
        print(f"{name}: {n_overlap} rows with an old code dropped, because the new code already has a value that year")
    dupes = int(df.duplicated(key).sum())               # CHANGE 5: stop instead of silently keeping the first
    assert dupes == 0, f"{name}: {dupes} region-years appear twice - a filter is missing"

    df = df.rename(columns={"value": name, "flag": name + "_flag"})
    cols = key + [name, name + "_flag"]
    return df[cols].sort_values(key).reset_index(drop=True)


def path(name):
    return os.path.join(RAW_DIR, name)


tables = {}

# CHANGE 3: GDP per head. PPS is the main measure (gdp_pps); euro per head (gdp_eur) is kept for the robustness check
gdp_pps = tidy(read_raw(path("estat_nama_10r_2gdp.tsv"), {"unit": "PPS_EU27_2020_HAB"}), "gdp_pps")
gdp_eur = tidy(read_raw(path("estat_nama_10r_2gdp.tsv"), {"unit": "EUR_HAB"}), "gdp_eur")
tables["gdp"] = gdp_pps.merge(gdp_eur, on=["geo", "year"], how="outer").fillna({"gdp_pps_flag": "", "gdp_eur_flag": ""})

# Employment rate, both sexes, ages 20-64, percent
tables["emp"] = tidy(read_raw(path("estat_lfst_r_lfe2emprt.tsv"),
                              {"unit": "PC", "sex": "T", "age": EMP_AGE}), "emp_rate")

# Employment rate, both sexes, ages 15-64: only used as a robustness check of the age-group decision (Question 2).
# Same raw file, same filters and same region rules as the main table; only the age group differs.
tables["emp_15_64"] = tidy(read_raw(path("estat_lfst_r_lfe2emprt.tsv"),
                                    {"unit": "PC", "sex": "T", "age": EMP_ALT_AGE}), "emp_rate")

# Youth unemployment rate, both sexes, all education levels, percent
tables["youth"] = tidy(read_raw(path("estat_lfst_r_lfu3rt.tsv"),
                                {"unit": "PC", "sex": "T", "age": YOUTH_AGE, "isced11": "TOTAL"}), "youth_unemp")

# Gross value added by sector, current prices, million euro (all sectors, so sector shares can be built later)
gva = read_raw(path("estat_nama_10r_3gva.tsv"), {"unit": "CP_MEUR"}).rename(columns={"nace_r2": "sector"})
tables["gva"] = tidy(gva, "gva_meur", keep=("geo", "year", "sector"))

# Population on 1 January, both sexes, all ages (raw file added later; skipped if it is not there yet)
pop_path = path("estat_demo_r_d2jan.tsv")
if os.path.exists(pop_path):
    tables["pop"] = tidy(read_raw(pop_path, {"unit": "NR", "sex": "T", "age": "TOTAL"}), "pop")
else:
    print("NOTE: population file not found, skipped:", pop_path)

# FROM RETHABILE (his cell 3): GVA per head = total GVA in million euro * 1,000,000 / population.
# Only region-years with both a GVA and a population value are kept (inner join).
gva_total = tables["gva"][tables["gva"]["sector"] == "TOTAL"][["geo", "year", "gva_meur"]]
if "pop" in tables:
    gva_pc = gva_total.merge(tables["pop"][["geo", "year", "pop"]], on=["geo", "year"], how="inner")
    gva_pc["gva_pc"] = gva_pc["gva_meur"] * 1_000_000 / gva_pc["pop"]
    tables["gva_pc"] = gva_pc[["geo", "year", "gva_pc"]]
    print(f"gva_pc: {len(gva_total) - len(gva_pc)} GVA region-years have no population value and are not in gva_pc")

# FROM RETHABILE (his cell 5): six broad sectors that add up to the total, shares in percent of the total.
# Only region-years where all six sectors have a value are kept, so the shares add up to about 100.
SIX_SECTORS = ["A", "B-E", "F", "G-J", "K-N", "O-U"]
six = tables["gva"][tables["gva"]["sector"].isin(SIX_SECTORS)]
complete = six.groupby(["geo", "year"])["sector"].nunique()
complete = complete[complete == len(SIX_SECTORS)].reset_index()[["geo", "year"]]
shares = six.merge(complete, on=["geo", "year"]).merge(
    gva_total.rename(columns={"gva_meur": "gva_total_meur"}), on=["geo", "year"])
shares["share_pct"] = shares["gva_meur"] / shares["gva_total_meur"] * 100
sum_check = shares.groupby(["geo", "year"])["share_pct"].sum()
assert sum_check.between(99, 101).all(), "sector shares do not add up to about 100%"
tables["gva_sector"] = shares[["geo", "year", "sector", "gva_meur", "gva_total_meur", "share_pct"]] \
    .sort_values(["geo", "year", "sector"]).reset_index(drop=True)

os.makedirs(OUT_DIR, exist_ok=True)
for name, t in tables.items():
    t.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name:6} {len(t):>8,} rows | {t['geo'].nunique():>3} regions | "
          f"years {t['year'].min()}-{t['year'].max()}")

# CHANGE 8: record of the region-code decisions, and a coverage table for the whole team
pd.DataFrame([{"old_code": o, "new_code": n, "type": k} for o, (n, k) in RENAMES.items()]).to_csv(
    os.path.join(OUT_DIR, "region_code_renames.csv"), index=False)

n_years = LAST_YEAR - FIRST_YEAR + 1
rows = []
for name, t in tables.items():
    per_region = t.groupby("geo")["year"].agg(["min", "max", "nunique"]) if name != "gva" else \
        t[t["sector"] == "TOTAL"].groupby("geo")["year"].agg(["min", "max", "nunique"])
    rows.append({"table": name, "regions": len(per_region),
                 "with_all_years": int((per_region["nunique"] == n_years).sum()),
                 f"with_{FIRST_YEAR}_and_{LAST_YEAR}": int(((per_region["min"] == FIRST_YEAR) & (per_region["max"] == LAST_YEAR)).sum())})
coverage = pd.DataFrame(rows)
coverage.to_csv(os.path.join(OUT_DIR, "coverage.csv"), index=False)
print()
print(coverage.to_string(index=False))