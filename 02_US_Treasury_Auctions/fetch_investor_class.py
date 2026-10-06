"""Fetch Treasury Investor Class Auction Allotments and extract 30-Year nominal bonds.

Official source:
https://home.treasury.gov/data/investor-class-auction-allotments

Treasury's current coupon-auction workbook is linked from that page. The
Treasury site does not expose that XLS link reliably to requests/BeautifulSoup,
so use the verified official workbook URL directly.
"""
from pathlib import Path
import io
import re
import requests
import pandas as pd

XLS_URL = "https://home.treasury.gov/system/files/276/August_7_2026_IC_Coupons.xls"

def norm(x):
    return re.sub(r"[^a-z0-9]+", "_", str(x).strip().lower()).strip("_")

def main():
    headers = {"User-Agent": "Mozilla/5.0 Treasury-research/1.0"}
    r = requests.get(XLS_URL, headers=headers, timeout=60)
    r.raise_for_status()
    print("Investor-class source:", XLS_URL, "bytes:", len(r.content))

    raw = pd.read_excel(io.BytesIO(r.content), header=None)
    outdir = Path(__file__).resolve().parent / "data"
    outdir.mkdir(exist_ok=True)
    raw.head(30).to_csv(outdir / "investor_class_raw_preview.csv", index=False, header=False)

    header = None
    for i, row in raw.head(40).iterrows():
        vals = [str(v).lower() for v in row.tolist()]
        if any("cusip" in v for v in vals) and any("issue" in v and "date" in v for v in vals):
            header = i
            break
    if header is None:
        raise RuntimeError("Header row not found; inspect investor_class_raw_preview.csv")

    df = pd.read_excel(io.BytesIO(r.content), header=header)
    df.columns = [norm(c) for c in df.columns]
    print("Columns:", list(df.columns))
    df.to_csv(outdir / "investor_class_coupon_allotments.csv", index=False)

    auctions = pd.read_csv(
        outdir / "treasury_30y_auctions_2016_present.csv", dtype={"cusip": str}
    )
    if "cusip" not in df.columns:
        raise RuntimeError("CUSIP column not found after normalization")

    # Reopenings reuse the original security's CUSIP, so CUSIP alone is not
    # an auction-event key. Treasury's Investor Class table is ordered by
    # issue date and includes issue_date; match on CUSIP + issue_date.
    if "issue_date" not in df.columns:
        raise RuntimeError("Issue-date column not found after normalization")

    df["cusip"] = df["cusip"].astype(str).str.strip()
    auctions["cusip"] = auctions["cusip"].astype(str).str.strip()
    df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce").dt.normalize()
    auctions["issue_date"] = pd.to_datetime(
        auctions["issue_date"], errors="coerce"
    ).dt.normalize()

    keys = auctions[["cusip", "issue_date"]].drop_duplicates()
    subset = df.merge(keys, on=["cusip", "issue_date"], how="inner", validate="one_to_one")
    subset = subset.sort_values("issue_date").copy()
    subset.to_csv(outdir / "investor_class_30y_nominal.csv", index=False)

    if subset.empty:
        raise RuntimeError("No nominal 30Y auction events matched investor-class workbook")

    expected = auctions[
        auctions["issue_date"].between(df["issue_date"].min(), df["issue_date"].max())
    ][["cusip", "issue_date"]].drop_duplicates()
    if len(subset) != len(expected):
        missing = expected.merge(
            subset[["cusip", "issue_date"]],
            on=["cusip", "issue_date"],
            how="left",
            indicator=True,
        )
        missing = missing[missing["_merge"] == "left_only"]
        raise RuntimeError(
            f"Investor-class event match incomplete: matched {len(subset)} of "
            f"{len(expected)} expected rows. Missing:\n{missing.to_string(index=False)}"
        )

    print(
        f"Matched {len(subset)} investor-class rows to nominal 30Y auction events "
        f"by CUSIP + issue_date"
    )

if __name__ == "__main__":
    main()
