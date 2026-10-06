from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

cftc = pd.read_csv(DATA / "cftc_long_bond_tff_annual.csv")
ic = pd.read_csv(DATA / "investor_class_30y_nominal.csv")

ic["issue_date"] = pd.to_datetime(ic["issue_date"], errors="coerce")
for c in ["total_issue", "investment_funds", "soma_federal_reserve_banks"]:
    ic[c] = pd.to_numeric(ic[c], errors="coerce")

# Keep the same total-issue denominator used in the existing interim comparison.
# Also calculate a market-only share excluding SOMA, because this is the cleaner
# measure of competitive/private absorption.
ic["year"] = ic["issue_date"].dt.year
ic["market_issue"] = ic["total_issue"] - ic["soma_federal_reserve_banks"]

annual_ic = (
    ic.groupby("year", as_index=False)
      .agg(
          auctions=("issue_date", "count"),
          total_issue=("total_issue", "sum"),
          soma=("soma_federal_reserve_banks", "sum"),
          investment_funds=("investment_funds", "sum"),
          market_issue=("market_issue", "sum"),
      )
)
annual_ic["investment_funds_pct_total_issue"] = (
    100 * annual_ic["investment_funds"] / annual_ic["total_issue"]
)
annual_ic["investment_funds_pct_ex_soma"] = (
    100 * annual_ic["investment_funds"] / annual_ic["market_issue"]
)

wide = cftc.pivot(
    index="year",
    columns="market",
    values=["asset_mgr_net_pct_oi_avg", "leveraged_funds_net_pct_oi_avg"],
)
wide.columns = [
    f"{metric}_{market.lower().replace(' ', '_')}"
    for metric, market in wide.columns
]
wide = wide.reset_index()

merged = annual_ic.merge(wide, on="year", how="left")
merged.to_csv(OUT / "auction_investment_funds_vs_cftc_annual.csv", index=False)

corr_rows = []
for c in merged.columns:
    if c.startswith(("asset_mgr_net_pct_oi_avg_", "leveraged_funds_net_pct_oi_avg_")):
        valid = merged[["investment_funds_pct_ex_soma", c]].dropna()
        corr_rows.append({
            "cftc_series": c,
            "n_years": len(valid),
            "corr_with_investment_funds_pct_ex_soma": valid["investment_funds_pct_ex_soma"].corr(valid[c]),
        })
pd.DataFrame(corr_rows).to_csv(OUT / "auction_vs_cftc_correlations.csv", index=False)

print("\nAnnual overlay:")
print(merged.to_string(index=False))
print("\nDescriptive annual correlations (NOT causal tests):")
print(pd.DataFrame(corr_rows).to_string(index=False))
print("\nCaution: Auction Investor Class and CFTC TFF are different classification systems.")
print("CFTC UST BOND and ULTRA UST BOND are kept separate; their contracts are not simply added.")
