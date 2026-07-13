"""
COVID-19 Layoffs — EDA & Power BI Export
==========================================
Runs after data_cleaning.py.
Produces:
  charts/           → PNG charts for README
  powerbi_exports/  → Aggregated CSVs for Power BI dashboard
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os, sys

# ── Paths ────────────────────────────────────────────────────────────────────
BASE       = os.path.dirname(__file__)
CLEAN_PATH = os.path.join(BASE, "powerbi_exports", "cleaned_for_powerbi.csv")
CHARTS_DIR = os.path.join(BASE, "charts")
PB_DIR     = os.path.join(BASE, "powerbi_exports")
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(PB_DIR, exist_ok=True)

# Run cleaning if needed
if not os.path.exists(CLEAN_PATH):
    print("Running data_cleaning.py first...")
    import runpy
    runpy.run_path(os.path.join(BASE, "data_cleaning.py"))

df = pd.read_csv(CLEAN_PATH, parse_dates=["date"])
print(f"Loaded cleaned data: {len(df):,} rows\n")

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE = ["#1a1a2e","#16213e","#0f3460","#533483","#e94560","#f5a623","#7bed9f","#70a1ff","#ff6b81","#2ed573"]
sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({"font.family":"sans-serif","figure.dpi":150})

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ROLLING MONTHLY LAYOFFS  (for line chart in Power BI)
# ═══════════════════════════════════════════════════════════════════════════════
monthly = (
    df.groupby("year_month")["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"year_month":"Month","total_laid_off":"Monthly_Layoffs"})
    .sort_values("Month")
)
monthly["Rolling_Total"] = monthly["Monthly_Layoffs"].cumsum()
monthly.to_csv(os.path.join(PB_DIR,"monthly_layoffs.csv"), index=False)

# Chart
fig, ax = plt.subplots(figsize=(12,4))
ax.fill_between(range(len(monthly)), monthly["Monthly_Layoffs"], alpha=0.3, color="#e94560")
ax.plot(range(len(monthly)), monthly["Monthly_Layoffs"], color="#e94560", linewidth=2)
ax.set_xticks(range(0, len(monthly), 3))
ax.set_xticklabels(monthly["Month"].iloc[::3], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
ax.set_title("Monthly Layoffs (Mar 2020 – Mar 2023)", fontsize=13, fontweight="bold")
ax.set_ylabel("Employees Laid Off")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR,"01_monthly_trend.png"))
plt.close()
print("✅ Chart 1: Monthly trend")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. LAYOFFS BY INDUSTRY
# ═══════════════════════════════════════════════════════════════════════════════
industry = (
    df.groupby("industry")["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"industry":"Industry","total_laid_off":"Total_Laid_Off"})
    .sort_values("Total_Laid_Off", ascending=False)
    .dropna()
)
industry.to_csv(os.path.join(PB_DIR,"industry_layoffs.csv"), index=False)

fig, ax = plt.subplots(figsize=(10,6))
bars = ax.barh(industry["Industry"], industry["Total_Laid_Off"], color=PALETTE[:len(industry)])
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x/1000)}K"))
ax.set_title("Total Layoffs by Industry", fontsize=13, fontweight="bold")
ax.set_xlabel("Employees Laid Off")
for bar, val in zip(bars, industry["Total_Laid_Off"]):
    ax.text(bar.get_width()+500, bar.get_y()+bar.get_height()/2,
            f"{int(val):,}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR,"02_industry_layoffs.png"))
plt.close()
print("✅ Chart 2: Industry breakdown")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. TOP 15 COUNTRIES
# ═══════════════════════════════════════════════════════════════════════════════
country = (
    df.groupby("country")["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"country":"Country","total_laid_off":"Total_Laid_Off"})
    .sort_values("Total_Laid_Off", ascending=False)
    .head(15)
)
country.to_csv(os.path.join(PB_DIR,"country_layoffs.csv"), index=False)

fig, ax = plt.subplots(figsize=(10,5))
ax.bar(country["Country"], country["Total_Laid_Off"], color="#0f3460")
ax.set_xticklabels(country["Country"], rotation=40, ha="right", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x/1000)}K"))
ax.set_title("Top 15 Countries by Total Layoffs", fontsize=13, fontweight="bold")
ax.set_ylabel("Employees Laid Off")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR,"03_country_layoffs.png"))
plt.close()
print("✅ Chart 3: Country breakdown")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. LAYOFFS BY COMPANY STAGE
# ═══════════════════════════════════════════════════════════════════════════════
stage = (
    df.groupby("stage")["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"stage":"Stage","total_laid_off":"Total_Laid_Off"})
    .sort_values("Total_Laid_Off", ascending=False)
    .dropna()
)
stage.to_csv(os.path.join(PB_DIR,"stage_layoffs.csv"), index=False)

fig, ax = plt.subplots(figsize=(9,5))
wedges, texts, autotexts = ax.pie(
    stage["Total_Laid_Off"], labels=stage["Stage"],
    autopct="%1.1f%%", colors=PALETTE[:len(stage)],
    pctdistance=0.8, startangle=140
)
for t in autotexts: t.set_fontsize(8)
ax.set_title("Layoffs by Company Stage", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR,"04_stage_layoffs.png"))
plt.close()
print("✅ Chart 4: Company stage")

# ═══════════════════════════════════════════════════════════════════════════════
# 5. TOP 10 COMPANIES ALL-TIME
# ═══════════════════════════════════════════════════════════════════════════════
top_companies = (
    df.groupby(["company","industry"])["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"company":"Company","industry":"Industry","total_laid_off":"Total_Laid_Off"})
    .sort_values("Total_Laid_Off", ascending=False)
    .head(10)
)
top_companies.to_csv(os.path.join(PB_DIR,"top_companies.csv"), index=False)

fig, ax = plt.subplots(figsize=(10,5))
colors = [PALETTE[i % len(PALETTE)] for i in range(len(top_companies))]
ax.barh(top_companies["Company"], top_companies["Total_Laid_Off"], color=colors)
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x/1000)}K"))
ax.set_title("Top 10 Companies by Total Layoffs", fontsize=13, fontweight="bold")
ax.set_xlabel("Employees Laid Off")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS_DIR,"05_top_companies.png"))
plt.close()
print("✅ Chart 5: Top companies")

# ═══════════════════════════════════════════════════════════════════════════════
# 6. TOP 5 COMPANIES PER YEAR (for Power BI ranking visual)
# ═══════════════════════════════════════════════════════════════════════════════
company_year = (
    df.groupby(["company","year"])["total_laid_off"]
    .sum()
    .reset_index()
    .rename(columns={"company":"Company","year":"Year","total_laid_off":"Total_Laid_Off"})
    .dropna()
)
company_year["Rank"] = company_year.groupby("Year")["Total_Laid_Off"].rank(ascending=False, method="dense").astype(int)
top5_year = company_year[company_year["Rank"] <= 5].sort_values(["Year","Rank"])
top5_year.to_csv(os.path.join(PB_DIR,"top_companies_by_year.csv"), index=False)
print("✅ Export: Top 5 companies per year")

# ═══════════════════════════════════════════════════════════════════════════════
# 7. YEARLY SUMMARY (KPI cards in Power BI)
# ═══════════════════════════════════════════════════════════════════════════════
yearly = (
    df.groupby("year").agg(
        Total_Laid_Off=("total_laid_off","sum"),
        Total_Events=("company","count"),
        Unique_Companies=("company","nunique"),
        Avg_Pct_Laid_Off=("percentage_laid_off","mean")
    ).reset_index()
    .rename(columns={"year":"Year"})
    .dropna(subset=["Year"])
)
yearly["Avg_Pct_Laid_Off"] = yearly["Avg_Pct_Laid_Off"].round(3)
yearly.to_csv(os.path.join(PB_DIR,"yearly_summary.csv"), index=False)
print("✅ Export: Yearly summary (KPI)")

# ═══════════════════════════════════════════════════════════════════════════════
# Summary print
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("EDA COMPLETE — KEY INSIGHTS")
print("=" * 60)
total = int(df["total_laid_off"].sum())
peak_month = monthly.loc[monthly["Monthly_Layoffs"].idxmax(), "Month"]
top_industry = industry.iloc[0]["Industry"]
top_country  = country.iloc[0]["Country"]
top_company  = top_companies.iloc[0]["Company"]
print(f"  Total employees laid off : {total:,}")
print(f"  Peak month               : {peak_month}")
print(f"  Hardest hit industry     : {top_industry}")
print(f"  Hardest hit country      : {top_country}")
print(f"  Company with most layoffs: {top_company}")
print(f"\n  Power BI CSVs → powerbi_exports/")
print(f"  Charts        → charts/")
print(f"\n✅ All done. Import CSVs into Power BI to build the dashboard.")
