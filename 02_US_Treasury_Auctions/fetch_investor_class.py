"""Fetch Treasury Investor Class Auction Allotments and extract 30-Year nominal bonds.

Official source:
https://home.treasury.gov/data/investor-class-auction-allotments

This first-pass extractor downloads Treasury's current coupon-auction XLS,
discovers the header row, normalizes the table, and saves both the cleaned
30-year subset and a raw preview for auditability.
"""
from pathlib import Path
import re, io
import requests
import pandas as pd
from bs4 import BeautifulSoup

PAGE="https://home.treasury.gov/data/investor-class-auction-allotments"
BASE="https://home.treasury.gov"

def norm(x):
    return re.sub(r"[^a-z0-9]+","_",str(x).strip().lower()).strip("_")

def main():
    html=requests.get(PAGE,timeout=60).text
    soup=BeautifulSoup(html,"html.parser")
    links=[a.get("href","") for a in soup.find_all("a")]
    candidates=[x for x in links if "IC_Coupons" in x and x.lower().endswith(".xls")]
    if not candidates:
        raise RuntimeError("Could not find current Treasury coupon investor-class XLS link")
    href=candidates[0]
    url=href if href.startswith("http") else BASE+href
    print("Investor-class source:",url)
    data=requests.get(url,timeout=60)
    data.raise_for_status()

    raw=pd.read_excel(io.BytesIO(data.content),header=None)
    outdir=Path(__file__).resolve().parent/"data"
    outdir.mkdir(exist_ok=True)
    raw.head(25).to_csv(outdir/"investor_class_raw_preview.csv",index=False,header=False)

    header=None
    for i,row in raw.head(30).iterrows():
        vals=[str(v).lower() for v in row.tolist()]
        if any("cusip" in v for v in vals) and any("issue" in v and "date" in v for v in vals):
            header=i; break
    if header is None:
        raise RuntimeError("Header row not found; inspect investor_class_raw_preview.csv")

    df=pd.read_excel(io.BytesIO(data.content),header=header)
    df.columns=[norm(c) for c in df.columns]
    print("Columns:",list(df.columns))
    df.to_csv(outdir/"investor_class_coupon_allotments.csv",index=False)

    # Match nominal 30-year auctions by CUSIP against our already-clean Phase 1 file.
    auctions=pd.read_csv(outdir/"treasury_30y_auctions_2016_present.csv",dtype={"cusip":str})
    if "cusip" not in df.columns:
        raise RuntimeError("CUSIP column not found after normalization")
    df["cusip"]=df["cusip"].astype(str).str.strip()
    keep=set(auctions["cusip"].astype(str))
    subset=df[df["cusip"].isin(keep)].copy()
    subset.to_csv(outdir/"investor_class_30y_nominal.csv",index=False)
    print(f"Matched {len(subset)} investor-class rows to nominal 30Y CUSIPs")

if __name__=="__main__":
    main()
