from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

START_YEAR = 2016
END_YEAR = 2026
BASE = "https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip"
OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(parents=True, exist_ok=True)

# CFTC Traders in Financial Futures codes
MARKETS = {
    "020601": "UST BOND",
    "020604": "ULTRA UST BOND",
}

frames = []
headers = {"User-Agent": "Mozilla/5.0 deep-money-research/1.0"}

for year in range(START_YEAR, END_YEAR + 1):
    url = BASE.format(year=year)
    r = requests.get(url, headers=headers, timeout=90)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        names = [n for n in z.namelist() if n.lower().endswith((".txt", ".csv"))]
        if not names:
            raise RuntimeError(f"No text/CSV file in {url}")
        with z.open(names[0]) as f:
            df = pd.read_csv(f, low_memory=False)
    frames.append(df)

raw = pd.concat(frames, ignore_index=True)
raw.columns = [str(c).strip() for c in raw.columns]

required = [
    "Market_and_Exchange_Names",
    "Report_Date_as_MM_DD_YYYY",
    "CFTC_Contract_Market_Code",
    "Open_Interest_All",
    "Asset_Mgr_Positions_Long_All",
    "Asset_Mgr_Positions_Short_All",
    "Lev_Money_Positions_Long_All",
    "Lev_Money_Positions_Short_All",
]
missing = [c for c in required if c not in raw.columns]
if missing:
    raise RuntimeError(f"Missing CFTC columns: {missing}")

codes = raw["CFTC_Contract_Market_Code"].astype(str).str.strip().str.replace('"', "", regex=False)
# Preserve leading zero if pandas inferred integer-like text.
codes = codes.str.replace(r"\.0$", "", regex=True).str.zfill(6)
raw["contract_code"] = codes

df = raw[raw["contract_code"].isin(MARKETS)].copy()
df["market"] = df["contract_code"].map(MARKETS)
df["report_date"] = pd.to_datetime(df["Report_Date_as_MM_DD_YYYY"], errors="coerce")

numcols = [
    "Open_Interest_All",
    "Asset_Mgr_Positions_Long_All",
    "Asset_Mgr_Positions_Short_All",
    "Lev_Money_Positions_Long_All",
    "Lev_Money_Positions_Short_All",
]
for c in numcols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=["report_date", *numcols]).copy()
df["asset_mgr_net"] = df["Asset_Mgr_Positions_Long_All"] - df["Asset_Mgr_Positions_Short_All"]
df["leveraged_funds_net"] = df["Lev_Money_Positions_Long_All"] - df["Lev_Money_Positions_Short_All"]
df["asset_mgr_net_pct_oi"] = 100 * df["asset_mgr_net"] / df["Open_Interest_All"]
df["leveraged_funds_net_pct_oi"] = 100 * df["leveraged_funds_net"] / df["Open_Interest_All"]

outcols = [
    "report_date", "market", "contract_code", "Open_Interest_All",
    "Asset_Mgr_Positions_Long_All", "Asset_Mgr_Positions_Short_All", "asset_mgr_net",
    "Lev_Money_Positions_Long_All", "Lev_Money_Positions_Short_All", "leveraged_funds_net",
    "asset_mgr_net_pct_oi", "leveraged_funds_net_pct_oi",
]
df[outcols].sort_values(["market", "report_date"]).to_csv(
    OUT / "cftc_long_bond_tff_2016_2026.csv", index=False
)

annual = (
    df.assign(year=df["report_date"].dt.year)
      .groupby(["year", "market"], as_index=False)
      .agg(
          weeks=("report_date", "count"),
          asset_mgr_net_avg=("asset_mgr_net", "mean"),
          leveraged_funds_net_avg=("leveraged_funds_net", "mean"),
          asset_mgr_net_pct_oi_avg=("asset_mgr_net_pct_oi", "mean"),
          leveraged_funds_net_pct_oi_avg=("leveraged_funds_net_pct_oi", "mean"),
      )
)
annual.to_csv(OUT / "cftc_long_bond_tff_annual.csv", index=False)

print(f"Saved {len(df):,} weekly CFTC observations")
print(annual.to_string(index=False))
