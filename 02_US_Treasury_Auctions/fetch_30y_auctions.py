"""Download and prepare U.S. Treasury 30-Year Bond auction data.

Source: U.S. Treasury Fiscal Data API (Auctions Query).
Period: 2016-01-01 through the run date.
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
    "cusip",
    "auction_date",
    "issue_date",
    "maturity_date",
    "security_type",
    "security_term",
    "reopening",
    "offering_amt",
    "high_yield",
    "bid_to_cover_ratio",
    "total_tendered",
    "total_accepted",
    "primary_dealer_accepted",
    "direct_bidder_accepted",
    "indirect_bidder_accepted",
]

def fetch_auctions():
    params = {
        "fields": ",".join(FIELDS),
        "filter": (
            f"security_type:eq:Bond,"
            f"security_term:eq:30-Year,"
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
        "total_tendered", "total_accepted",
        "primary_dealer_accepted", "direct_bidder_accepted",
        "indirect_bidder_accepted",
    ]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["auction_date"] = pd.to_datetime(df["auction_date"])
    accepted = df["total_accepted"].replace(0, pd.NA)
    df["primary_dealer_pct"] = 100 * df["primary_dealer_accepted"] / accepted
    df["direct_bidder_pct"] = 100 * df["direct_bidder_accepted"] / accepted
    df["indirect_bidder_pct"] = 100 * df["indirect_bidder_accepted"] / accepted

    df["year"] = df["auction_date"].dt.year
    df = df.sort_values("auction_date").reset_index(drop=True)
    return df

def main():
    rows = fetch_auctions()
    df = prepare(rows)

    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "treasury_30y_auctions_2016_present.csv"
    df.to_csv(out, index=False)

    print(f"Saved {len(df)} auctions to {out}")
    print(df[[
        "auction_date", "high_yield", "bid_to_cover_ratio",
        "primary_dealer_pct", "direct_bidder_pct", "indirect_bidder_pct"
    ]].tail(12).to_string(index=False))

if __name__ == "__main__":
    main()
