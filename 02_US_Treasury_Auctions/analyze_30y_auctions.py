"""Initial exploratory analysis for 30-Year Treasury auctions."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "treasury_30y_auctions_2016_present.csv"
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["auction_date"])

cols = [
    "high_yield", "bid_to_cover_ratio",
    "primary_dealer_pct", "direct_bidder_pct", "indirect_bidder_pct",
]

print("\nCorrelation matrix")
print(df[cols].corr().round(3))

annual = (
    df.assign(year=df["auction_date"].dt.year)
      .groupby("year")[cols]
      .mean()
      .round(3)
)
annual.to_csv(OUT / "annual_averages.csv")
print("\nAnnual averages")
print(annual)

for col, ylabel in [
    ("high_yield", "High Yield (%)"),
    ("bid_to_cover_ratio", "Bid-to-Cover Ratio"),
    ("primary_dealer_pct", "Primary Dealer Share (%)"),
    ("direct_bidder_pct", "Direct Bidder Share (%)"),
    ("indirect_bidder_pct", "Indirect Bidder Share (%)"),
]:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["auction_date"], df[col])
    ax.set_title(f"30-Year Treasury Auction: {ylabel}")
    ax.set_xlabel("Auction Date")
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(OUT / f"{col}.png", dpi=160)
    plt.close(fig)

# Core scatter plots: does buyer composition change as the funding price rises?
for col in ["primary_dealer_pct", "direct_bidder_pct", "indirect_bidder_pct", "bid_to_cover_ratio"]:
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(df["high_yield"], df[col], alpha=0.7)
    ax.set_xlabel("High Yield (%)")
    ax.set_ylabel(col.replace("_", " ").title())
    ax.set_title(f"30-Year Treasury: High Yield vs {col.replace('_', ' ').title()}")
    fig.tight_layout()
    fig.savefig(OUT / f"yield_vs_{col}.png", dpi=160)
    plt.close(fig)
