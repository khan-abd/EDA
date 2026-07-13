"""
COVID-19 Layoffs — Data Cleaning (Python / Pandas)
====================================================
Mirrors the SQL cleaning steps from DATA CLEANING/Data Cleaning.sql
Input : DATA CLEANING/layoffs.csv  (raw, 2361 rows)
Output: powerbi_exports/cleaned_for_powerbi.csv  (cleaned)
"""

import pandas as pd
import numpy as np
import os

RAW_PATH   = os.path.join(os.path.dirname(__file__), "DATA CLEANING", "layoffs.csv")
OUT_DIR    = os.path.join(os.path.dirname(__file__), "powerbi_exports")
CLEAN_PATH = os.path.join(OUT_DIR, "cleaned_for_powerbi.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ── 0. Load raw data ────────────────────────────────────────────────────────
df = pd.read_csv(RAW_PATH)
print("=" * 60)
print("BEFORE CLEANING")
print("=" * 60)
print(f"  Rows            : {len(df):,}")
print(f"  Columns         : {list(df.columns)}")
print(f"\n  Null counts:")
print(df.isnull().sum().to_string(header=False))
print(f"\n  Duplicate rows  : {df.duplicated().sum():,}")
print(f"  Date dtype      : {df['date'].dtype}")

# ── 1. Remove duplicates ────────────────────────────────────────────────────
before = len(df)
df = df.drop_duplicates(
    subset=["company","location","industry","total_laid_off",
            "percentage_laid_off","date","stage","country","funds_raised_millions"]
)
print(f"\n[Step 1] Removed {before - len(df)} duplicate rows → {len(df):,} remaining")

# ── 2. Standardise text fields ───────────────────────────────────────────────
df["company"] = df["company"].str.strip()
df["country"]  = df["country"].str.strip().str.rstrip(".")   # "United States." → "United States"
crypto_mask = df["industry"].str.startswith("Crypto", na=False)
df.loc[crypto_mask, "industry"] = "Crypto"
print(f"[Step 2] Standardised whitespace + merged {crypto_mask.sum()} Crypto variants")

# ── 3. Convert date string to datetime ──────────────────────────────────────
df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="coerce")
print(f"[Step 3] Parsed date → {df['date'].dtype}  |  NaT: {df['date'].isna().sum()}")

# ── 4. Convert numeric columns ───────────────────────────────────────────────
for col in ["total_laid_off","percentage_laid_off","funds_raised_millions"]:
    df[col] = df[col].replace("NULL", np.nan)
    df[col] = pd.to_numeric(df[col], errors="coerce")
print(f"[Step 4] Converted numeric columns to float")

# ── 5. Populate missing industry via same-company forward-fill ───────────────
df["industry"] = df["industry"].replace("", np.nan)
industry_map = df.dropna(subset=["industry"]).groupby("company")["industry"].first()
mask = df["industry"].isna()
df.loc[mask, "industry"] = df.loc[mask, "company"].map(industry_map)
filled = mask.sum() - df["industry"].isna().sum()
print(f"[Step 5] Forward-filled {filled} missing industry values")

# ── 6. Drop rows with no layoff numbers ─────────────────────────────────────
before = len(df)
df = df.dropna(subset=["total_laid_off","percentage_laid_off"], how="all")
print(f"[Step 6] Dropped {before - len(df)} rows with no layoff data → {len(df):,} remaining")

# ── 7. Add time helper columns ───────────────────────────────────────────────
df["year"]       = df["date"].dt.year.astype("Int64")
df["month"]      = df["date"].dt.month.astype("Int64")
df["year_month"] = df["date"].dt.to_period("M").astype(str)

# ── Final quality report ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AFTER CLEANING")
print("=" * 60)
print(f"  Rows            : {len(df):,}")
print(f"  Date range      : {df['date'].min().date()} → {df['date'].max().date()}")
print(f"  Industries      : {df['industry'].nunique()}")
print(f"  Countries       : {df['country'].nunique()}")
print(f"  Companies       : {df['company'].nunique()}")
nulls = df.isnull().sum()
nulls = nulls[nulls > 0]
if len(nulls):
    print(f"\n  Remaining nulls:\n{nulls.to_string(header=False)}")
else:
    print("\n  Remaining nulls: None in key columns")

df.to_csv(CLEAN_PATH, index=False)
print(f"\n✅ Saved → {CLEAN_PATH}")

# Return df for use by eda_analysis.py
if __name__ == "__main__":
    print("\nRun eda_analysis.py to generate insights and Power BI exports.")
