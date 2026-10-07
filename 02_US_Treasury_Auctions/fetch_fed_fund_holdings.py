from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"data"; OUT.mkdir(exist_ok=True)
BASE="https://fred.stlouisfed.org/graph/fredgraph.csv?id="

series={
 "mutual_funds_treasury":"BOGZ1FL653061105Q",
 "hf_domestic_treasury_net":"BOGZ1FL623061103Q",
 "hf_foreign_treasury_net":"BOGZ1FL623061163Q",
 "hf_domestic_government_long":"BOGZ1FL623061003Q",
 "hf_foreign_government_long":"BOGZ1FL623061063Q",
}
frames=[]
for name,sid in series.items():
    x=pd.read_csv(BASE+sid)
    x.columns=["date",name]
    x["date"]=pd.to_datetime(x["date"])
    x[name]=pd.to_numeric(x[name],errors="coerce")
    frames.append(x)
df=frames[0]
for x in frames[1:]: df=df.merge(x,on="date",how="outer")
df=df[(df.date>="2016-01-01") & (df.date<="2026-12-31")].sort_values("date")
df.to_csv(OUT/"fed_fund_treasury_holdings_quarterly.csv",index=False)

# Year-end observations; 2026 uses latest available quarter and is flagged.
df["year"]=df.date.dt.year
annual=df.groupby("year",as_index=False).tail(1).copy()
annual["period_type"]=annual["date"].dt.quarter.map(lambda q:"year_end" if q==4 else "latest_ytd")
annual.to_csv(OUT/"fed_fund_treasury_holdings_annual.csv",index=False)
print(annual.to_string(index=False))
