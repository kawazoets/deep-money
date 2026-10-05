"""Download and prepare nominal U.S. Treasury 30-Year Bond auction data.

Source: U.S. Treasury Fiscal Data API (Auctions Query).
Period: 2016-01-01 through the run date.
Excludes inflation-indexed securities (TIPS).
Output: data/treasury_30y_auctions_2016_present.csv
"""

from pathlib import Path
from datetime import date
import requests
import pandas as pd

API = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
START_DATE = "2016-01-01"
END_DATE = date.today().isoformat()

FIELDS = [
    "cusip", "auction_date", "issue_date", "maturity_date",
    "security_type", "security_term", "original_security_term",
    "inflation_index_security", "reopening", "offering_amt",
    "high_yield", "bid_to_cover_ratio", "total_tendered",
    "total_accepted", "comp_accepted",
    "primary_dealer_accepted", "direct_bidder_accepted",
    "indirect_bidder_accepted",
]

def fetch_auctions():
    params = {
        "fields": ",".join(FIELDS),
        "filter": (
            "security_type:eq:Bond,"
            "original_security_term:eq:30-Year,"
            "inflation_index_security:eq:No,"
            f"auction_date:gte:{START_DATE},"
            f"auction_date:lte:{END_DATE}"
        ),
        "sort": "auction_date",
        "page[size]": 500,
        "format": "json",
    }
    response = requests.get(API, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    rows = payload["data"]
    total = int(payload.get("meta", {}).get("total-count", len(rows)))
    if total > len(rows):
        raise RuntimeError(f"API returned {len(rows)} of {total} rows; add pagination.")
    return rows

def prepare(rows):
    df = pd.DataFrame(rows)
    numeric = [
        "offering_amt", "high_yield", "bid_to_cover_ratio",
        "total_tendered", "total_accepted", "comp_accepted",
        "primary_dealer_accepted", "direct_bidder_accepted",
        "indirect_bidder_accepted",
    ]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["auction_date"] = pd.to_datetime(df["auction_date"])

    # Primary / Direct / Indirect categories partition competitive awards,
    # so use competitive accepted amount as the denominator.
    comp = df["comp_accepted"].replace(0, pd.NA)
    df["primary_dealer_pct"] = 100 * df["primary_dealer_accepted"] / comp
    df["direct_bidder_pct"] = 100 * df["direct_bidder_accepted"] / comp
    df["indirect_bidder_pct"] = 100 * df["indirect_bidder_accepted"] / comp
    df["bidder_pct_sum"] = (
        df["primary_dealer_pct"] + df["direct_bidder_pct"] + df["indirect_bidder_pct"]
    )

    df["year"] = df["auction_date"].dt.year
    return df.sort_values("auction_date").reset_index(drop=True)

def main():
    df = prepare(fetch_auctions())

    # Integrity checks: Phase 1 must contain nominal 30-Year Bonds only.
    assert (df["inflation_index_security"] == "No").all(), "TIPS contamination detected"
    assert df["bidder_pct_sum"].between(99.99, 100.01).all(), "Bidder shares do not sum to 100%"

    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "treasury_30y_auctions_2016_present.csv"
    df.to_csv(out, index=False)

    print(f"Saved {len(df)} nominal 30-Year Bond auctions to {out}")
    print(df[[
        "auction_date", "high_yield", "bid_to_cover_ratio",
        "primary_dealer_pct", "direct_bidder_pct", "indirect_bidder_pct"
    ]].tail(12).to_string(index=False))

if __name__ == "__main__":
    main()
